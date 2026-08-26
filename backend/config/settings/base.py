from datetime import timedelta
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parents[2]
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "unsafe-development-only-key")
DEBUG = False
ALLOWED_HOSTS = [h.strip() for h in os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1,10.12.129.199").split(",") if h.strip()]
CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in os.getenv("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",") if origin.strip()]
INSTALLED_APPS = [
    "django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes",
    "django.contrib.sessions", "django.contrib.messages", "django.contrib.staticfiles",
    "rest_framework", "drf_spectacular", "rest_framework_simplejwt.token_blacklist",
    "apps.core", "apps.locations", "apps.accounts", "apps.audit", "apps.reporting", "apps.administration",
    "apps.governance", "apps.population",
    "apps.infrastructure", "apps.wellbeing", "apps.economy", "apps.projects", "apps.resilience", "apps.culture",
    "apps.documents", "apps.data_quality", "apps.workflow", "apps.analytics", "apps.mobile_api",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware", "apps.core.middleware.RequestContextMiddleware",
    "apps.core.middleware.SecurityHeadersMiddleware", "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware", "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware", "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware", "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
ROOT_URLCONF = "config.urls"
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [BASE_DIR / "templates"], "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.request", "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
        "apps.accounts.context_processors.role_capabilities",
    ]},
}]
WSGI_APPLICATION = "config.wsgi.application"
AUTH_USER_MODEL = "accounts.User"
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
LANGUAGE_CODE = "en"
LANGUAGES = [("en", "English"), ("fj", "iTaukei")]
LOCALE_PATHS = [BASE_DIR / "locale"]
TIME_ZONE = "Pacific/Fiji"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = Path(os.getenv("DJANGO_STATIC_ROOT", BASE_DIR / "staticfiles"))
MEDIA_URL = "media/"
MEDIA_ROOT = Path(os.getenv("DJANGO_MEDIA_ROOT", BASE_DIR / "media"))
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LOGIN_REDIRECT_URL = "core:dashboard"
LOGOUT_REDIRECT_URL = "login"
TNK_REPORTING_MIN_YEAR = int(os.getenv("TNK_REPORTING_MIN_YEAR", "2000"))
TNK_REPORTING_MAX_YEAR = int(os.getenv("TNK_REPORTING_MAX_YEAR", "2100"))
TNK_MAX_UPLOAD_BYTES = int(os.getenv("TNK_MAX_UPLOAD_BYTES", str(10 * 1024 * 1024)))
TNK_PDF_FONT_PATH = os.getenv("TNK_PDF_FONT_PATH", "")
TNK_PDF_FONT_BOLD_PATH = os.getenv("TNK_PDF_FONT_BOLD_PATH", "")
SESSION_COOKIE_AGE = int(os.getenv("DJANGO_SESSION_COOKIE_AGE", "3600"))
SESSION_SAVE_EVERY_REQUEST = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_REFERRER_POLICY = "same-origin"
CONTENT_SECURITY_POLICY = os.getenv(
    "DJANGO_CONTENT_SECURITY_POLICY",
    "default-src 'self'; base-uri 'self'; connect-src 'self'; font-src 'self' data:; "
    "form-action 'self'; frame-ancestors 'none'; img-src 'self' data: https://tile.openstreetmap.org https://unpkg.com; "
    "object-src 'none'; script-src 'self' https://cdn.jsdelivr.net https://unpkg.com; "
    "style-src 'self' 'unsafe-inline' https://unpkg.com; upgrade-insecure-requests",
)
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ("apps.mobile_api.authentication.ActiveDeviceJWTAuthentication",),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "EXCEPTION_HANDLER": "apps.mobile_api.exceptions.mobile_api_exception_handler",
    "DEFAULT_THROTTLE_RATES": {"mobile_login": os.getenv("MOBILE_LOGIN_RATE", "5/minute")},
}
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=int(os.getenv("MOBILE_ACCESS_TOKEN_MINUTES", "10"))),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=int(os.getenv("MOBILE_REFRESH_TOKEN_DAYS", "7"))),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
}
SPECTACULAR_SETTINGS = {"TITLE": "TNK Insight Mobile API", "VERSION": "1.0.0", "SERVE_INCLUDE_SCHEMA": False}
MOBILE_MINIMUM_SUPPORTED_VERSION = os.getenv("MOBILE_MINIMUM_SUPPORTED_VERSION", "1.0.0")
MOBILE_LATEST_VERSION = os.getenv("MOBILE_LATEST_VERSION", "1.0.0")
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"json": {"()": "apps.core.logging.JsonFormatter"}},
    "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "json"}},
    "root": {"handlers": ["console"], "level": os.getenv("DJANGO_LOG_LEVEL", "INFO")},
    "loggers": {
        "django": {"handlers": ["console"], "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"), "propagate": False},
        "tnk": {"handlers": ["console"], "level": os.getenv("TNK_LOG_LEVEL", "INFO"), "propagate": False},
    },
}
