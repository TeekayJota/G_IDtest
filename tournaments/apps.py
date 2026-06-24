from django.apps import AppConfig
from django.db.backends.signals import connection_created


def _set_sqlite_pragmas(sender, connection, **kwargs):
    """Optimiza SQLite para producción: WAL mejora la concurrencia
    lectura/escritura durante los eventos (los lectores no bloquean al
    escritor) y busy_timeout evita errores de 'database is locked'."""
    if connection.vendor == "sqlite":
        cursor = connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.execute("PRAGMA synchronous=NORMAL;")
        cursor.execute("PRAGMA busy_timeout=5000;")


class TournamentsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "tournaments"

    def ready(self):
        connection_created.connect(_set_sqlite_pragmas)
