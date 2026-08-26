from collections.abc import Iterable

from .models import Role

REPORT_AUTHOR_ROLE_CODES = {
    Role.Codes.TURAGA_NI_KORO,
    Role.Codes.VILLAGE_DATA_ASSISTANT,
}

DETAILED_REPORT_ROLE_CODES = set(Role.Codes.values) - {Role.Codes.READ_ONLY_ANALYST}

PHOTO_REPORT_ROLE_CODES = {
    Role.Codes.ROKO_VEIVUKE,
    Role.Codes.ROKO_TUI,
    Role.Codes.PROVINCIAL_ADMIN,
    Role.Codes.SYSTEM_ADMIN,
}


def user_has_any_role(user, role_codes: Iterable[str]) -> bool:
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return user.role_assignments.filter(
        is_active=True,
        role__is_active=True,
        role__code__in=set(role_codes),
    ).exists()
