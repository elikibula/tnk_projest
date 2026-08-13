from decimal import Decimal

from django.contrib.contenttypes.models import ContentType
from django.db.models import Avg

from apps.documents.models import EvidenceLink

from .models import ReportSectionStatus, TNKReport
from .section_entries import entry_queryset
from .section_registry import SECTION_ENTRIES


MAX_IN_PROGRESS = Decimal("90.00")


def calculate_section_progress(report: TNKReport, section: ReportSectionStatus) -> Decimal:
    """Calculate section progress without asking a user to estimate a percentage."""
    if section.status in (ReportSectionStatus.Status.COMPLETE, ReportSectionStatus.Status.VERIFIED) or section.confirmed_unchanged:
        return Decimal("100.00")

    if section.section_code == ReportSectionStatus.Section.EVIDENCE_DECLARATIONS:
        content_type = ContentType.objects.get_for_model(report)
        has_evidence = EvidenceLink.objects.filter(content_type=content_type, object_id=report.pk).exists()
        return MAX_IN_PROGRESS if has_evidence else (Decimal("10.00") if section.status != ReportSectionStatus.Status.NOT_STARTED else Decimal("0.00"))

    if section.section_code == ReportSectionStatus.Section.VALIDATION_SUBMISSION:
        checks = 0
        if report.data_quality_score is not None:
            checks += 1
        if hasattr(report, "final_declaration") and report.final_declaration.acknowledged:
            checks += 1
        return Decimal(checks * 45) if checks else (Decimal("10.00") if section.status != ReportSectionStatus.Status.NOT_STARTED else Decimal("0.00"))

    configs = SECTION_ENTRIES.get(section.section_code, ())
    if not configs:
        return Decimal("50.00") if section.status != ReportSectionStatus.Status.NOT_STARTED else Decimal("0.00")

    # A non-repeatable master form is counted only after the user opens the
    # section and marks work as started; repeatable groups count when a record exists.
    completed_groups = sum(
        1
        for config in configs
        if (not config.allow_create and section.status != ReportSectionStatus.Status.NOT_STARTED)
        or (config.allow_create and entry_queryset(config, report).exists())
    )
    if not completed_groups:
        return Decimal("10.00") if section.status != ReportSectionStatus.Status.NOT_STARTED else Decimal("0.00")
    return min(MAX_IN_PROGRESS, (Decimal(completed_groups) / Decimal(len(configs)) * MAX_IN_PROGRESS).quantize(Decimal("0.01")))


def recalculate_section_progress(section: ReportSectionStatus) -> Decimal:
    value = calculate_section_progress(section.report, section)
    if section.confirmed_unchanged and section.status != ReportSectionStatus.Status.VERIFIED:
        section.status = ReportSectionStatus.Status.COMPLETE
    elif value > 0 and section.status == ReportSectionStatus.Status.NOT_STARTED:
        section.status = ReportSectionStatus.Status.IN_PROGRESS
    section.completion_percentage = value
    section.save(update_fields=("status", "completion_percentage", "last_updated_at"))
    return value


def recalculate_report_progress(report: TNKReport) -> Decimal:
    for section in report.section_statuses.select_related("report"):
        recalculate_section_progress(section)
    total = report.section_statuses.aggregate(value=Avg("completion_percentage"))["value"] or Decimal("0.00")
    total = Decimal(total).quantize(Decimal("0.01"))
    TNKReport.objects.filter(pk=report.pk).update(completeness_percentage=total)
    report.completeness_percentage = total
    return total
