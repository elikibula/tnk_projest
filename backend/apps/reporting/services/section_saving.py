from decimal import Decimal

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.db.models import F

from apps.accounts.permissions import REPORT_AUTHOR_ROLE_CODES, user_has_any_role
from apps.audit.services import record_event
from apps.reporting.models import ReportSectionStatus, TNKReport
from apps.reporting.selectors import reports_for_user
from apps.reporting.progress import recalculate_report_progress


@transaction.atomic
def update_section_status(*, report: TNKReport, section_code: str, status: str, confirmed_unchanged: bool, user, expected_version: int, completion_percentage: Decimal | None = None) -> ReportSectionStatus:
    if not user_has_any_role(user, REPORT_AUTHOR_ROLE_CODES):
        raise PermissionDenied("Your role cannot edit this report.")
    if not reports_for_user(user).filter(pk=report.pk).exists():
        raise PermissionDenied("You are not assigned to this report's village.")
    locked_report = TNKReport.objects.select_for_update().get(pk=report.pk)
    if not locked_report.is_editable:
        raise ValidationError("This report is not editable in its current status.")
    if locked_report.record_version != expected_version:
        raise ValidationError("This report changed in another session. Reload and try again.")
    section = ReportSectionStatus.objects.get(report=locked_report, section_code=section_code)
    section.status = status
    section.confirmed_unchanged = confirmed_unchanged
    section.last_updated_by = user
    section.full_clean()
    section.save()
    completeness = recalculate_report_progress(locked_report)
    TNKReport.objects.filter(pk=locked_report.pk).update(record_version=F("record_version") + 1)
    section.refresh_from_db()
    record_event(actor=user, action="report.section_saved", instance=locked_report, summary=f"Saved {section.get_section_code_display()}", metadata={"section_code": section_code, "automatic_percentage": str(section.completion_percentage), "report_percentage": str(completeness)})
    return section
