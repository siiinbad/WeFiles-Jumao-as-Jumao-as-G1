import logging
from unittest.mock import patch

from django.conf import settings
from django.db import OperationalError
from django.test import SimpleTestCase, override_settings
from django.urls import reverse


@override_settings(
    ALLOWED_HOSTS=["testserver"],
    MIDDLEWARE=[
        item for item in settings.MIDDLEWARE if item != "whitenoise.middleware.WhiteNoiseMiddleware"
    ],
)
class ReadinessTests(SimpleTestCase):
    def test_successful_probe_returns_minimal_uncached_status(self):
        with patch("core.views.connection") as database:
            cursor = database.cursor.return_value.__enter__.return_value
            response = self.client.get(reverse("core:ready"), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ready"})
        self.assertEqual(response["Cache-Control"], "no-store")
        cursor.execute.assert_called_once_with("SELECT 1")

    def test_failed_probe_exposes_no_connection_or_exception_details(self):
        private_detail = "TEST_PASSWORD_DO_NOT_EXPOSE"
        with (
            patch("core.views.connection") as database,
            self.assertLogs("core.views", level=logging.WARNING) as logs,
        ):
            database.cursor.side_effect = OperationalError(private_detail)
            response = self.client.get(reverse("core:ready"), secure=True)
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json(), {"status": "unavailable"})
        self.assertEqual(response["Cache-Control"], "no-store")
        self.assertNotIn(private_detail, response.content.decode())
        self.assertNotIn(private_detail, " ".join(logs.output))

    @override_settings(SECURE_SSL_REDIRECT=True)
    def test_internal_http_probe_cannot_report_a_redirect_as_healthy(self):
        with (
            patch("core.views.connection") as database,
            self.assertLogs("core.views", level=logging.WARNING),
        ):
            database.cursor.side_effect = OperationalError("TEST_OUTAGE")
            response = self.client.get(reverse("core:ready"))
        self.assertEqual(response.status_code, 503)
        self.assertNotIn("Location", response)

    def test_head_probe_checks_database_and_mutations_are_rejected(self):
        with patch("core.views.connection") as database:
            head = self.client.head(reverse("core:ready"), secure=True)
            rejected = self.client.post(reverse("core:ready"), secure=True)
        self.assertEqual(head.status_code, 200)
        self.assertEqual(head.content, b"")
        self.assertEqual(rejected.status_code, 405)
        database.cursor.assert_called_once()


class BuildScriptTests(SimpleTestCase):
    def test_failed_static_collection_stops_before_migrations(self):
        """Execute the real build script with a controlled Python command."""
        import os
        import subprocess
        import tempfile
        from pathlib import Path

        from django.conf import settings

        with tempfile.TemporaryDirectory(prefix="wefiles-build-test-") as directory:
            directory = Path(directory)
            log = directory / "commands.log"
            fake_python = directory / "python"
            fake_python.write_text(
                '#!/bin/sh\nprintf "%s\\n" "$*" >> "$WEFILES_BUILD_TEST_LOG"\n'
                'if [ "$2" = "collectstatic" ]; then exit 1; fi\n'
            )
            fake_python.chmod(0o700)
            environment = os.environ.copy()
            environment["PATH"] = f"{directory}:{environment['PATH']}"
            environment["WEFILES_BUILD_TEST_LOG"] = str(log)
            result = subprocess.run(
                ["bash", str(settings.BASE_DIR / "build.sh")],
                cwd=directory,
                env=environment,
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )
            commands = log.read_text().splitlines()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(commands[0], "-m pip install -r requirements.txt")
        self.assertIn("manage.py collectstatic --noinput", commands)
        self.assertFalse(any("migrate" in command for command in commands))
