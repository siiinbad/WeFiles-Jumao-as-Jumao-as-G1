"""Fresh WeFiles foundation: Django templates and Supabase PostgreSQL only."""

import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

from .environment import boolean, comma_list, database_config, required

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env", override=False)

SECRET_KEY = required("SECRET_KEY")
RENDER_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME", "").strip()
IS_RENDER = boolean("RENDER") or bool(RENDER_HOSTNAME)
DEBUG = boolean("DEBUG", default=False) and not IS_RENDER
ALLOWED_HOSTS = comma_list("ALLOWED_HOSTS", default="localhost,127.0.0.1,[::1]" if DEBUG else "")
CSRF_TRUSTED_ORIGINS = comma_list("CSRF_TRUSTED_ORIGINS")
if RENDER_HOSTNAME:
    if RENDER_HOSTNAME not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(RENDER_HOSTNAME)
    render_origin = f"https://{RENDER_HOSTNAME}"
    if render_origin not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(render_origin)
if not DEBUG:
    if len(SECRET_KEY) < 50:
        raise ImproperlyConfigured("Production SECRET_KEY must contain at least 50 characters.")
    if not ALLOWED_HOSTS or "*" in ALLOWED_HOSTS:
        raise ImproperlyConfigured("Set explicit production ALLOWED_HOSTS or a Render hostname.")
    if any(not origin.startswith("https://") for origin in CSRF_TRUSTED_ORIGINS):
        raise ImproperlyConfigured("Production CSRF_TRUSTED_ORIGINS must use HTTPS.")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "accounts.apps.AccountsConfig",
    "core.apps.CoreConfig",
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
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"
DATABASES = {
    "default": database_config(required("DATABASE_URL"), os.getenv("DATABASE_POOL_MODE", "auto"))
}
AUTH_USER_MODEL = "accounts.User"
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
LANGUAGE_CODE = "en-us"
TIME_ZONE = os.getenv("TIME_ZONE", "Asia/Manila")
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STORAGES = {
    # Validate these only when storage is used, so missing upload credentials
    # cannot prevent static collection or database management commands.
    "default": {
        "BACKEND": "core.storage.PrivateSupabaseStorage",
        "OPTIONS": {
            "endpoint_url": os.getenv("SUPABASE_S3_ENDPOINT_URL", "").strip(),
            "region_name": os.getenv("SUPABASE_S3_REGION", "").strip(),
            "bucket_name": os.getenv("SUPABASE_STORAGE_BUCKET", "").strip(),
            "access_key": os.getenv("SUPABASE_S3_ACCESS_KEY_ID", "").strip(),
            "secret_key": os.getenv("SUPABASE_S3_SECRET_ACCESS_KEY", "").strip(),
        },
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        if DEBUG
        else "whitenoise.storage.CompressedManifestStaticFilesStorage"
    },
}

SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_SSL_REDIRECT = not DEBUG
# Render must receive actual DB readiness, even on an internal HTTP probe.
# The endpoint exposes only a status and performs no authentication or writes.
SECURE_REDIRECT_EXEMPT = [r"^health/ready/$"]
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG
SECURE_REFERRER_POLICY = "same-origin"
X_FRAME_OPTIONS = "DENY"
if boolean("TRUST_PROXY_HTTPS"):
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
