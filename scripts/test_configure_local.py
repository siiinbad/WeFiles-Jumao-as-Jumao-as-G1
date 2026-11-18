import tempfile
import unittest
from pathlib import Path
from urllib.parse import unquote, urlsplit

from dotenv import dotenv_values, set_key
from configure_local import configure_local


class ConfigureLocalTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.env_path = Path(self.directory.name) / ".env"

    def test_new_checkout_gets_matching_persistent_secrets_and_database_url(self):
        configure_local(self.env_path)
        values = dotenv_values(self.env_path)
        parsed = urlsplit(values["DATABASE_URL"])
        self.assertGreaterEqual(len(values["SECRET_KEY"]), 50)
        self.assertGreaterEqual(len(values["POSTGRES_PASSWORD"]), 32)
        self.assertEqual(parsed.hostname, "127.0.0.1")
        self.assertEqual(str(parsed.port), values["POSTGRES_PORT"])
        self.assertEqual(unquote(parsed.username), values["POSTGRES_USER"])
        self.assertEqual(unquote(parsed.password), values["POSTGRES_PASSWORD"])
        self.assertEqual(unquote(parsed.path[1:]), values["POSTGRES_DB"])
        self.assertEqual(values["DJANGO_DEBUG"], "True")
        self.assertEqual(values["PRIVATE_STORAGE_BACKEND"], "local")

    def test_running_again_preserves_the_file_and_session_secret(self):
        configure_local(self.env_path)
        original = self.env_path.read_bytes()
        self.assertEqual(configure_local(self.env_path), [])
        self.assertEqual(self.env_path.read_bytes(), original)

    def test_different_checkouts_receive_different_secrets(self):
        configure_local(self.env_path)
        second = self.env_path.with_name("another.env")
        configure_local(second)
        first_values, second_values = dotenv_values(self.env_path), dotenv_values(second)
        self.assertNotEqual(first_values["SECRET_KEY"], second_values["SECRET_KEY"])
        self.assertNotEqual(first_values["POSTGRES_PASSWORD"], second_values["POSTGRES_PASSWORD"])

    def test_existing_custom_values_and_comments_are_preserved(self):
        configure_local(self.env_path)
        set_key(str(self.env_path), "DJANGO_DEBUG", "False")
        set_key(str(self.env_path), "PRIVATE_STORAGE_BACKEND", "supabase")
        with self.env_path.open("a", encoding="utf-8") as target:
            target.write("# Keep my settings\nCUSTOM_SETTING=kept\n")
        original = self.env_path.read_bytes()
        configure_local(self.env_path)
        self.assertEqual(self.env_path.read_bytes(), original)

    def test_existing_password_is_url_encoded_in_generated_database_url(self):
        self.env_path.write_text("POSTGRES_PASSWORD='local password@?#/'\nPOSTGRES_PORT=55499\n", encoding="utf-8")
        configure_local(self.env_path)
        values = dotenv_values(self.env_path)
        parsed = urlsplit(values["DATABASE_URL"])
        self.assertEqual(unquote(parsed.password), "local password@?#/")
        self.assertEqual(parsed.port, 55499)

    def test_existing_database_selection_is_not_replaced(self):
        custom = "postgresql://member:encoded-password@db.project.supabase.co:5432/postgres"
        configure_local(self.env_path, database_url=custom)
        with self.assertRaisesRegex(ValueError, "Existing DATABASE_URL was preserved"):
            configure_local(self.env_path, database_url="postgresql://other:password@127.0.0.1:5432/other")
        self.assertEqual(dotenv_values(self.env_path)["DATABASE_URL"], custom)

    def test_invalid_database_url_does_not_create_an_env_file(self):
        for url in ("sqlite:///db.sqlite3", "postgresql://missing-password@localhost/app", "postgresql://u:p@localhost/app#fragment"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                configure_local(self.env_path, database_url=url)
            self.assertFalse(self.env_path.exists())

    def test_invalid_existing_port_or_secret_does_not_change_existing_file(self):
        for value in ("POSTGRES_PORT=99999\n", "SECRET_KEY=too-short\n"):
            self.env_path.write_text(value, encoding="utf-8")
            with self.assertRaises(ValueError):
                configure_local(self.env_path)
            self.assertEqual(self.env_path.read_text(encoding="utf-8"), value)


if __name__ == "__main__":
    unittest.main()
