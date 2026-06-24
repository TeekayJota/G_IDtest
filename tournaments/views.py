from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import RegistrationForm, TournamentForm
from .models import Member, Registration, StaffNote, Tournament
from .utils import generate_code, notify_status_change


# =====================================================================
#  Helpers
# =====================================================================
def admin_required(view_func):
    """Solo usuarios con rol ADMIN. Staff queda fuera (no puede crear torneos)."""

    @wraps(view_func)
    @login_required
    def _wrapped(request, *args, **kwargs):
        if not getattr(request.user, "is_admin_role", False):
            messages.error(request, "Solo un administrador puede crear o editar torneos.")
            return redirect("staff_inbox")
        return view_func(request, *args, **kwargs)

    return _wrapped


def _default_tournament():
    return (
        Tournament.objects.filter(featured=True).first()
        or Tournament.objects.first()
    )


# =====================================================================
#  Público
# =====================================================================
def landing(request):
    tournaments = list(Tournament.objects.all())
    context = {
        "tournaments": tournaments[:4],
        "featured": _default_tournament(),
    }
    return render(request, "public/landing.html", context)


def tournament_list(request):
    f = request.GET.get("f", "todos")
    tournaments = Tournament.objects.all()
    if f == "abiertos":
        tournaments = tournaments.filter(status=Tournament.Status.OPEN)
    elif f == "proximos":
        tournaments = tournaments.filter(status=Tournament.Status.SOON)
    context = {"tournaments": tournaments, "filter": f}
    return render(request, "public/tournaments.html", context)


def tournament_detail(request, slug):
    t = get_object_or_404(Tournament, slug=slug)
    regs = t.registrations.all()
    context = {
        "t": t,
        "confirmed": regs.filter(status=Registration.Status.APPROVED),
        "review": regs.filter(status=Registration.Status.REVIEW),
        "pending": regs.filter(status=Registration.Status.PENDING),
    }
    return render(request, "public/detail.html", context)


def register(request, slug=None):
    if slug:
        tournament = get_object_or_404(Tournament, slug=slug)
    else:
        slug_q = request.GET.get("t")
        tournament = (
            get_object_or_404(Tournament, slug=slug_q) if slug_q else _default_tournament()
        )

    all_tournaments = Tournament.objects.exclude(status=Tournament.Status.SOON)

    if request.method == "POST" and tournament:
        form = RegistrationForm(request.POST, tournament=tournament)
        if form.is_valid():
            reg = form.save(commit=False)
            reg.tournament = tournament
            reg.code = generate_code(tournament)
            reg.status = Registration.Status.PENDING
            reg.created_at = timezone.now()
            reg.save()

            # Integrantes adicionales del equipo.
            if tournament.requires_team:
                extra = max(tournament.team_size - 1, 0)
                for i in range(2, extra + 2):
                    nick = request.POST.get(f"member_nick_{i}", "").strip()
                    steam = request.POST.get(f"member_steam_{i}", "").strip()
                    if nick or steam:
                        Member.objects.create(
                            registration=reg, nick=nick or f"Jugador {i}",
                            steam_id=steam, order=i,
                        )
            return redirect("confirm", code=reg.code)
    else:
        form = RegistrationForm(tournament=tournament)

    extra_members = []
    if tournament and tournament.requires_team:
        extra_members = list(range(2, max(tournament.team_size - 1, 0) + 2))

    context = {
        "tournament": tournament,
        "tournaments": all_tournaments,
        "form": form,
        "extra_members": extra_members,
    }
    return render(request, "public/register.html", context)


def confirm(request, code):
    reg = get_object_or_404(Registration, code=code)
    return render(request, "public/confirm.html", {"reg": reg})


# =====================================================================
#  Staff
# =====================================================================
class StaffLoginView(LoginView):
    template_name = "staff/login.html"
    redirect_authenticated_user = True


STATUS_ORDER = [
    Registration.Status.PENDING,
    Registration.Status.REVIEW,
    Registration.Status.APPROVED,
    Registration.Status.REJECTED,
]

STATUS_SLUGS = {
    "PENDING": "pendiente", "REVIEW": "revision",
    "APPROVED": "aprobado", "REJECTED": "rechazado",
}


@login_required
def inbox(request):
    qs = Registration.objects.select_related("tournament").all()

    status = request.GET.get("status", "")
    if status in Registration.Status.values:
        qs = qs.filter(status=status)

    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(
            Q(code__icontains=q)
            | Q(team_name__icontains=q)
            | Q(first_name__icontains=q)
            | Q(last_name__icontains=q)
        )

    all_regs = Registration.objects.all()
    filters = [
        {"label": "Todas", "value": "", "n": all_regs.count(), "active": status == ""},
    ]
    for st in STATUS_ORDER:
        filters.append({
            "label": Registration.Status(st).label,
            "value": st,
            "n": all_regs.filter(status=st).count(),
            "active": status == st,
            "slug": STATUS_SLUGS[st],
        })

    context = {"registrations": qs, "filters": filters, "q": q, "status": status}
    return render(request, "staff/inbox.html", context)


def _build_timeline(reg):
    """Línea de estados para el detalle (Enviado → … → estado actual)."""
    s = reg.status
    nodes = [{"label": "Enviado", "state": "done", "slug": "aprobado"}]
    if s == Registration.Status.REJECTED:
        nodes.append({"label": "Rechazado", "state": "current", "slug": "rechazado"})
        return nodes
    order = [
        ("Pendiente", "pendiente"),
        ("En revisión", "revision"),
        ("Aprobado", "aprobado"),
    ]
    idx = {Registration.Status.PENDING: 0, Registration.Status.REVIEW: 1,
           Registration.Status.APPROVED: 2}[s]
    for i, (label, slug) in enumerate(order):
        state = "done" if i < idx else ("current" if i == idx else "todo")
        nodes.append({"label": label, "state": state, "slug": slug})
    return nodes


@login_required
def reg_detail(request, code):
    reg = get_object_or_404(
        Registration.objects.select_related("tournament").prefetch_related("members", "notes"),
        code=code,
    )

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "set_status":
            new_status = request.POST.get("status")
            if new_status in Registration.Status.values and new_status != reg.status:
                old = reg.status
                reg.status = new_status
                reg.save(update_fields=["status"])
                # Mantener cupos ocupados coherentes con las aprobaciones.
                t = reg.tournament
                approved = Registration.Status.APPROVED
                if new_status == approved and old != approved:
                    t.slots_taken = min(t.slots_total, t.slots_taken + 1)
                    t.save(update_fields=["slots_taken"])
                elif old == approved and new_status != approved:
                    t.slots_taken = max(0, t.slots_taken - 1)
                    t.save(update_fields=["slots_taken"])
                notify_status_change(reg)
                messages.success(request, f"Estado actualizado a «{reg.get_status_display()}».")

        elif action == "add_note":
            text = request.POST.get("text", "").strip()
            if text:
                StaffNote.objects.create(registration=reg, author=request.user, text=text)
                messages.success(request, "Nota guardada.")

        return redirect("staff_reg_detail", code=reg.code)

    context = {
        "reg": reg,
        "timeline": _build_timeline(reg),
        "status_choices": Registration.Status.choices,
    }
    return render(request, "staff/reg_detail.html", context)


@admin_required
def create_tournament(request):
    if request.method == "POST":
        form = TournamentForm(request.POST)
        if form.is_valid():
            t = form.save()
            messages.success(request, f"Torneo «{t.name}» publicado.")
            return redirect("staff_inbox")
    else:
        form = TournamentForm()
    return render(request, "staff/create.html", {"form": form})
