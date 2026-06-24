from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

MONTHS_ES = ["", "Ene", "Feb", "Mar", "Abr", "May", "Jun",
             "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]

# Etiqueta corta por juego (la que va en el recuadro de la tarjeta).
GAME_TAGS = {
    "Dota 2": "D2",
    "Fortnite": "FN",
    "eFootball": "EF",
    "Clash Royale": "CR",
}


class Game(models.TextChoices):
    DOTA = "Dota 2", "Dota 2"
    FORTNITE = "Fortnite", "Fortnite"
    EFOOTBALL = "eFootball", "eFootball"
    CLASH = "Clash Royale", "Clash Royale"


class Tournament(models.Model):
    class Format(models.TextChoices):
        TEAM = "TEAM", "Equipos"
        DUO = "DUO", "Dúo"
        SOLO = "SOLO", "Individual"

    class Status(models.TextChoices):
        OPEN = "OPEN", "Inscripciones abiertas"
        FEW = "FEW", "Pocos cupos"
        SOON = "SOON", "Próximamente"

    name = models.CharField("Nombre del torneo", max_length=160)
    slug = models.SlugField(unique=True, max_length=180, blank=True)
    game = models.CharField("Juego", max_length=40, choices=Game.choices)
    format = models.CharField("Formato", max_length=8, choices=Format.choices, default=Format.TEAM)
    team_size = models.PositiveSmallIntegerField("Jugadores por equipo", default=5)

    start_date = models.DateField("Inicio")
    end_date = models.DateField("Fin")
    registration_close = models.DateTimeField("Cierre de inscripción")

    prize_pen = models.PositiveIntegerField("Premio (S/)", default=0)
    slots_total = models.PositiveIntegerField("Cupos", default=32)
    slots_taken = models.PositiveIntegerField("Cupos ocupados", default=0)
    status = models.CharField("Estado", max_length=8, choices=Status.choices, default=Status.OPEN)

    description = models.TextField("Reglas / descripción", blank=True)
    featured = models.BooleanField("Torneo destacado", default=False)
    code_prefix = models.CharField("Prefijo de código", max_length=8, default="BTD")

    # Qué campos pide el formulario público de inscripción.
    field_dni = models.BooleanField("Pedir DNI", default=True)
    field_phone = models.BooleanField("Pedir teléfono", default=True)
    field_email = models.BooleanField("Pedir correo", default=True)
    field_steam = models.BooleanField("Pedir Steam ID", default=False)
    field_nick = models.BooleanField("Pedir nick / usuario", default=True)
    field_gaming_center = models.BooleanField("Pedir gaming center", default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-featured", "start_date"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name) or slugify(self.game)
            slug = base
            i = 2
            while Tournament.objects.exclude(pk=self.pk).filter(slug=slug).exists():
                slug = f"{base}-{i}"
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)

    # --- Presentación ---------------------------------------------------------
    @property
    def tag(self) -> str:
        return GAME_TAGS.get(self.game, (self.game[:2] or "GG").upper())

    @property
    def requires_team(self) -> bool:
        return self.format in (self.Format.TEAM, self.Format.DUO) and self.team_size > 1

    @property
    def mode_label(self) -> str:
        if self.format == self.Format.TEAM:
            return f"{self.team_size} vs {self.team_size} · Equipos"
        if self.format == self.Format.DUO:
            return "Dúos"
        return "1 vs 1"

    @property
    def type_label(self) -> str:
        if self.format == self.Format.TEAM:
            return f"Equipo · {self.team_size}"
        if self.format == self.Format.DUO:
            return f"Dúo · {self.team_size}"
        return "Individual"

    @property
    def prize_label(self) -> str:
        return f"S/ {self.prize_pen:,}"

    @property
    def slots_label(self) -> str:
        return f"{self.slots_taken} / {self.slots_total}"

    @property
    def slots_pct(self) -> int:
        if not self.slots_total:
            return 0
        return min(100, round(self.slots_taken * 100 / self.slots_total))

    @property
    def status_slug(self) -> str:
        return {"OPEN": "abierto", "FEW": "pocos", "SOON": "proximo"}[self.status]

    def _fmt_date(self, d, with_year=False):
        year = f" {d.year}" if with_year else ""
        return f"{d.day} {MONTHS_ES[d.month]}{year}"

    @property
    def dates_label(self) -> str:
        s, e = self.start_date, self.end_date
        if s == e:
            return self._fmt_date(s)
        if s.month == e.month and s.year == e.year:
            return f"{s.day} – {e.day} {MONTHS_ES[s.month]}"
        return f"{self._fmt_date(s)} – {self._fmt_date(e)}"

    @property
    def dates_label_year(self) -> str:
        base = self.dates_label
        if str(self.end_date.year) not in base:
            base = f"{base} {self.end_date.year}"
        return base

    @property
    def close_label(self) -> str:
        dt = timezone.localtime(self.registration_close)
        return f"{dt.day} {MONTHS_ES[dt.month]} · {dt:%H:%M}"


class Registration(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pendiente"
        REVIEW = "REVIEW", "En revisión"
        APPROVED = "APPROVED", "Aprobado"
        REJECTED = "REJECTED", "Rechazado"

    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name="registrations")
    code = models.CharField(max_length=20, unique=True, db_index=True)

    team_name = models.CharField("Nombre del equipo", max_length=120, blank=True)

    # Datos del capitán / jugador que llena el formulario.
    first_name = models.CharField("Nombre", max_length=80)
    last_name = models.CharField("Apellido", max_length=80, blank=True)
    dni = models.CharField("DNI", max_length=15, blank=True)
    phone = models.CharField("Teléfono", max_length=30, blank=True)
    email = models.EmailField("Correo", blank=True)
    steam_id = models.CharField("Steam ID", max_length=60, blank=True)
    nick = models.CharField("Nick / usuario", max_length=60, blank=True)
    gaming_center = models.CharField("Gaming center", max_length=120, blank=True)

    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.code} · {self.display_name}"

    @property
    def display_name(self) -> str:
        if self.team_name:
            return self.team_name
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def captain_full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def status_slug(self) -> str:
        return {
            "PENDING": "pendiente",
            "REVIEW": "revision",
            "APPROVED": "aprobado",
            "REJECTED": "rechazado",
        }[self.status]

    @property
    def type_label(self) -> str:
        return self.tournament.type_label

    @property
    def players_count(self) -> int:
        # Capitán + integrantes adicionales.
        return self.members.count() + 1

    @property
    def created_label(self) -> str:
        dt = timezone.localtime(self.created_at)
        return f"{dt.day} {MONTHS_ES[dt.month]} · {dt:%H:%M}"

    @property
    def created_label_full(self) -> str:
        dt = timezone.localtime(self.created_at)
        return f"{dt.day} {MONTHS_ES[dt.month]} {dt.year} · {dt:%H:%M}"


class Member(models.Model):
    """Integrante adicional de un equipo (además del capitán)."""

    registration = models.ForeignKey(Registration, on_delete=models.CASCADE, related_name="members")
    nick = models.CharField("Nick", max_length=60)
    steam_id = models.CharField("Steam ID", max_length=60, blank=True)
    dni = models.CharField("DNI", max_length=15, blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.nick

    @property
    def initial(self) -> str:
        return (self.nick[:1] or "?").upper()


class StaffNote(models.Model):
    """Nota interna del staff sobre una inscripción."""

    registration = models.ForeignKey(Registration, on_delete=models.CASCADE, related_name="notes")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    author_label = models.CharField(max_length=120, blank=True)
    text = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Nota de {self.author_label or self.author} · {self.created_at:%d/%m}"

    @property
    def author_name(self) -> str:
        if self.author_label:
            return self.author_label
        if self.author:
            role = self.author.get_role_display()
            return f"{self.author.get_full_name() or self.author.username} ({role})"
        return "Staff"

    @property
    def time_label(self) -> str:
        dt = timezone.localtime(self.created_at)
        return f"{dt.day} {MONTHS_ES[dt.month]} · {dt:%H:%M}"
