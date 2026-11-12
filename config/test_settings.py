"""Database-backed tests are allowed only in a separate Supabase project."""

from django.core.exceptions import ImproperlyConfigured

from .environment import database_config, required, supabase_project
from .settings import *  # noqa: F403

test_database = database_config(required("TEST_DATABASE_URL"), "session")
if supabase_project(test_database) == supabase_project(DATABASES["default"]):  # noqa: F405
    raise ImproperlyConfigured(
        "TEST_DATABASE_URL must select a separate disposable Supabase project."
    )
# Use only the explicitly selected disposable project's existing database.
# --keepdb avoids requiring CREATE DATABASE privileges in hosted PostgreSQL.
test_database["TEST"] = {"NAME": test_database["NAME"]}
DATABASES = {"default": test_database}
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
STORAGES = {"staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"}}
