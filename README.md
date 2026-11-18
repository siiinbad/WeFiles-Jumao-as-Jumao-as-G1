# WeFiles - Project Development 2 (in progress)

Increment 2 in `wefiles-increment/` builds on this checkout's existing Django
account feature and uses `../WeFiles/` as the reference for folders, uploads,
private downloads, validation and storage cleanup. The original `WeFiles/`
application is preserved. This increment is being prepared; Supabase and Render
are not configured and the submission is not final.

## Core feature: private file vault

A member signs in, opens **My files**, creates nested folders, uploads one file
(up to 50 MiB), browses and downloads it, edits its name/description/location,
and confirms deletion. Empty folders can be renamed, moved and deleted.
Administrators use **All files** to manage records across accounts; uploads and
new folders always belong to the signed-in creator. Success/error messages and
server-side form validation cover every mutation.

Every file and folder has an owner ForeignKey to `accounts.User`. Members can
only access their own records, including direct detail/download/edit/delete
URLs and destination selectors. Administrators retain the original owner's
identity when managing records. Folder parents and file destinations must
belong to that owner. Folder names are unique within the same parent and owner,
case-insensitively; cycles, excessive nesting and deletion of nonempty folders
are rejected. Downloads are authenticated attachments with private cache headers.

All account, session, folder, file metadata and deletion-job records use
PostgreSQL (Supabase PostgreSQL is supported; there is no SQLite fallback).
Uploaded bytes use a private Supabase Storage bucket in production, accessed
through its S3 interface. Local filesystem storage is allowed only in debug
mode. Production startup refuses local upload storage or missing cloud settings.

Registration, login/POST logout, Admin/Member dashboards and own profile editing
remain included. New registrations cannot select privileges. Workspace Admin
roles are separate from Django maintenance staff permissions.

The interface uses the original WeFiles logo, sidebar, design tokens, responsive
file tables, account cards and theme controls. See [UI reference](docs/UI_REFERENCE.md)
for the source assets and adapted screens. Workspace search and dashboard
statistics respect the same owner/Admin access rules.

## Run from a fresh clone

Install **Git**, **Python 3.12+** (Python 3.14 matches the series in
`.python-version`), and **Docker with Compose v2.20+**. On Windows/macOS, install
[Docker Desktop](https://docs.docker.com/desktop/) and start it before the database
command. On Linux, use Docker Engine with its Compose plugin.

Clone the setup feature branch while this increment is in progress:

```bash
git clone --branch feature/local-setup https://github.com/siiinbad/WeFiles-Jumao-as-Jumao-as-G1.git wefiles
cd wefiles
```

Run the following commands from this repository's root, which contains
`manage.py`. The application is at the root of the clone; there is no additional
`wefiles-increment` directory to enter. If you already cloned it, fetch and switch
to `feature/local-setup` before following the commands.

### Windows PowerShell

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts\configure_local.py
docker compose up -d --wait db
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py runserver
```

These commands use the virtual environment's Python directly; PowerShell script
activation and execution-policy changes are unnecessary.

### macOS / Linux

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/configure_local.py
docker compose up -d --wait db
.venv/bin/python manage.py migrate
.venv/bin/python manage.py runserver
```

Open **http://127.0.0.1:8000/**, create an account, and sign in. The setup helper
creates an ignored `.env` with a random Django secret and PostgreSQL password,
and a matching local database URL. It preserves existing values when run again.
Compose creates the database and login, waits for PostgreSQL to become healthy,
and stores its records in a named Docker volume. Upload bytes are stored in the
ignored `media/` directory for local development.

A clone needs no bundled database, `.tools/`, pre-existing virtual environment,
other WeFiles folder, or Supabase account. Dependencies, the environment template,
setup helper, migrations, design assets and Compose definition are versioned.

### Stop and start again

Press **Ctrl+C** to stop Django, then run:

```bash
docker compose stop db
```

On the next run, start the database and Django again. In PowerShell:

```powershell
docker compose up -d --wait db
.\.venv\Scripts\python.exe manage.py runserver
```

On macOS/Linux, replace the Python path with `.venv/bin/python`. Your `.env`,
accounts, database records and uploads persist between restarts. After pulling
changes with new migrations, run `manage.py migrate` before starting Django.

To test the Admin role, register another account, stop Django, then use the same
virtual environment's Python in the same repository:

```powershell
.\.venv\Scripts\python.exe manage.py promote_workspace_admin YOUR_USERNAME
```

Start Django again and sign in as that account. Admin is a workspace role;
Django maintenance staff permissions are managed separately.

### Use existing PostgreSQL or Supabase instead of Docker

Install PostgreSQL and create a dedicated login/database, or create a new
Supabase project. For a new native PostgreSQL instance, run these statements as
its administrator in `psql` or pgAdmin:

```sql
CREATE ROLE wefiles WITH LOGIN PASSWORD 'choose-your-local-password' CREATEDB;
CREATE DATABASE wefiles OWNER wefiles;
```

After installing the Python requirements, choose that connection during initial
configuration (PowerShell example):

```powershell
.\.venv\Scripts\python.exe scripts\configure_local.py --database-url "postgresql://wefiles:choose-your-local-password@127.0.0.1:5432/wefiles"
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py runserver
```

For Supabase, use the PostgreSQL **Session pooler** connection string from its
Connect panel. URL-encode special password characters. There is no SQLite
fallback. If `.env` already selects another database, edit `DATABASE_URL` there
explicitly; the setup helper does not replace an existing selection. Do not
reuse the original WeFiles database because its user schema/migrations differ.

### Setup troubleshooting

- **Docker is unavailable or cannot connect:** install/start Docker, verify
  `docker compose version`, and retry; or use the native PostgreSQL option.
- **Port 55432 is occupied:** choose another unused `POSTGRES_PORT` in `.env` and
  update the port in `DATABASE_URL` to match before starting the database.
- **Existing database rejects a changed password:** initialization credentials
  apply when a Docker volume is first created. Keep the original `.env` password
  for that volume, or change the PostgreSQL role password explicitly.
- **Old terminal settings override `.env`:** environment variables take priority.
  Open a fresh terminal after changing configuration, and avoid reusing the old
  temporary `wefiles_test`/port-55439 settings.
- **Python is not found:** install Python first. Use `py -3` on Windows and
  `python3` on macOS/Linux to create the virtual environment. Minimal Linux
  installations may also require their distribution's `python3-venv` package.

See [setup and deployment](docs/SETUP.md) for hosted Supabase storage and Render
configuration. Local startup does not create or deploy cloud resources.

## Tests

Run the setup helper regression checks and database-independent Django checks
from the repository root (PowerShell):

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s scripts -p test_configure_local.py
.\.venv\Scripts\python.exe manage.py test accounts.tests.test_registration accounts.tests.test_sessions accounts.tests.test_roles accounts.tests.test_profiles vault.tests vault.tests_deployment --settings=config.test_settings
.\.venv\Scripts\python.exe manage.py check --settings=config.test_settings
```

On macOS/Linux, use `.venv/bin/python` for the same commands.

For the complete journey suite, set `TEST_DATABASE_URL` to a separate disposable
PostgreSQL database/login you created. Local tests create/drop a `test_` database,
so the test login needs `CREATEDB`. Substitute your test connection below:

```powershell
$env:TEST_DATABASE_URL = 'postgresql://test_user:URL_ENCODED_TEST_PASSWORD@127.0.0.1:5432/wefiles_test'
.\.venv\Scripts\python.exe manage.py test --settings=config.test_settings --parallel 1
```

For a disposable Supabase test project, see [SETUP](docs/SETUP.md): its test
runner reuses and flushes that project's tables and requires explicit opt-in.
GitHub Actions runs the suite with isolated PostgreSQL and separately exercises
the generated `.env`, Compose startup and migrations from a clean checkout.

## Render preparation

[render.yaml](render.yaml), [build.sh](build.sh), and [start.sh](start.sh) prepare
static collection, HTTPS/proxy settings, private Supabase Storage, migrations,
Gunicorn and a database health check. Automatic deployment is disabled.
Creating a Render Blueprint still causes its first deployment; do this only
when the remaining setup is ready. No Render service was created here.

See [setup and deployment](docs/SETUP.md),
[requirements status](docs/REQUIREMENTS.md),
[branch/PR workflow](docs/GITHUB_WORKFLOW.md), and [verification](VERIFICATION.md).
The supplied report template is retained in `docs/`; the filled report stays a
**draft**, with final identity, screenshots, test accounts, PR links and hosted
verification pending. Its final required filename is
`WeFiles-Lastname-Firstname-Section-PD2.pdf`.
