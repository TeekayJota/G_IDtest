"""Context processors globales."""

from django.conf import settings


def demo_nav(request):
    """Expone la barra de navegación de demo (réplica del prototipo).

    Controlada por SHOW_DEMO_NAV (por defecto = DEBUG). Calcula un torneo y
    un código por defecto para que los enlaces "Detalle"/"Confirmación"
    apunten a algo real.
    """
    show = getattr(settings, "SHOW_DEMO_NAV", False)
    if not show:
        return {"show_demo_nav": False}

    # Import diferido para no cargar modelos al iniciar settings.
    from tournaments.models import Registration, Tournament

    t = Tournament.objects.filter(featured=True).first() or Tournament.objects.first()
    reg = Registration.objects.order_by("-created_at").first()
    return {
        "show_demo_nav": True,
        "demo_slug": t.slug if t else None,
        "demo_code": reg.code if reg else None,
    }
