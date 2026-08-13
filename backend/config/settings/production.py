import os
import logging
from urllib.parse import urlparse
from django.core.exceptions import ImproperlyConfigured
from .base import *  # noqa: F403

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "")
if not SECRET_KEY or SECRET_KEY.startswith("replace-with-") or SECRET_KEY == "unsafe-development-only-key":
    raise ImproperlyConfigured("DJANGO_SECRET_KEY must be a strong deployment secret.")

database = urlparse(os.environ["DATABASE_URL"])
if database.scheme not in {"postgres", "postgresql"} or not all((database.path.lstrip("/"), database.username, database.password, database.hostname)):
    raise ImproperlyConfigured("DATABASE_URL must be a complete PostgreSQL URL.")
DATABASES = {"default": {"ENGINE": "django.db.backends.postgresql", "NAME": database.path.lstrip("/"), "USER": database.username, "PASSWORD": database.password, "HOST": database.hostname, "PORT": database.port or 5432, "CONN_MAX_AGE": int(os.getenv("DJANGO_DB_CONN_MAX_AGE", "60")), "CONN_HEALTH_CHECKS": True}}
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = os.getenv("DJANGO_SECURE_SSL_REDIRECT", "True").lower() == "true"
SECURE_HSTS_SECONDS = int(os.getenv("DJANGO_SECURE_HSTS_SECONDS", "31536000"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

if os.getenv("SENTRY_DSN"):
    try:
        import sentry_sdk
    except ImportError:
        pass
    else:
        from sentry_sdk.integrations.django import DjangoIntegration
        from sentry_sdk.integrations.logging import LoggingIntegration

        def scrub_sentry_event(event, hint):
            request_data = event.get("request", {})
            request_data.pop("data", None)
            request_data.pop("cookies", None)
            headers = request_data.get("headers", {})
            for name in tuple(headers):
                if name.lower() in {"authorization", "cookie", "x-csrftoken"}:
                    headers.pop(name, None)
            event.pop("user", None)
            return event

        sentry_sdk.init(
            dsn=os.environ["SENTRY_DSN"],
            environment=os.getenv("SENTRY_ENVIRONMENT", "production"),
            release=os.getenv("SENTRY_RELEASE") or None,
            traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0")),
            send_default_pii=False,
            before_send=scrub_sentry_event,
            integrations=[DjangoIntegration(), LoggingIntegration(level=logging.INFO, event_level=logging.ERROR)],
        )
