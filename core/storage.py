"""Supabase S3 storage: server-only access and no generated object URLs."""

from urllib.parse import urlsplit

from boto3.s3.transfer import TransferConfig
from botocore.config import Config
from django.core.exceptions import ImproperlyConfigured
from storages.backends.s3 import S3Storage


class PrivateSupabaseStorage(S3Storage):
    def __init__(self, **options):
        required_options = {
            "endpoint_url": "SUPABASE_S3_ENDPOINT_URL",
            "region_name": "SUPABASE_S3_REGION",
            "bucket_name": "SUPABASE_STORAGE_BUCKET",
            "access_key": "SUPABASE_S3_ACCESS_KEY_ID",
            "secret_key": "SUPABASE_S3_SECRET_ACCESS_KEY",
        }
        for option, variable in required_options.items():
            if not options.get(option):
                raise ImproperlyConfigured(f"Set {variable} before using private Supabase Storage.")
        try:
            endpoint = urlsplit(options["endpoint_url"])
            valid_endpoint = (
                endpoint.scheme == "https"
                and (endpoint.hostname or "").endswith(".supabase.co")
                and endpoint.port in (None, 443)
                and endpoint.path.rstrip("/") == "/storage/v1/s3"
                and not endpoint.username
                and not endpoint.password
                and not endpoint.query
                and not endpoint.fragment
            )
        except ValueError:
            valid_endpoint = False
        if not valid_endpoint:
            raise ImproperlyConfigured(
                "SUPABASE_S3_ENDPOINT_URL must be the HTTPS S3 endpoint copied from Supabase."
            )
        options.update(
            default_acl=None,  # Supabase does not support x-amz-acl; bucket must be private.
            custom_domain=None,
            querystring_auth=True,
            file_overwrite=False,
            object_parameters={"CacheControl": "private, no-store"},
            use_ssl=True,
            verify=True,
            max_memory_size=8 * 1024 * 1024,
            transfer_config=TransferConfig(use_threads=False),
            client_config=Config(
                signature_version="s3v4",
                s3={"addressing_style": "path"},
                connect_timeout=5,
                read_timeout=30,
                retries={"mode": "standard", "total_max_attempts": 2},
                request_checksum_calculation="when_required",
                response_checksum_validation="when_required",
            ),
        )
        super().__init__(**options)

    def url(self, name, parameters=None, expire=None, http_method=None):
        raise NotImplementedError("Private files must be served by an authorized Django view.")
