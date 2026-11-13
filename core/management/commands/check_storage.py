"""Explicit operator smoke check; no public storage-test HTTP endpoint."""

import uuid

from botocore.exceptions import BotoCoreError, ClientError
from django.core.exceptions import ImproperlyConfigured
from django.core.files.base import ContentFile
from django.core.files.storage import storages
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Save/read/delete one disposable object in the configured private Supabase bucket."

    def handle(self, *args, **options):
        try:
            storage = storages["default"]
        except ImproperlyConfigured as exc:
            raise CommandError(str(exc)) from None

        name = f"_checks/{uuid.uuid4().hex}.txt"
        payload = b"WeFiles private storage smoke check.\n"
        try:
            name = storage.save(name, ContentFile(payload))
            with storage.open(name, "rb") as stored:
                if stored.read() != payload:
                    raise CommandError("Storage returned unexpected bytes.")
        except (BotoCoreError, ClientError, OSError):
            raise CommandError(
                "Storage check failed. Verify the private bucket, endpoint, region and S3 keys."
            ) from None
        finally:
            try:
                storage.delete(name)
            except (BotoCoreError, ClientError, OSError):
                raise CommandError(
                    f"Storage cleanup failed. Remove the disposable object {name} and retry."
                ) from None
        self.stdout.write(self.style.SUCCESS("Private Storage save/read/delete check passed."))
