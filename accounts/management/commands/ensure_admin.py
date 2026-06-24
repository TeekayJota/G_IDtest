"""Crea un usuario administrador desde variables de entorno, si no existe.

Pensado para Railway (sin shell interactiva). Idempotente: si el usuario ya
existe no hace nada (no pisa la contraseña). Variables:

    ADMIN_USERNAME  (por defecto: admin)
    ADMIN_EMAIL     (opcional)
    ADMIN_PASSWORD  (obligatoria; si falta, se omite sin error)
"""

import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    help = "Crea un admin desde ADMIN_USERNAME/ADMIN_EMAIL/ADMIN_PASSWORD si no existe."

    def handle(self, *args, **options):
        username = os.environ.get("ADMIN_USERNAME", "admin").strip()
        email = os.environ.get("ADMIN_EMAIL", "").strip()
        password = os.environ.get("ADMIN_PASSWORD", "")

        if not password:
            self.stdout.write("ensure_admin: ADMIN_PASSWORD no definida, se omite.")
            return

        if User.objects.filter(username=username).exists():
            self.stdout.write(f"ensure_admin: el usuario '{username}' ya existe, sin cambios.")
            return

        user = User.objects.create(
            username=username, email=email,
            role=User.Role.ADMIN, is_staff=True, is_superuser=True,
        )
        user.set_password(password)
        user.save()
        self.stdout.write(self.style.SUCCESS(f"ensure_admin: admin '{username}' creado."))
