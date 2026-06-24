"""Utilidades de dominio: generación de códigos y avisos por correo."""

import random

from django.conf import settings
from django.core.mail import send_mail


def generate_code(tournament) -> str:
    """Genera un código único de seguimiento, ej. BTD-0241."""
    from .models import Registration

    prefix = (tournament.code_prefix or "GID").upper()
    for _ in range(50):
        code = f"{prefix}-{random.randint(100, 9999):04d}"
        if not Registration.objects.filter(code=code).exists():
            return code
    # Fallback prácticamente imposible de alcanzar.
    n = Registration.objects.count() + 1
    return f"{prefix}-{n:06d}"


def notify_status_change(registration) -> None:
    """Envía un correo al jugador cuando cambia el estado de su inscripción.

    Apagado por defecto (SEND_STATUS_EMAILS=False). Cuando el cliente
    entregue su SMTP, basta activarlo en el .env: nada de código cambia.
    """
    if not getattr(settings, "SEND_STATUS_EMAILS", False):
        return
    if not registration.email:
        return

    estado = registration.get_status_display()
    subject = f"GamerID · Tu inscripción {registration.code} está {estado}"
    body = (
        f"Hola {registration.first_name},\n\n"
        f"El estado de tu inscripción para «{registration.tournament.name}» "
        f"(código {registration.code}) ahora es: {estado}.\n\n"
        "Puedes consultar el detalle en la página del torneo.\n\n"
        "— Equipo GamerID · Beyond the Dreams"
    )
    send_mail(
        subject,
        body,
        settings.DEFAULT_FROM_EMAIL,
        [registration.email],
        fail_silently=True,
    )
