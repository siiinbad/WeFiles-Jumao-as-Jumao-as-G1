# WeFiles: four-day build from scratch

Updated November 13, 2026 (Asia/Manila). This replaces the upgrade roadmap.
Start from an empty Django project; do not copy the completed app into the
first commit. Day 1-A is foundation commit `127ae1e` on `main`. Day 1-B's
deployment code is implemented and tested locally, ready for its own commit.
Live Supabase migrations, Storage access and Render deployment acceptance remain
pending private provider configuration. No later session has been implemented.
See [verification evidence](verification.md).

## Commit calendar

The schedule starts today, **November 13, 2026**, in **Asia/Manila (UTC+08:00)**.

| Date | Morning commit | Evening commit |
| --- | --- | --- |
| November 13, 2026 | Day 1-A | Day 1-B |
| November 14, 2026 | Day 2-A | Day 2-B |
| November 15, 2026 | Day 3-A | Day 3-B |
| November 16, 2026 | Day 4-A | Day 4-B |

Commit commands use `TZ=Asia/Manila` so Git records the actual commit time with
the local +08:00 offset. These are planned dates; existing commit timestamps
are unchanged. Each commit is created when its session is completed.

## Scope and preservation

Eight genuine sessions: Session A in the morning and Session B in the evening,
each 1–2 hours and one working capability per commit. The deliverable is a
private file-vault MVP: administrator-provisioned member accounts, sign-in/out,
own-file upload/list/download, metadata editing and owner-only deletion, hosted
on Render with Supabase PostgreSQL and private Storage.

Registration/verification/approval, shared folders, favorites, search/filter/
pagination, chat, notifications, role-management screens and reports are later
milestones. Rebuilding the full existing product cannot fit eight small
sessions. The new MVP uses owner permissions and Django admin; it does not yet
reproduce the old shared-workspace permission model.

Keep the old inner `WeFiles/` Git repository, history, database, uploads and
private .env intact. Create a separate empty `../WeFiles-fresh/` directory
relative to that Git root, within the shared workspace, with its own Git
repository and a NEW Supabase project. Never reset old history or run new
initial migrations against the old database. The
old audit and upgrade proposal in the sibling WeFiles/docs directory is historical
reference only; its 67 tests and 98% coverage do not verify this fresh build.

The configured fresh remote is `siiinbad/WeFiles-Jumao-as-Jumao-as-G1`.
Confirm that it is Public. The original app remains in its separate directory;
only the new foundation belongs on this remote's main branch. Local folder and
remote names may differ. Keep real commit timestamps and add one session at a time.

## Foundation and provider setup

```text
WeFiles-fresh/                  New Git root, no extra project wrapper
  manage.py
  config/                      settings.py, test_settings.py, urls.py, WSGI/ASGI
  accounts/                    Minimal custom User, authentication
  core/                        Landing/health/privacy, storage helper, tests/
  vault/                       Added with uploads: model/forms/services/views
  templates/                   base.html, feature pages, error pages
  static/css/app.css           Small responsive stylesheet
  requirements.txt .env.example .gitignore
  build.sh render.yaml         Added Day 1-B
  README.md docs/
```

Use Django templates, class-based page views, Django forms, template inheritance,
CSRF and POST mutations. Create a minimal AbstractUser subclass BEFORE the first
migration. Members initially use username/password sign-in; administrators
create their accounts through Django admin. Add validation and meaningful
permission tests alongside each feature instead of deferring correctness.

The first two commits prepare deployment:

1. **Django + Supabase foundation.** Load .env through python-dotenv with
   override=False. Require SECRET_KEY and DATABASE_URL. Parse with
   dj-database-url, require SSL and reject non-PostgreSQL engines. No SQLite
   fallback in application, test settings or CI. Read DEBUG, ALLOWED_HOSTS and
   CSRF_TRUSTED_ORIGINS from the environment; force DEBUG=False on Render.
   Automatically allow RENDER_EXTERNAL_HOSTNAME and its HTTPS origin. Apply
   secure cookies/HTTPS redirects/proxy handling in production.
2. **Render runtime.** Add Gunicorn, build.sh and render.yaml; configure
   WhiteNoise after SecurityMiddleware, STATIC_ROOT and
   STORAGES['staticfiles']=CompressedManifestStaticFilesStorage. Configure
   STORAGES['default'] for the private Supabase S3 bucket using django-storages,
   path-style addressing and server-only keys. Durable files never use Render's
   filesystem; no public media route. Verify the empty app on Render before
   adding member features.

Use Supabase's **Session pooler**, normally port **5432**, rather than its
IPv6-only direct database host, which Render may not reach. Copy the exact
pooler host/user from Connect and URL-encode the password. Session mode uses
CONN_MAX_AGE=60 with health checks. Port **6543**, or an explicit transaction
mode flag, forces CONN_MAX_AGE=0 and DISABLE_SERVER_SIDE_CURSORS=True. See
[Supabase connections](https://supabase.com/docs/guides/database/connecting-to-postgres)
and [Django cursor guidance](https://docs.djangoproject.com/en/5.2/ref/databases/#transaction-pooling-and-server-side-cursors).

Proposed pins, to install and verify during execution:

```text
Django==5.2.19
gunicorn==26.2.0
whitenoise==6.12.0
psycopg2-binary==2.9.13
dj-database-url==3.1.2
python-dotenv==1.2.4
django-storages==1.14.6
boto3==1.44.1
```

The first six are Day 1-A dependencies; the Storage packages join Day 1-B.
Published pins are not a claimed successful installation. Django's patch
selection follows the [official release listing](https://www.djangoproject.com/download/).

### Environment table for .env.example and README

| Variable | Placeholder/purpose |
| --- | --- |
| SECRET_KEY | Blank example; generate an independent random key privately |
| DEBUG | True locally; False on Render |
| DATABASE_URL | `postgresql://postgres.PROJECT_REF:URL_ENCODED_PASSWORD@POOLER_HOST:5432/postgres?sslmode=require` |
| DATABASE_POOL_MODE | session, or transaction for safe pooler overrides |
| ALLOWED_HOSTS | localhost,127.0.0.1 locally; custom deployment hosts if needed |
| CSRF_TRUSTED_ORIGINS | Comma-separated origins; add Render HTTPS origin automatically |
| RENDER_EXTERNAL_HOSTNAME | Supplied automatically by Render |
| TRUST_PROXY_HTTPS | False locally; True behind Render's HTTPS proxy |
| SUPABASE_S3_ENDPOINT_URL | Dashboard S3 endpoint including /storage/v1/s3 |
| SUPABASE_S3_REGION | Dashboard project region |
| SUPABASE_STORAGE_BUCKET | Private bucket name, e.g. wefiles-private |
| SUPABASE_S3_ACCESS_KEY_ID | Blank example; server-only credential |
| SUPABASE_S3_SECRET_ACCESS_KEY | Blank example; server-only credential |
| TEST_DATABASE_URL | Separate disposable Supabase test project; never app DB |
| MAX_UPLOAD_BYTES | e.g. 10485760; align with Supabase limits |
| PRIVACY_CONTACT | Actual operator contact before inviting members |
| TIME_ZONE | Asia/Manila |

Ignore .env, private .env.* variants (except .env.example), venv/, .venv/,
__pycache__/, *.pyc, db.sqlite3, staticfiles/, media/ and generated caches.
If a real secret is ever committed, rotate it immediately.

### Supabase → local migration → Render

1. Create NEW Supabase application and disposable test projects, separate from
   the existing app. Copy **Connect → Session pooler** into private .env;
   require SSL. Day 1-A supplies exact scaffold/setup commands and a safe
   private secret-generation helper. Never overwrite an existing private .env.
2. After creating the custom User and its initial migration, run:

```bash
python manage.py check
python manage.py migrate --plan
python manage.py migrate --noinput
python manage.py createsuperuser
python manage.py runserver
```

3. Create a private Storage bucket and generate server-side S3 keys. Copy
   endpoint/region/keys into local and Render environments; do not expose keys
   to templates or browsers. Supabase S3 keys bypass RLS, so Django must enforce
   ownership. See [S3 authentication](https://supabase.com/docs/guides/storage/s3/authentication).
4. Create the new Public GitHub repository and configure the fresh repository's
   origin. Day 1-B provides a Render Blueprint or these exact dashboard values:

| Render setting | Value |
| --- | --- |
| Runtime | Python, matching the verified local runtime |
| Root Directory | Blank; fresh remote root contains manage.py |
| Build Command | bash build.sh |
| Start Command | gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --threads 2 --timeout 120 |
| Health Check | /health/ready/ |
| Environment | SECRET_KEY, DATABASE_URL, DEBUG=False, TRUST_PROXY_HTTPS=True, Storage variables |
| Database resource | None on Render; external Supabase PostgreSQL only |

   build.sh fails fast and runs pip install -r requirements.txt, collectstatic
   --noinput, then migrate --noinput. Never create demo/admin passwords during
   builds. See [Render's Django guide](https://render.com/docs/deploy-django).
5. Verify landing/readiness/hashed static assets first; recheck after later
   sessions. Once uploads exist, verify bytes survive restart/redeploy and
   unauthorized members cannot read them. Publish actual storage/provider,
   retention and contact information in the privacy page.
6. Tests require TEST_DATABASE_URL selecting an isolated Supabase project and
   must reject the normal application database. If CREATE DATABASE is denied,
   use TEST['NAME'] for that existing disposable database and --keepdb.
   Serialize runs. Use temporary storage/mocks for failure tests and disposable
   objects for real Storage smoke checks; no SQLite testing shortcut.

## Four-day roadmap

Each row is one capability and one commit. Day 1-A is runnable from a fresh
environment; Day 1-B establishes the first live Render deploy. Later sessions
keep it deployable. Basic responsive markup, validations and tests accompany
their owning feature. All paths below are relative to the NEW Git root.

| Session | Feature goal | Files to create/modify | Model/migration | Acceptance check | Commit message |
| --- | --- | --- | --- | --- | --- |
| Day 1-A · morning | Bootstrap an empty Django app using SSL Supabase PostgreSQL. | manage.py; config/{settings,test_settings,urls,wsgi,asgi}.py; accounts/{apps,models,admin}.py; accounts/migrations/0001_initial.py; core/{apps,views,urls,tests/}; templates/{base.html,core/home.html}; static/css/app.css; requirements.txt; scripts/configure_local.py; .env.example; .gitignore; README.md; package initializers | New minimal accounts.User; apply its committed initial migration and Django built-in migrations. | Fresh install/homepage/admin work; migrations apply to NEW Supabase; missing/SQLite URL fails; SSL/pool settings correct. | chore: bootstrap Django with Supabase PostgreSQL |
| Day 1-B · evening | Deploy the foundation with private persistent-storage configuration. | build.sh; render.yaml; .python-version; requirements.txt; config/settings.py; core/{storage,views,urls}.py; core/management/commands/check_storage.py and initializers; core/tests/{test_deployment,test_storage}.py; .env.example; README.md; docs/{operations,verification,PROGRESSIVE_PLAN}.md | None. | Local tests/security/static checks pass; then verify real Render build/migrations, HTTPS landing/readiness/CSS and private Storage save/read/delete using configured providers. | chore: deploy Django foundation on Render |
| Day 2-A · morning | Let administrator-provisioned members sign in and out. | accounts/{urls,views,tests}.py; config/{settings,urls}.py; templates/accounts/login.html; templates/base.html | None. | Correct login succeeds; bad credentials fail generically; unsafe next redirect rejected; logout requires POST/CSRF. | feat: add member sign-in and sign-out |
| Day 2-B · evening | Upload files into a member's private vault. | vault/{apps,models,forms,services,views,urls,tests}.py and initializers; vault/migrations/0001_initial.py; templates/vault/{list,upload}.html; templates/core/privacy.html; core/{views,urls}.py; config/{settings,urls}.py; templates/base.html | New File: UUID, owner FK, randomized private blob, display name, description, size and timestamps. | Valid upload appears in own-file receipt/list; invalid size/name/description rejected before storage save; other users cannot list it; failed DB save compensates the object. | feat: upload files to a private member vault |
| Day 3-A · morning | Download owned files securely. | vault/{views,urls,tests}.py; templates/vault/list.html | None. | Owner gets original bytes as attachment; another member gets 404; anonymous visitor goes to login; provider failures produce safe feedback. | feat: download owned files securely |
| Day 3-B · evening | Edit owned file display metadata. | vault/{forms,services,views,urls,tests}.py; templates/vault/{edit,list}.html | None. | Owner changes name/description; invalid values fail; another user cannot GET/POST the editor; blob key and bytes unchanged. | feat: edit owned file metadata |
| Day 4-A · morning | Delete owned files with retryable object cleanup. | vault/{models,services,views,urls,tests}.py; vault/migrations/0002_storage_deletion_job.py; vault/management/commands/process_storage_deletions.py and initializers; templates/vault/{confirm_delete,list}.html; render.yaml; README.md | New StorageDeletionJob with unique object key and bounded retry state; queue atomically with file removal. | GET never deletes; owner-confirmed POST removes metadata; unauthorized POST denied; provider failure leaves a retry job; command later completes cleanup. | feat: delete owned files with retryable cleanup |
| Day 4-B · evening | Verify and document the complete MVP release. | core/tests/test_deployment.py; .github/workflows/tests.yml; README.md; docs/{verification,operations,PROGRESSIVE_PLAN}.md | None. | Isolated Supabase suite, migration-drift/deploy/static checks pass; live CRUD/auth/restart persistence verified; schedules, monitoring and backup/restore evidence or limits recorded. | test: verify the Render file-vault release |

Deletion scheduling belongs to deletion correctness: configure its cron/worker
with explicit production host/origin and the same Supabase settings. Confirm
hosted job costs before creating services. Do not claim alerts, backups,
restores or a live deployment without observing them. Final README includes
setup, env table, Supabase/Render steps and feature progress checklist.

### Exact Git commands for each session

Run inside the FRESH repository after acceptance checks and staged-diff review.
Initialize its main branch and configure its NEW origin during Day 1-A.

**Day 1-A**

```bash
git add manage.py config accounts core templates static scripts docs requirements.txt requirements-dev.txt pyproject.toml .env.example .gitignore README.md
TZ=Asia/Manila git commit -m "chore: bootstrap Django with Supabase PostgreSQL"
git push -u origin main
```

**Day 1-B**

```bash
git add .env.example .python-version build.sh render.yaml requirements.txt config/settings.py core/storage.py core/views.py core/urls.py core/management core/tests/test_deployment.py core/tests/test_storage.py README.md docs
TZ=Asia/Manila git commit -m "chore: deploy Django foundation on Render"
git push origin main
```

**Day 2-A**

```bash
git add accounts/urls.py accounts/views.py accounts/tests.py config/settings.py config/urls.py templates/accounts/login.html templates/base.html
TZ=Asia/Manila git commit -m "feat: add member sign-in and sign-out"
git push origin main
```

**Day 2-B**

```bash
git add vault templates/vault/list.html templates/vault/upload.html templates/core/privacy.html core/views.py core/urls.py config/settings.py config/urls.py templates/base.html
TZ=Asia/Manila git commit -m "feat: upload files to a private member vault"
git push origin main
```

**Day 3-A**

```bash
git add vault/views.py vault/urls.py vault/tests.py templates/vault/list.html
TZ=Asia/Manila git commit -m "feat: download owned files securely"
git push origin main
```

**Day 3-B**

```bash
git add vault/forms.py vault/services.py vault/views.py vault/urls.py vault/tests.py templates/vault/edit.html templates/vault/list.html
TZ=Asia/Manila git commit -m "feat: edit owned file metadata"
git push origin main
```

**Day 4-A**

```bash
git add vault/models.py vault/services.py vault/views.py vault/urls.py vault/tests.py vault/migrations/0002_storage_deletion_job.py vault/management templates/vault/confirm_delete.html templates/vault/list.html render.yaml README.md
TZ=Asia/Manila git commit -m "feat: delete owned files with retryable cleanup"
git push origin main
```

**Day 4-B**

```bash
git add core/tests/test_deployment.py .github/workflows/tests.yml README.md docs/verification.md docs/operations.md docs/PROGRESSIVE_PLAN.md
TZ=Asia/Manila git commit -m "test: verify the Render file-vault release"
git push origin main
```

## Execution contract

Day 1-B's deployment code is prepared; live provider checks remain pending.
Wait for `Next` or `Day 2-A` before implementing member sign-in. Implement
only the requested session, with full file
contents for new files, clear diffs for later edits, its acceptance check and
single commit command. Explain the code as a mentor without jumping to the
finished application. Keep secrets external, commit genuine migrations, and
preserve the old project. The complete app will grow through real sessions,
not a bulk rewrite disguised as progress.
