from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Start with Django identity; extend it through future committed migrations."""
