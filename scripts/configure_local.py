"""Create a persistent local .env without replacing existing values.

Run after installing requirements.txt. PostgreSQL can run through compose.yaml
or an existing local/Supabase instance supplied with --database-url.
"""
import argparse
import secrets
from pathlib import Path
from urllib.parse import quote, urlsplit

from dotenv import dotenv_values, set_key

ROOT = Path(__file__).resolve().parent.parent


def validate_database_url(value):
    try:
        parsed = urlsplit(value)
        if (parsed.scheme not in {"postgres", "postgresql"}
                or not all((parsed.hostname, parsed.username, parsed.password, parsed.path.strip("/")))
                or any(character in value for character in "\r\n")
                or parsed.fragment):
            raise ValueError
        if parsed.port is not None and not 1 <= parsed.port <= 65535:
            raise ValueError
    except (ValueError, TypeError):
        raise ValueError("Use a complete PostgreSQL DATABASE_URL; URL-encode special password characters.") from None


def configure_local(env_path, *, database_url=None, template_path=None):
    env_path = Path(env_path)
    template_path = Path(template_path) if template_path else ROOT / ".env.example"
    existing = dict(dotenv_values(env_path, interpolate=False)) if env_path.exists() else {}
    if database_url and existing.get("DATABASE_URL") and existing["DATABASE_URL"] != database_url:
        raise ValueError("Existing DATABASE_URL was preserved. Edit .env explicitly to change databases.")
    if existing.get("SECRET_KEY") and len(existing["SECRET_KEY"]) < 50:
        raise ValueError("Existing SECRET_KEY is too short. Set at least 50 random characters in .env.")
    values = {
        "SECRET_KEY": existing.get("SECRET_KEY") or secrets.token_urlsafe(64),
        "DJANGO_DEBUG": existing.get("DJANGO_DEBUG") or "True",
        "ALLOWED_HOSTS": existing.get("ALLOWED_HOSTS") or "localhost,127.0.0.1",
        "PRIVATE_STORAGE_BACKEND": existing.get("PRIVATE_STORAGE_BACKEND") or "local",
        "POSTGRES_DB": existing.get("POSTGRES_DB") or "wefiles",
        "POSTGRES_USER": existing.get("POSTGRES_USER") or "wefiles",
        "POSTGRES_PASSWORD": existing.get("POSTGRES_PASSWORD") or secrets.token_urlsafe(32),
        "POSTGRES_PORT": existing.get("POSTGRES_PORT") or "55432",
    }
    try:
        port = int(values["POSTGRES_PORT"])
        if not 1 <= port <= 65535:
            raise ValueError
    except (TypeError, ValueError):
        raise ValueError("POSTGRES_PORT must be a number between 1 and 65535.") from None
    local_url = "postgresql://{}:{}@127.0.0.1:{}/{}".format(
        quote(values["POSTGRES_USER"], safe=""),
        quote(values["POSTGRES_PASSWORD"], safe=""), port,
        quote(values["POSTGRES_DB"], safe=""),
    )
    values["DATABASE_URL"] = existing.get("DATABASE_URL") or database_url or local_url
    validate_database_url(values["DATABASE_URL"])
    changed = [key for key in values if not existing.get(key)]
    # Validate all inputs before touching an existing file.
    if not env_path.exists():
        with env_path.open("x", encoding="utf-8", newline="\n") as target:
            target.write(template_path.read_text(encoding="utf-8"))
        env_path.chmod(0o600)
    for key in changed:
        set_key(str(env_path), key, values[key], quote_mode="always")
    return changed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database-url", help="Optional existing PostgreSQL/Supabase URL; otherwise use Compose PostgreSQL.")
    args = parser.parse_args()
    try:
        changed = configure_local(ROOT / ".env", database_url=args.database_url)
    except (OSError, ValueError) as error:
        parser.exit(1, f"Local setup failed: {error}\n")
    print("Prepared .env; existing values were preserved." if changed else ".env is already configured; existing values were preserved.")
    print("For the default local database: docker compose up -d --wait db")
    print("Then run manage.py migrate and manage.py runserver with your virtual environment's Python.")


if __name__ == "__main__":
    main()
