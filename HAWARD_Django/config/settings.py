"""Configuración local del inventario de hardware."""
import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent

# DEBUG solo se activa con DJANGO_DEBUG=1 (en local). En producción queda apagado.
DEBUG = os.environ.get("DJANGO_DEBUG") == "1"

# La clave secreta de desarrollo solo se permite con DEBUG; en producción es obligatoria.
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = "dev-only-change-this-key"
    else:
        raise ImproperlyConfigured(
            "Define la variable de entorno DJANGO_SECRET_KEY (o DJANGO_DEBUG=1 en local)."
        )

ALLOWED_HOSTS = ["127.0.0.1", "localhost", "haward.onrender.com"]
CSRF_TRUSTED_ORIGINS = ["https://haward.onrender.com"]

if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "inventario",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]
WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# En producción (p. ej. Render) define DATABASE_URL con una base PostgreSQL:
# SQLite en el disco de Render se borra en cada despliegue.
if os.environ.get("DATABASE_URL"):
    import dj_database_url

    DATABASES["default"] = dj_database_url.config(conn_max_age=600)

LANGUAGE_CODE = "es-co"
TIME_ZONE = "America/Bogota"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
STATIC_ROOT = BASE_DIR / "staticfiles"

# Imágenes subidas desde el formulario de productos
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Los usuarios sin sesión se envían al login del administrador
LOGIN_URL = "admin:login"

# Texto que ve el cliente al pagar por transferencia (pon aquí tus datos bancarios / número de Nequi)
TRANSFERENCIA_INSTRUCCIONES = os.environ.get(
    "HAWARD_INSTRUCCIONES_TRANSFERENCIA",
    "Te contactaremos por correo o teléfono con los datos para realizar la transferencia. "
    "Tu pedido queda reservado mientras confirmamos el pago.",
)

# Configuración para que WhiteNoise comprima y guarde en caché los estáticos eficientemente
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
