import os
from urllib.parse import urlparse

from django.core.exceptions import ImproperlyConfigured

from .test import *  # noqa: F403


database = urlparse(os.environ.get("DATABASE_URL", ""))
if database.scheme not in {"postgres", "postgresql"} or not all(
    (
        database.path.lstrip("/"),
        database.username,
        database.password,
        database.hostname,
    )
):
    raise ImproperlyConfigured(
        "DATABASE_URL must be a complete PostgreSQL URL for PostgreSQL tests."
    )

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": database.path.lstrip("/"),
        "USER": database.username,
        "PASSWORD": database.password,
        "HOST": database.hostname,
        "PORT": database.port or 5432,
        # Match production connection reuse. A zero lifetime closes the
        # transactional TestCase connection when a streaming response emits
        # request_finished, leaving psycopg with a closed transaction handle.
        "CONN_MAX_AGE": 60,
        "CONN_HEALTH_CHECKS": True,
    }
}
