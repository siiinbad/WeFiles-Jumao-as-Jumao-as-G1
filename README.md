# WeFiles — fresh build

A new Django project, built one feature at a time. The original application is
kept in the separate sibling `WeFiles/` directory. This project has its own Git
history, environment and database; no old application code or data was copied.

Current session: **Day 1-A — Django and Supabase foundation**. The public landing
page and Django admin are wired. Member sign-in, vault uploads and other file
features will be added in later sessions.

## Local setup

From this folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python scripts/configure_local.py
```

The helper creates an ignored private `.env`, generates SECRET_KEY if missing,
and preserves existing values. Open `.env` locally and set DATABASE_URL to the
**Session pooler** URI from **Connect** in a NEW Supabase project. Copy the exact
hostname and `postgres.PROJECT_REF` username; URL-encode its password component.
Do not reuse the existing application's database or credentials.

```dotenv
# Placeholder only — use your project's actual pooler URI privately.
DATABASE_URL=postgresql://postgres.PROJECT_REF:URL_ENCODED_PASSWORD@POOLER_HOST:5432/postgres?sslmode=require
```

Use port 5432 Session pooling rather than the direct IPv6 database host, which
Render may not reach. The app enforces SSL. Transaction port 6543 automatically
disables persistent connections and server-side cursors. No SQLite fallback.
See [Supabase connection guidance](https://supabase.com/docs/guides/database/connecting-to-postgres).

After setting DATABASE_URL:

```bash
python manage.py check
python manage.py migrate --plan
python manage.py migrate --noinput
python manage.py createsuperuser
python manage.py runserver
```

Open http://127.0.0.1:8000/ or http://127.0.0.1:8000/admin/. The minimal custom
User model is installed before its first migration. Do not apply these initial
migrations over the old project's database.

## Environment

| Variable | Purpose |
| --- | --- |
| SECRET_KEY | Required random secret; the local helper creates it privately. |
| DATABASE_URL | Required Supabase PostgreSQL URL; SSL is enforced. |
| DATABASE_POOL_MODE | auto by default; transaction explicitly disables persistent connections/cursors on any port. |
| DEBUG | True locally; defaults to False and is always False on Render. |
| ALLOWED_HOSTS | Comma-separated hosts; explicit production hosts required unless Render supplies its hostname. |
| CSRF_TRUSTED_ORIGINS | Comma-separated origins; production requires HTTPS. |
| RENDER_EXTERNAL_HOSTNAME | Automatically allowed, with its HTTPS CSRF origin. |
| TRUST_PROXY_HTTPS | True only behind a trusted proxy such as Render. |
| TEST_DATABASE_URL | Separate disposable Supabase project; required by database-backed test settings. |
| TIME_ZONE | Asia/Manila by default. |

Never commit `.env`, private environment variants, credentials, virtual
environments, generated static output, uploads or caches. If a real secret was
ever committed, rotate it immediately.

## Verification

Configuration safety tests do not require a database or private .env:

```bash
python -m unittest core.tests.test_environment
```

Once your private .env is configured, run the full current foundation suite
(all current cases avoid database access), system checks and formatting:

```bash
python manage.py test core.tests --noinput
python manage.py check
python manage.py makemigrations --check --dry-run
ruff check .
ruff format --check .
```

Future database-backed tests must use a separate disposable Supabase project:
set TEST_DATABASE_URL in .env and run
`python manage.py test --settings=config.test_settings --keepdb --noinput`.
These settings reject a test URL identifying the normal app's Supabase project,
even across direct/session/transaction endpoints. Test runs must be serialized.
The dedicated test database may be flushed; never point it at real app data.

## Render — next session

The next session adds build.sh and render.yaml, a readiness endpoint and private
Supabase Storage configuration. The planned Render service uses this Git root
(Root Directory blank), `bash build.sh`, and
`gunicorn config.wsgi:application --bind 0.0.0.0:$PORT`.
Set environment secrets in Render, DEBUG=False and TRUST_PROXY_HTTPS=True.
Build installs pinned requirements, collects static assets and migrates the
external Supabase database. No Render PostgreSQL service or durable local media.

There is no upload backend or file model yet; durable uploads will use a private
Supabase bucket configured before their feature is introduced.

## Progress: two real commits per day

| Planned date (Asia/Manila) | Morning | Evening |
| --- | --- | --- |
| November 13, 2026 | Day 1-A: Django/Supabase foundation | Day 1-B: Render/Storage foundation |
| November 14, 2026 | Day 2-A: member sign-in/out | Day 2-B: private upload/list |
| November 15, 2026 | Day 3-A: secure download | Day 3-B: edit metadata |
| November 16, 2026 | Day 4-A: delete with retryable cleanup | Day 4-B: release verification |

- [x] Fresh Django scaffold, inherited template and responsive base styles
- [x] Environment-only secrets and SSL Supabase database settings
- [x] Minimal custom User and initial migration file
- [ ] Apply migrations to the NEW Supabase project and verify admin access
- [ ] Render build, health/static checks and private Storage configuration
- [ ] Member authentication
- [ ] Private file CRUD
- [ ] Final deployment tests and operational documentation

Git is initialized on `main`; there are no commits or remotes yet. You will
configure your own name/email. Create a NEW Public repository named
`WeFiles-Lastname-Firstname-Section` before adding its origin. Do not reuse the
old repository's remote. After the Day 1-A acceptance checks:

```bash
git add .env.example .gitignore README.md manage.py pyproject.toml requirements.txt requirements-dev.txt config accounts core scripts static templates docs
git diff --cached
TZ=Asia/Manila git commit -m "chore: bootstrap Django with Supabase PostgreSQL"
git push -u origin main
```

Commits record their actual creation time; work is not pre-committed for future
sessions. See docs/verification.md for the checks actually performed.
