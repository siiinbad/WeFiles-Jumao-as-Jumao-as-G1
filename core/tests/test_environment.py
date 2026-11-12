"""Configuration safety checks; these do not connect to Supabase."""

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from django.core.exceptions import ImproperlyConfigured

from config.environment import boolean, database_config, required, supabase_project

ROOT = Path(__file__).resolve().parents[2]
SESSION_URL = (
    "postgresql://postgres.exampleapp:NOT_A_REAL_PASSWORD"
    "@aws-0-example.pooler.supabase.com:5432/postgres"
)
TEST_URL = SESSION_URL.replace("exampleapp", "exampletest")


class EnvironmentTests(unittest.TestCase):
    def test_missing_values_fail_with_variable_name_only(self):
        with patch.dict(os.environ, {"DATABASE_URL": ""}):
            with self.assertRaisesRegex(ImproperlyConfigured, "Set DATABASE_URL"):
                required("DATABASE_URL")

    def test_boolean_settings_do_not_treat_false_as_truthy(self):
        for value, expected in [("False", False), ("0", False), ("True", True)]:
            with self.subTest(value=value), patch.dict(os.environ, {"DEBUG": value}):
                self.assertEqual(boolean("DEBUG"), expected)
        with patch.dict(os.environ, {"DEBUG": "perhaps"}):
            with self.assertRaises(ImproperlyConfigured):
                boolean("DEBUG")

    def test_session_pooler_requires_ssl_and_checks_connections(self):
        database = database_config(SESSION_URL + "?sslmode=disable")
        self.assertEqual(database["OPTIONS"]["sslmode"], "require")
        self.assertEqual(database["CONN_MAX_AGE"], 60)
        self.assertTrue(database["CONN_HEALTH_CHECKS"])
        self.assertFalse(database["DISABLE_SERVER_SIDE_CURSORS"])

    def test_transaction_port_disables_persistence_and_server_cursors(self):
        for mode in ("auto", "session", "transaction"):
            with self.subTest(mode=mode):
                database = database_config(SESSION_URL.replace(":5432/", ":6543/"), mode)
                self.assertEqual(database["CONN_MAX_AGE"], 0)
                self.assertTrue(database["DISABLE_SERVER_SIDE_CURSORS"])

    def test_explicit_transaction_mode_works_on_other_ports(self):
        database = database_config(SESSION_URL, "transaction")
        self.assertEqual(database["CONN_MAX_AGE"], 0)
        self.assertTrue(database["DISABLE_SERVER_SIDE_CURSORS"])

    def test_missing_sqlite_and_external_database_urls_are_rejected(self):
        for url in ("", "sqlite:///:memory:", "postgresql://user:password@localhost:5432/app"):
            with self.subTest(url=url), self.assertRaises(ImproperlyConfigured):
                database_config(url)

    def test_bad_url_never_exposes_its_password(self):
        password = "TEST_PASSWORD_DO_NOT_LOG"
        with self.assertRaises(ImproperlyConfigured) as raised:
            database_config(f"postgresql://user:{password}@invalid:not-a-port/app")
        self.assertNotIn(password, str(raised.exception))

    def test_url_requires_credentials_and_database(self):
        for url in (SESSION_URL.replace(":NOT_A_REAL_PASSWORD", ""), SESSION_URL.rsplit("/", 1)[0]):
            with self.subTest(url=url), self.assertRaises(ImproperlyConfigured):
                database_config(url)

    def test_pool_mode_typos_fail_clearly(self):
        with self.assertRaisesRegex(ImproperlyConfigured, "DATABASE_POOL_MODE"):
            database_config(SESSION_URL, "transacton")

    def test_test_isolation_identifies_same_project_across_endpoints(self):
        direct = "postgresql://postgres:NOT_A_REAL_PASSWORD@db.exampleapp.supabase.co:5432/postgres"
        self.assertEqual(
            supabase_project(database_config(SESSION_URL)),
            supabase_project(database_config(direct)),
        )


class SettingsTests(unittest.TestCase):
    def load_settings(self, module="config.settings", **overrides):
        environment = os.environ.copy()
        environment.update(
            {
                "SECRET_KEY": "TEST_ONLY_" + "x" * 64,
                "DATABASE_URL": SESSION_URL,
                "TEST_DATABASE_URL": TEST_URL,
                "DATABASE_POOL_MODE": "auto",
                "DEBUG": "False",
                "ALLOWED_HOSTS": "app.example.test",
                "CSRF_TRUSTED_ORIGINS": "",
                "RENDER_EXTERNAL_HOSTNAME": "",
                "RENDER": "false",
                "TRUST_PROXY_HTTPS": "False",
            }
        )
        environment.update(overrides)
        code = (
            "import importlib, json; "
            f"s = importlib.import_module({module!r}); "
            "print(json.dumps({'debug': s.DEBUG, 'hosts': s.ALLOWED_HOSTS, "
            "'origins': s.CSRF_TRUSTED_ORIGINS, 'database': s.DATABASES['default']['USER']}))"
        )
        return subprocess.run(
            [sys.executable, "-c", code],
            cwd=ROOT,
            env=environment,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )

    def test_render_disables_debug_and_adds_host_and_csrf_origin(self):
        result = self.load_settings(
            DEBUG="True", ALLOWED_HOSTS="", RENDER_EXTERNAL_HOSTNAME="fresh.example.onrender.com"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        settings = json.loads(result.stdout)
        self.assertFalse(settings["debug"])
        self.assertEqual(settings["hosts"], ["fresh.example.onrender.com"])
        self.assertIn("https://fresh.example.onrender.com", settings["origins"])

    def test_production_rejects_blank_or_short_secret(self):
        for secret in ("", "short"):
            with self.subTest(secret=secret):
                result = self.load_settings(SECRET_KEY=secret)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("SECRET_KEY", result.stderr)

    def test_production_rejects_wildcard_hosts_and_http_csrf_origin(self):
        for values in ({"ALLOWED_HOSTS": "*"}, {"CSRF_TRUSTED_ORIGINS": "http://app.example.test"}):
            with self.subTest(values=values):
                result = self.load_settings(**values)
                self.assertNotEqual(result.returncode, 0)

    def test_database_url_is_required(self):
        result = self.load_settings(DATABASE_URL="")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("DATABASE_URL", result.stderr)

    def test_test_settings_require_a_different_supabase_project(self):
        same_project = SESSION_URL.replace(":5432/", ":6543/")
        result = self.load_settings("config.test_settings", TEST_DATABASE_URL=same_project)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("separate disposable Supabase project", result.stderr)

    def test_test_settings_accept_only_the_explicit_disposable_project(self):
        result = self.load_settings("config.test_settings")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["database"], "postgres.exampletest")
