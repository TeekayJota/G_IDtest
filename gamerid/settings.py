"""
Django settings for GamerID — plataforma de inscripción a torneos.
"""

from pathlib import Path
import os

import dj_database_url
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Carga variables desde .env (si existe). Nada sensible se versiona.
load_dotenv(BASE_DIR / ".env")


def env_bool(name, default=False):
    val = os.environ.get(name)
    if val is None:
        return default
    return val.strip().lower() in {"1", "true", "yes", "on"}


# --- Seguridad / entorno -----------------------------------------------------
SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "dev-insecure-key-change-me-in-prod-0000000000000000000000000000",
)
DEBUG = env_bool("DEBUG", True)
ALLOWED_HOSTS = [
    h.strip() for h in os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",") if h.strip()
]
CSRF_TRUSTED_ORIGINS = [
    o.strip() for o in os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",") if o.strip()
]

# Railway expone el dominio público generado en esta variable. Lo agregamos
# automáticamente para que la app funcione sin pelear con ALLOWED_HOSTS.
_railway_domain = os.environ.get("RAILWAY_PUBLIC_DOMAIN", "").strip()
if _railway_domain:
    ALLOWED_HOSTS.append(_railway_domain)
    CSRF_TRUSTED_ORIGINS.append(f"https://{_railway_domain}")

# Barra "PROTOTIPO · DEMO" para navegar entre pantallas. En prod queda apagada.
SHOW_DEMO_NAV = env_bool("SHOW_DEMO_NAV", DEBUG)


# --- Apps --------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "accounts",
    "tournaments",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # WhiteNoise sirve los archivos estáticos en producción (sin Nginx/CDN aparte).
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "gamerid.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "gamerid.context_processors.demo_nav",
            ],
        },
    },
]

WSGI_APPLICATION = "gamerid.wsgi.application"


# --- Base de datos -----------------------------------------------------------
# Dev: SQLite (cero configuración). Prod: define DATABASE_URL (Postgres) en .env
# y no cambias nada más. Ej: postgres://user:pass@localhost:5432/gamerid
DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
    )
}


# --- Autenticación / usuarios ------------------------------------------------
AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LOGIN_URL = "staff_login"
LOGIN_REDIRECT_URL = "staff_inbox"
LOGOUT_REDIRECT_URL = "staff_login"


# --- Internacionalización ----------------------------------------------------
LANGUAGE_CODE = "es"
TIME_ZONE = "America/Lima"
USE_I18N = True
USE_TZ = True


# --- Archivos estáticos ------------------------------------------------------
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# En producción (DEBUG=False) WhiteNoise comprime y cachea los estáticos.
# En dev se usa el almacenamiento normal para no exigir collectstatic.
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": (
            "django.contrib.staticfiles.storage.StaticFilesStorage"
            if DEBUG
            else "whitenoise.storage.CompressedManifestStaticFilesStorage"
        ),
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# --- Seguridad en producción (solo cuando DEBUG=False) -----------------------
# Detrás de un proxy/HTTPS (Nginx, Caddy, etc.) que reenvía X-Forwarded-Proto.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
if not DEBUG:
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"
    # Activa estos cuando el dominio ya tenga HTTPS (evita romper un demo en http):
    SECURE_SSL_REDIRECT = env_bool("SECURE_SSL_REDIRECT", False)
    SESSION_COOKIE_SECURE = env_bool("COOKIE_SECURE", False)
    CSRF_COOKIE_SECURE = env_bool("COOKIE_SECURE", False)
    SECURE_HSTS_SECONDS = int(os.environ.get("SECURE_HSTS_SECONDS", "0"))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool("SECURE_HSTS_SUBDOMAINS", False)


# --- Correo ------------------------------------------------------------------
# Configurado pero "apagado": en dev los correos se imprimen en consola.
# Para activar el SMTP del cliente, define EMAIL_* en .env y cambia el backend.
EMAIL_BACKEND = os.environ.get(
    "EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend"
)
EMAIL_HOST = os.environ.get("EMAIL_HOST", "")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
EMAIL_USE_TLS = env_bool("EMAIL_USE_TLS", True)
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "GamerID <no-reply@gamerid.gg>")

# Interruptor para enviar (o no) avisos por correo al cambiar de estado.
SEND_STATUS_EMAILS = env_bool("SEND_STATUS_EMAILS", False)
