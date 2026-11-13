# Fresh foundation and Day 1-B verification

Verified November 13, 2026 (Asia/Manila), using Python 3.14.10 and Django 5.2.19.
This evidence applies to the NEW WeFiles-fresh project, not the old app.

| Check | Result |
| --- | --- |
| Pinned requirements installation | Passed in this project's independent .venv, including psycopg2-binary. |
| pip check | No broken requirements. |
| Foundation and deployment tests | 31 passed: original 18 plus readiness behavior, fail-fast build execution, private S3 adapter roundtrip, endpoint/credential validation and smoke-check cleanup/error paths. |
| Django system checks | No issues. |
| Production check --deploy | No issues, including warning-level checks, with ephemeral test configuration. |
| User migration | accounts/0001_initial.py generated from the new minimal custom User. |
| Model/migration drift | No changes detected; checked offline without querying database history. |
| Production collectstatic | Compressed manifest generation passed into ignored staticfiles/. |
| Production HTTPS Django-client checks | Landing page, hashed CSS and admin login returned HTTP 200; HTTP redirected to HTTPS; trusted forwarded HTTPS worked. |
| Readiness | Mocked database success returned 200; mocked outage returned 503 even on internal HTTP; no connection details exposed. |
| Gunicorn | check-config passed with production settings. |
| Storage adapter | Real django-storages/boto3 save/open/delete code passed against botocore's stubbed provider, including exact private upload parameters. No live S3 request was made. |
| Storage smoke command | In-memory save/read/delete passed; failures/mismatched bytes trigger cleanup; cleanup failure is reported safely. |
| Build script | bash syntax passed; executing its real shell script with a failing static command stopped before migrations. Full live build was not run. |
| Blueprint | YAML syntax and selected service/secret fields validated locally; Render's own API/dashboard validation remains pending. |
| Ruff | Lint and formatting passed. |
| Local configuration helper | Generated a private secret without printing it; repeat run preserved file content; .env permissions are 0600. |
| Git exclusions | .env, .venv/, staticfiles/ and media/ are ignored. |

No live Supabase credentials were supplied. Database configuration and
no-database tests used clearly synthetic PostgreSQL URLs with no real password.
The test runner skipped the unused database; it did not create or use SQLite.
Production static/client checks used a temporary process-only secret and
generated ignored local static assets. No secret was saved in source or deployed.

Live Supabase connectivity, applying migrations, creating users and database-
backed admin authentication have NOT been verified. Migration generation/drift
checks skipped the database-history lookup; they do not establish that a remote
database is ready. Set the NEW project's real DATABASE_URL privately in .env,
then follow README's check/migrate/admin acceptance steps.

Real bucket read/write/delete, private visibility and restart persistence have
NOT been verified. No Render service, Storage bucket, monitoring, backups, or
hosted schedules were created. There is no upload/file feature yet. The initial
foundation is commit 127ae1e; Day 1-B's changes are left uncommitted for review.
No commit or push was performed during Day 1-B. The old application's tracked
source and history were not modified by this work. Use the acceptance checklist
in [operations](operations.md) when provider credentials are available.
