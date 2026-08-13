from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.accounts.permissions import REPORT_AUTHOR_ROLE_CODES, user_has_any_role
from apps.accounts.selectors import villages_for_user
from apps.audit.services import record_event
from apps.locations.models import Village
from apps.reporting.models import ReportingPeriod, ReportSectionStatus, TNKReport


@transaction.atomic
def create_report(*, village: Village, reporting_period: ReportingPeriod, prepared_by) -> TNKReport:
    if not user_has_any_role(prepared_by, REPORT_AUTHOR_ROLE_CODES):
        raise PermissionDenied("Your role cannot create TNK reports.")
    if not villages_for_user(prepared_by).filter(pk=village.pk).exists():
        raise PermissionDenied("You are not assigned to this village.")
    period = ReportingPeriod.objects.select_for_update().get(pk=reporting_period.pk)
    if not period.is_open or period.is_locked:
        raise ValidationError("Reports can only be created in an open, unlocked period.")
    previous_report = TNKReport.objects.filter(
        village=village,
        reporting_period__start_date__lt=period.start_date,
        status__in=(TNKReport.Status.APPROVED, TNKReport.Status.LOCKED, TNKReport.Status.ARCHIVED),
    ).order_by("-reporting_period__start_date").first()
    report = TNKReport(
        village=village,
        reporting_period=period,
        previous_report=previous_report,
        prepared_by=prepared_by,
        collection_started_at=timezone.now(),
    )
    report.full_clean()
    try:
        with transaction.atomic():
            report.save()
    except IntegrityError as error:
        raise ValidationError("A report already exists for this village and reporting period.") from error
    ReportSectionStatus.objects.bulk_create(
        [ReportSectionStatus(report=report, section_code=code) for code, _ in ReportSectionStatus.Section.choices]
    )
    record_event(actor=prepared_by, action="report.created", instance=report, summary=f"Created {report}")
    return report
