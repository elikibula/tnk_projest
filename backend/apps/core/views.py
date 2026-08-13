from django.contrib.auth.decorators import login_required
from django.db import connection
from django.http import JsonResponse
from django.shortcuts import render
from apps.accounts.permissions import DETAILED_REPORT_ROLE_CODES, REPORT_AUTHOR_ROLE_CODES, user_has_any_role
from apps.reporting.selectors import reports_for_user


def healthcheck(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception:
        return JsonResponse({"status": "unavailable"}, status=503)
    return JsonResponse({"status": "ok"})

@login_required
def dashboard(request):
    reports = reports_for_user(request.user).select_related("village", "reporting_period")
    can_view_details = user_has_any_role(request.user, DETAILED_REPORT_ROLE_CODES)
    current_report = reports.order_by("-reporting_period__start_date").first()
    return render(request, "core/dashboard.html", {
        "current_report": current_report,
        "recent_reports": reports[:5] if can_view_details else reports.none(),
        "report_count": reports.count(),
        "draft_count": reports.filter(status__in=("draft", "returned_to_village")).count(),
        "review_count": reports.filter(status__in=("submitted", "under_tikina_review", "under_provincial_review")).count(),
        "approved_count": reports.filter(status__in=("approved", "locked")).count(),
        "can_create": user_has_any_role(request.user, REPORT_AUTHOR_ROLE_CODES),
        "can_view_details": can_view_details,
    })
