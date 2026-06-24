from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Usuario del staff de GamerID.

    Usamos un modelo propio desde el inicio (buena práctica) para poder
    crecer sin migraciones dolorosas. El rol controla qué puede hacer cada
    quien dentro del panel de staff.
    """

    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Administrador"
        STAFF = "STAFF", "Staff"

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.STAFF,
        verbose_name="Rol",
    )

    @property
    def is_admin_role(self) -> bool:
        return self.role == self.Role.ADMIN

    @property
    def initials(self) -> str:
        first = (self.first_name or self.username or "?")[:1]
        last = (self.last_name or "")[:1]
        return (first + last).upper() or "?"

    @property
    def role_label(self) -> str:
        return self.get_role_display()

    def __str__(self):
        full = self.get_full_name()
        return full or self.username
