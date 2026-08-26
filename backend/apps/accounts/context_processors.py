from .models import Role
from .permissions import DETAILED_REPORT_ROLE_CODES, PHOTO_REPORT_ROLE_CODES, user_has_any_role


def role_capabilities(request):
    return {
        "can_view_photo_reports": user_has_any_role(request.user, PHOTO_REPORT_ROLE_CODES),
        "can_view_detailed_reports": user_has_any_role(request.user, DETAILED_REPORT_ROLE_CODES),
        "can_access_administration": user_has_any_role(
            request.user, {Role.Codes.SYSTEM_ADMIN, Role.Codes.PROVINCIAL_ADMIN}
        ),
    }
