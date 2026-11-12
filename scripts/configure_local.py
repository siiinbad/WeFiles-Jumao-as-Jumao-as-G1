"""Create a private local .env and generate its missing secret without printing it."""

import os
import secrets
from pathlib import Path

from dotenv import dotenv_values, set_key

root = Path(__file__).resolve().parent.parent
path = root / ".env"
previous_mask = os.umask(0o077)
try:
    if not path.exists():
        path.write_text((root / ".env.example").read_text())
    if not dotenv_values(path).get("SECRET_KEY"):
        set_key(path, "SECRET_KEY", secrets.token_urlsafe(64))
    path.chmod(0o600)
finally:
    os.umask(previous_mask)
print("Private .env prepared. Set DATABASE_URL to your new Supabase Session pooler URL.")
