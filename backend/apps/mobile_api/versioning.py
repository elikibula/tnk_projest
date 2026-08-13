import re

from django.conf import settings


VERSION_PATTERN = re.compile(r"^(\d+)\.(\d+)\.(\d+)(?:\+\d+)?$")


def parse_app_version(value):
    match = VERSION_PATTERN.fullmatch(value or "")
    if not match:
        return None
    return tuple(int(part) for part in match.groups())


def app_version_policy(app_version):
    current = parse_app_version(app_version)
    minimum = parse_app_version(settings.MOBILE_MINIMUM_SUPPORTED_VERSION)
    latest = parse_app_version(settings.MOBILE_LATEST_VERSION)
    force_upgrade = current is None or minimum is None or current < minimum
    update_available = not force_upgrade and latest is not None and current < latest
    return {
        "minimum_supported_version": settings.MOBILE_MINIMUM_SUPPORTED_VERSION,
        "latest_version": settings.MOBILE_LATEST_VERSION,
        "force_upgrade": force_upgrade,
        "update_available": update_available,
    }
