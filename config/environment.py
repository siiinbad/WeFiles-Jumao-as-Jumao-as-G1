"""Validate deployment configuration without connecting to a database."""

import os

import dj_database_url
from django.core.exceptions import ImproperlyConfigured


def required(name):
    value = os.environ.get(name, "").strip()
    if not value:
        raise ImproperlyConfigured(f"Set {name} in your environment or private .env file.")
    return value


def boolean(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default
    value = value.strip().lower()
    if value in {"true", "1", "yes", "on"}:
        return True
    if value in {"false", "0", "no", "off"}:
        return False
    raise ImproperlyConfigured(f"{name} must be True or False.")


def comma_list(name, default=""):
    return [item.strip() for item in os.environ.get(name, default).split(",") if item.strip()]


def database_config(url, pool_mode="auto"):
    if not url or not url.strip():
        raise ImproperlyConfigured("Set DATABASE_URL to your Supabase Session pooler URL.")
    try:
        database = dj_database_url.parse(
            url, conn_max_age=60, conn_health_checks=True, ssl_require=True
        )
    except (ValueError, TypeError):
        # Do not expose the original URL or driver error: it may contain credentials.
        raise ImproperlyConfigured("DATABASE_URL must be a valid PostgreSQL URL.") from None
    if database["ENGINE"] != "django.db.backends.postgresql":
        raise ImproperlyConfigured("Only Supabase PostgreSQL is supported; SQLite is disabled.")
    host = database.get("HOST", "").lower()
    if not host.endswith((".pooler.supabase.com", ".supabase.co")):
        raise ImproperlyConfigured("Use the database host copied from your Supabase project.")
    if not database.get("USER") or not database.get("PASSWORD") or not database.get("NAME"):
        raise ImproperlyConfigured("DATABASE_URL must include a database, username and password.")
    pool_mode = pool_mode.strip().lower()
    if pool_mode not in {"auto", "session", "transaction"}:
        raise ImproperlyConfigured("DATABASE_POOL_MODE must be auto, session or transaction.")
    transaction_pool = str(database.get("PORT")) == "6543" or pool_mode == "transaction"
    database["CONN_MAX_AGE"] = 0 if transaction_pool else 60
    database["DISABLE_SERVER_SIDE_CURSORS"] = transaction_pool
    # Force SSL even if the supplied URL tries to disable it.
    database.setdefault("OPTIONS", {})["sslmode"] = "require"
    database["OPTIONS"]["connect_timeout"] = 10
    return database


def supabase_project(database):
    """Identify a project across direct/session/transaction connection URLs."""
    host = database["HOST"].lower()
    if host.endswith(".pooler.supabase.com"):
        username = database["USER"]
        if "." in username:
            return username.rsplit(".", 1)[1].lower()
    elif host.startswith("db.") and host.endswith(".supabase.co"):
        return host.removeprefix("db.").removesuffix(".supabase.co")
    raise ImproperlyConfigured("Cannot safely identify this Supabase project's test isolation.")
