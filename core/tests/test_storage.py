from io import BytesIO, StringIO
from unittest.mock import MagicMock, Mock, patch

from botocore.exceptions import ClientError
from botocore.response import StreamingBody
from botocore.stub import ANY, Stubber
from django.core.exceptions import ImproperlyConfigured
from django.core.files.base import ContentFile
from django.core.files.storage import storages
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import SimpleTestCase, override_settings

from core.storage import PrivateSupabaseStorage

STORAGE_OPTIONS = {
    "endpoint_url": "https://exampleproject.storage.supabase.co/storage/v1/s3",
    "region_name": "ap-southeast-1",
    "bucket_name": "wefiles-test",
    "access_key": "TEST_ACCESS_KEY",
    "secret_key": "TEST_SECRET_NOT_REAL",
}


class PrivateStorageTests(SimpleTestCase):
    def test_missing_storage_config_never_falls_back_to_other_credentials(self):
        with patch("boto3.Session") as session:
            for option in STORAGE_OPTIONS:
                with self.subTest(option=option):
                    options = {**STORAGE_OPTIONS, option: ""}
                    with self.assertRaises(ImproperlyConfigured):
                        PrivateSupabaseStorage(**options)
            session.assert_not_called()

    def test_credentials_cannot_be_sent_to_http_or_external_endpoints(self):
        endpoints = [
            "http://exampleproject.supabase.co/storage/v1/s3",
            "https://example.com/storage/v1/s3",
            "https://exampleproject.supabase.co/incorrect-path",
            "https://exampleproject.supabase.co/storage/v1/s3?token=TEST",
            "https://user:TEST@exampleproject.supabase.co/storage/v1/s3",
        ]
        for endpoint in endpoints:
            with self.subTest(endpoint=endpoint), self.assertRaises(ImproperlyConfigured):
                PrivateSupabaseStorage(**{**STORAGE_OPTIONS, "endpoint_url": endpoint})

    def test_storage_never_generates_an_object_url(self):
        storage = PrivateSupabaseStorage(**STORAGE_OPTIONS)
        with self.assertRaisesRegex(NotImplementedError, "authorized Django view"):
            storage.url("objects/test.txt")

    def test_real_s3_adapter_saves_reads_and_deletes_with_stubbed_provider(self):
        storage = PrivateSupabaseStorage(**STORAGE_OPTIONS)
        client = storage.connection.meta.client
        payload = b"A disposable private file."
        key = "_checks/roundtrip.txt"
        parameters = {"Bucket": STORAGE_OPTIONS["bucket_name"], "Key": key}
        with Stubber(client) as stub:
            # File overwrite protection checks whether the random key exists.
            stub.add_client_error("head_object", service_error_code="404", http_status_code=404)
            stub.add_response(
                "put_object",
                {},
                {
                    **parameters,
                    "Body": ANY,
                    "ContentType": "text/plain",
                    "CacheControl": "private, no-store",
                },
            )
            stub.add_response("head_object", {"ContentLength": len(payload)})
            stub.add_response(
                "get_object",
                {
                    "Body": StreamingBody(BytesIO(payload), len(payload)),
                    "ContentLength": len(payload),
                },
            )
            stub.add_response("delete_object", {}, parameters)
            saved = storage.save(key, ContentFile(payload))
            with storage.open(saved, "rb") as stored:
                self.assertEqual(stored.read(), payload)
            storage.delete(saved)
            stub.assert_no_pending_responses()
        self.assertEqual(saved, key)


class StorageSmokeCommandTests(SimpleTestCase):
    @override_settings(
        STORAGES={"default": {"BACKEND": "django.core.files.storage.InMemoryStorage"}}
    )
    def test_smoke_check_leaves_no_disposable_object_behind(self):
        output = StringIO()
        call_command("check_storage", stdout=output)
        self.assertIn("save/read/delete check passed", output.getvalue())
        self.assertEqual(storages["default"].listdir("_checks"), ([], []))

    def test_provider_errors_are_safe_and_cleanup_is_attempted(self):
        storage = Mock()
        storage.save.side_effect = ClientError(
            {"Error": {"Code": "AccessDenied", "Message": "TEST_SECRET_DO_NOT_EXPOSE"}},
            "PutObject",
        )
        with (
            patch("core.management.commands.check_storage.storages", {"default": storage}),
            self.assertRaises(CommandError) as raised,
        ):
            call_command("check_storage")
        self.assertNotIn("TEST_SECRET_DO_NOT_EXPOSE", str(raised.exception))
        storage.delete.assert_called_once()

    def test_read_mismatch_fails_and_still_removes_the_disposable_object(self):
        storage = MagicMock()
        storage.save.return_value = "_checks/test.txt"
        storage.open.return_value.__enter__.return_value.read.return_value = b"wrong"
        with (
            patch("core.management.commands.check_storage.storages", {"default": storage}),
            self.assertRaisesRegex(CommandError, "unexpected bytes"),
        ):
            call_command("check_storage")
        storage.delete.assert_called_once_with("_checks/test.txt")

    def test_cleanup_failure_is_reported_without_provider_details(self):
        storage = MagicMock()
        storage.save.return_value = "_checks/test.txt"
        storage.open.return_value.__enter__.return_value.read.return_value = (
            b"WeFiles private storage smoke check.\n"
        )
        storage.delete.side_effect = ClientError(
            {"Error": {"Code": "AccessDenied", "Message": "TEST_SECRET_DO_NOT_EXPOSE"}},
            "DeleteObject",
        )
        with (
            patch("core.management.commands.check_storage.storages", {"default": storage}),
            self.assertRaisesRegex(CommandError, "Remove the disposable object") as raised,
        ):
            call_command("check_storage")
        self.assertNotIn("TEST_SECRET_DO_NOT_EXPOSE", str(raised.exception))
