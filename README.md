# WeFiles — fresh build

A new Django project, built one feature at a time. The original application is
kept in the separate sibling `WeFiles/` directory. This project has its own Git
history, environment and database; no old application code or data was copied.

Current session: **Day 1-B — Render and private Storage foundation**. Deployment
files, database readiness and the private Storage adapter are implemented.
Live deployment still needs your provider configuration. Member sign-in and
file-upload screens begin in Day 2; they are not included in this session.

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
| SUPABASE_S3_ENDPOINT_URL | Exact HTTPS endpoint from Supabase Storage S3 settings, including /storage/v1/s3. |
| SUPABASE_S3_REGION | Region copied from the same S3 settings. |
| SUPABASE_STORAGE_BUCKET | Private bucket name, e.g. wefiles-private. |
| SUPABASE_S3_ACCESS_KEY_ID | Generated server-side S3 access key; not the anon/publishable key. |
| SUPABASE_S3_SECRET_ACCESS_KEY | Matching server-side S3 secret; never expose it in HTML or Git. |

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

## Private Supabase Storage

1. In your NEW Supabase project, create a bucket such as `wefiles-private` and
   leave **Public bucket disabled**. Configure the size limit appropriate to
   your workspace. Do not create a public-read policy for this bucket.
2. Open Storage's S3 settings. Generate an Access Key ID/Secret Access Key pair;
   copy its endpoint and region. These are S3 credentials, not database,
   publishable/anon or service-role keys.
3. Add the five SUPABASE_* variables from .env.example to your private .env.
   Keep the endpoint exactly as supplied; it commonly looks like
   `https://PROJECT_REF.storage.supabase.co/storage/v1/s3`.
4. Run the explicit server-side check:

```bash
python manage.py check_storage
```

It writes, reads and deletes one random `_checks/` object. Failures stop the
command; a failed cleanup reports the disposable key to remove manually. The
check verifies server-side access, not bucket visibility. Separately confirm
the bucket remains private and an unauthenticated public object URL cannot
read an object. Never make a private bucket public to fix an authorization error.

S3 keys bypass RLS and remain server-only. The backend refuses `.url()` calls;
future downloads will go through owner-checked Django views. It uses no local
upload fallback and sends no unsupported ACL header. See
[Supabase S3 authentication](https://supabase.com/docs/guides/storage/s3/authentication)
and [S3 compatibility](https://supabase.com/docs/guides/storage/s3/compatibility).

Storage settings are validated lazily when storage is used. This lets database
management and static collection work before upload credentials are configured.
There is still no user-facing upload or download feature in this session.

## Deploy on Render

The committed .python-version pins Python 3.14.10, matching local verification.
Connect this fresh repository to Render; do not select the old application.
Use **New → Blueprint** and its render.yaml, or create a Python web service:

| Dashboard field | Value |
| --- | --- |
| Branch | main |
| Root Directory | Blank: manage.py is at the repository root. |
| Build Command | `bash build.sh` |
| Start Command | The complete startCommand in render.yaml (Gunicorn binds 0.0.0.0:$PORT). |
| Health Check Path | /health/ready/ |
| Environment | DEBUG=False, TRUST_PROXY_HTTPS=True, DATABASE_URL and the five private Storage variables. |
| SECRET_KEY | Independent stable random production key, at least 50 characters. |
| Database/disk | External Supabase only; no Render PostgreSQL or persistent media disk. |

Generate the production secret privately, for example in your own terminal:

```bash
python -c 'import secrets; print(secrets.token_urlsafe(64))'
```

Paste it into Render's SECRET_KEY field and keep it stable across deployments.
Do not put the output in a source file or chat. Blueprint `sync: false` fields
prompt during initial creation; add new values manually in Environment when
updating an already-created service. ALLOWED_HOSTS and the HTTPS CSRF origin
automatically include RENDER_EXTERNAL_HOSTNAME; custom domains need their own
explicit host/origin values. No SITE_URL or email provider is needed yet.

build.sh installs requirements, runs production checks, collects static assets,
and applies existing migrations. It exits immediately if any step fails. A
working Supabase pooler URL is necessary to complete the build. No additional
model migration was introduced in Day 1-B. Do not use fake credentials to make
a live deploy appear successful.

Gunicorn's access-log format records method/status/duration without request
paths or query strings. WhiteNoise serves versioned static files. Readiness
returns only ready/200 or unavailable/503 after SELECT 1, with no-store caching;
it never writes data or contacts object Storage. Internal health probes are
exempt from Django's SSL redirect so a redirect cannot hide database failure.
Normal application HTTP requests still redirect to HTTPS in production.

After deploying, confirm the landing page, /admin/login/ and its hashed CSS load;
/health/ready/ returns 200; and `check_storage` passes from a configured server
shell or your local environment with the same Supabase bucket. Create the admin
through `python manage.py createsuperuser` after migrations, using a configured
local environment if your Render plan does not provide a shell. Never create
fixed admin credentials in build.sh. Provider acceptance details are in
[operations](docs/operations.md). This follows
[Render's Django deployment workflow](https://render.com/docs/deploy-django)
using Supabase in place of a Render-managed database.

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
- [x] Render build/Blueprint, readiness endpoint and private Storage adapter
- [ ] Live Render deploy and real Supabase Storage smoke/privacy checks
- [ ] Member authentication
- [ ] Private file CRUD
- [ ] Final deployment tests and operational documentation

Day 1-A is commit `127ae1e` on `main`. Day 1-B changes are provided for review;
no automatic commit or push is made by this session. Repository naming follows
`WeFiles-Lastname-Firstname-Section`. Review your staged files before committing:

```bash
git add .env.example .python-version build.sh render.yaml requirements.txt config/settings.py core/views.py core/urls.py core/storage.py core/management core/tests/test_deployment.py core/tests/test_storage.py README.md docs
git diff --cached
TZ=Asia/Manila git commit -m "chore: deploy Django foundation on Render"
git push origin main
```

Commits record their actual creation time; work is not pre-committed for future
sessions. See docs/verification.md for the checks actually performed.
