from .permissions import DETAILED_REPORT_ROLE_CODES, user_has_any_role


def role_capabilities(request):
    return {
        "can_view_detailed_reports": user_has_any_role(request.user, DETAILED_REPORT_ROLE_CODES),
    }
