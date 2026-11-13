# Day 1-B: Render and Supabase acceptance

The repository contains deployment code. A passing mocked test is not evidence
of a live service. Keep this checklist pending until the provider checks below
are actually observed.

## Configure providers

1. Use the NEW Supabase application's Session pooler URL, ordinarily port 5432,
   with SSL. URL-encode the database password. Copy its exact host/username;
   the IPv6 direct host can be unreachable from Render. Port 6543 forces
   zero connection lifetime and disabled server-side cursors in this app.
2. Apply migrations locally to the new project and create its first superuser.
   The Day 1-A custom User migration is preserved; Day 1-B adds no migrations.
3. Create a private Supabase bucket. Copy S3 endpoint, region, Access Key ID and
   Secret Access Key to the five .env.example variables. Do not expose these
   credentials to Git, browser templates, logs or public pages.
4. Run `python manage.py check_storage`. It uses one disposable random object,
   verifies the returned bytes and deletes it in a finally block. If cleanup
   fails, remove the reported `_checks/` key and investigate provider access.
5. Confirm private visibility in the dashboard and with an unauthenticated
   public-object request. A server's ability to read an object does not prove
   the bucket is private. Keep S3 credentials on the server; they bypass RLS.
6. Create the Render Blueprint/web service using README's exact settings. The
   Blueprint requests secrets without storing them in Git, uses a free Python
   web service, and creates no Render database, disk, cron or worker.
7. Supply an independent production SECRET_KEY of at least 50 characters and
   keep it stable. The Blueprint intentionally requests it rather than using
   Render's shorter generated-value example. Set DEBUG=False and enable the
   trusted proxy flag only behind Render. Python is pinned in .python-version.
8. Watch the build: pip install, deployment checks, collectstatic and migrate
   must all complete. Migration failure stops the build; never remove migration
   execution or switch to SQLite to conceal a configuration problem.

## Live acceptance checklist

- [ ] New Supabase database is reachable over SSL; current migrations applied.
- [ ] Private bucket is configured; server-side save/read/delete succeeds.
- [ ] Anonymous public object access is denied; bucket remains private.
- [ ] Render Blueprint passes provider validation and its build succeeds.
- [ ] / and /admin/login/ return HTTPS 200 and load hashed CSS.
- [ ] /health/ready/ returns 200 with `{"status": "ready"}` and no-store caching.
- [ ] An isolated outage test produces 503 rather than leaked connection text.
- [ ] Gunicorn starts on Render's assigned PORT; normal HTTP redirects to HTTPS.
- [ ] Restart/redeploy leaves existing disposable bucket bytes intact.
- [ ] Admin authentication works against the new database.

Use a disposable staging environment for fault tests. Do not break the live
database or publish a bucket while testing failure handling. There are no
member file screens yet; app-level upload/download/restart checks follow when
those features exist in Day 2 and Day 3.

## Ongoing operations

Keep a database backup and a separate copy of private object bytes; rehearse
restoring both into an isolated environment and document the resulting recovery
steps and retention period. Provider accounts, backup jobs, external uptime
checks/alerts and restore drills have not been configured by this session.
Monitor /health/ready/ and Render logs without recording credentials or request
bodies. Public health responses expose no database hostname or Storage details.

Use backward-compatible migrations during rolling releases. build.sh currently
runs migrate as requested; if moving it to a paid Render pre-deploy hook later,
remove it from build.sh so it runs once. Add cleanup schedules only when the
deletion outbox exists in Day 4-A. No new scheduled service is needed today.

References: [Render Django](https://render.com/docs/deploy-django),
[Blueprint settings](https://render.com/docs/blueprint-spec),
[Supabase S3 authentication](https://supabase.com/docs/guides/storage/s3/authentication),
[django-storages S3](https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html).
