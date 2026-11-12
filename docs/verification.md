# Fresh foundation verification

Verified November 13, 2026 (Asia/Manila), using Python 3.14.10 and Django 5.2.19.
This evidence applies to the NEW WeFiles-fresh project, not the old app.

| Check | Result |
| --- | --- |
| Pinned requirements installation | Passed in this project's independent .venv, including psycopg2-binary. |
| pip check | No broken requirements. |
| Foundation tests | 18 passed: environment validation, SSL/pooling, Render host/debug behavior, test-project isolation, landing page and security headers. |
| Django system checks | No issues. |
| Production check --deploy | No issues, including warning-level checks, with ephemeral test configuration. |
| User migration | accounts/0001_initial.py generated from the new minimal custom User. |
| Model/migration drift | No changes detected; checked offline without querying database history. |
| Production collectstatic | Compressed manifest generation passed in temporary storage. |
| Production HTTPS Django-client checks | Landing page, hashed CSS and admin login returned HTTP 200; HTTP redirected to HTTPS. |
| Ruff | Lint and formatting passed. |
| Local configuration helper | Generated a private secret without printing it; repeat run preserved file content; .env permissions are 0600. |
| Git exclusions | .env, .venv/, staticfiles/ and media/ are ignored. |

No live Supabase credentials were supplied. Database configuration and
no-database tests used clearly synthetic PostgreSQL URLs with no real password.
The test runner skipped the unused database; it did not create or use SQLite.
Production static/client checks used a temporary secret and directory. Neither
was saved in source or deployed.

Live Supabase connectivity, applying migrations, creating users and database-
backed admin authentication have NOT been verified. Migration generation/drift
checks skipped the database-history lookup; they do not establish that a remote
database is ready. Set the NEW project's real DATABASE_URL privately in .env,
then follow README's check/migrate/admin acceptance steps.

No Render service, Storage bucket, monitoring, backups, or hosted schedules were
created. There is no upload/file feature yet. There are no commits or pushes;
the user will configure Git identity. The old application's tracked source and
history were not modified by this foundation work.
