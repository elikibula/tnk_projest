from decimal import Decimal

from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.utils import timezone

from apps.documents.models import EvidenceLink
from apps.economy.models import VillageBusiness
from apps.infrastructure.models import EnergySnapshot, VillageWaterSource
from apps.population.models import Household
from apps.projects.models import IVDPProject
from apps.reporting.models import ReportSectionStatus, TNKReport
from apps.reporting.progress import recalculate_report_progress
from .models import DataQualityIssue, DataQualityRule


DEFAULT_RULES = (
    ("required_sections", "validation_submission", "All report sections must be complete.", "critical"),
    ("household_components", "population_households", "Household component counts cannot exceed household size.", "error"),
    ("water_coverage", "water", "Households served by a water source cannot exceed active households.", "error"),
    ("energy_coverage", "energy", "Connected households cannot exceed active households.", "error"),
    ("closed_business", "business_finance", "A closed business requires a closure date.", "error"),
    ("completed_project", "ivdp_projects", "A completed project requires a valid completion date.", "error"),
    ("report_late", "validation_submission", "Report is being completed after its due date.", "warning"),
)


def ensure_default_rules():
    return {
        code: DataQualityRule.objects.get_or_create(
            code=code,
            defaults={"section": section, "description": description, "severity": severity},
        )[0]
        for code, section, description, severity in DEFAULT_RULES
    }


def add_issue(report, rule, message, *, field_name="", current_value="", previous_value=""):
    """Create an issue once, while retaining prior validation history."""
    issue = DataQualityIssue.objects.filter(
        report=report,
        rule=rule,
        field_name=field_name,
        message=message,
        resolved=False,
    ).first()
    if issue is None:
        issue = DataQualityIssue.objects.create(
            report=report,
            section=rule.section,
            field_name=field_name,
            rule=rule,
            severity=rule.severity,
            message=message,
            current_value=str(current_value),
            previous_value=str(previous_value),
        )
    else:
        issue.current_value = str(current_value)
        issue.previous_value = str(previous_value)
        issue.severity = rule.severity
        issue.save(update_fields=("current_value", "previous_value", "severity"))
    return issue


@transaction.atomic
def validate_report(report: TNKReport):
    rules = ensure_default_rules()
    previously_open = set(
        DataQualityIssue.objects.filter(report=report, resolved=False).values_list("pk", flat=True)
    )
    current_issue_ids = set()

    def flag(rule_code, message, **details):
        issue = add_issue(report, rules[rule_code], message, **details)
        current_issue_ids.add(issue.pk)
        return issue
    incomplete = report.section_statuses.exclude(
        status__in=(ReportSectionStatus.Status.COMPLETE, ReportSectionStatus.Status.VERIFIED)
    ).count()
    if incomplete:
        flag("required_sections", f"{incomplete} sections are not complete.", current_value=incomplete)

    households = Household.objects.filter(village=report.village, is_active=True)
    household_count = households.count()
    for household in households:
        components = sum(value or 0 for value in (household.male_count, household.female_count))
        if household.household_size is not None and components > household.household_size:
            flag("household_components", f"Household {household.household_code} components exceed its size.", field_name="household_size", current_value=components)

    for source in VillageWaterSource.objects.filter(village=report.village, is_active=True):
        if source.households_served is not None and source.households_served > household_count:
            flag("water_coverage", f"Water source {source.source_name} serves more households than are active.", field_name="households_served", current_value=source.households_served)

    for snapshot in EnergySnapshot.objects.filter(report=report):
        if snapshot.households_connected is not None and snapshot.households_connected > household_count:
            flag("energy_coverage", "Connected households exceed the active household count.", field_name="households_connected", current_value=snapshot.households_connected)

    for business in VillageBusiness.objects.filter(village=report.village, operating_status__iexact="closed", closure_date__isnull=True):
        flag("closed_business", f"Closed business {business.business_name} has no closure date.", field_name="closure_date")

    for project in IVDPProject.objects.filter(village=report.village, project_status__iexact="completed"):
        invalid_date = project.actual_end_date is None or (project.actual_start_date and project.actual_end_date < project.actual_start_date)
        if invalid_date:
            flag("completed_project", f"Completed project {project.project_name} has an invalid completion date.", field_name="actual_end_date")

    if timezone.localdate() > report.reporting_period.submission_due_date:
        flag("report_late", "The reporting period submission due date has passed.")

    stale_issue_ids = previously_open - current_issue_ids
    if stale_issue_ids:
        DataQualityIssue.objects.filter(pk__in=stale_issue_ids).update(
            resolved=True,
            resolution_comment="Automatically resolved by a later validation run.",
            resolved_at=timezone.now(),
        )

    for section in report.section_statuses.all():
        open_issues = report.quality_issues.filter(section=section.section_code, resolved=False)
        issue_count = open_issues.count()
        blocking_issue_count = open_issues.filter(severity__in=("error", "critical")).count()
        section.issue_count = issue_count
        if blocking_issue_count and section.status == ReportSectionStatus.Status.COMPLETE:
            section.status = ReportSectionStatus.Status.NEEDS_ATTENTION
        elif not blocking_issue_count and section.status == ReportSectionStatus.Status.NEEDS_ATTENTION:
            section.status = ReportSectionStatus.Status.COMPLETE
        section.save(update_fields=("issue_count", "status", "last_updated_at"))

    section_count = report.section_statuses.count() or 1
    completeness = recalculate_report_progress(report)
    blocking_count = report.quality_issues.filter(resolved=False, severity__in=("error", "critical")).count()
    consistency = Decimal(max(0, 100 - blocking_count * 20))
    verification = Decimal(report.section_statuses.filter(status="verified").count() * 100 / section_count).quantize(Decimal("0.01"))
    timeliness = Decimal(100 if timezone.localdate() <= report.reporting_period.submission_due_date else 50)
    report_content_type = ContentType.objects.get_for_model(report)
    evidence = Decimal(100 if EvidenceLink.objects.filter(content_type=report_content_type, object_id=report.pk).exists() else 0)
    # Save a non-null validation marker inside the transaction, then refresh
    # progress so the validation/submission section reflects this completed check.
    report.data_quality_score = Decimal("0.00")
    report.verification_score = verification
    report.timeliness_score = timeliness
    report.evidence_score = evidence
    report.save(update_fields=("data_quality_score", "verification_score", "timeliness_score", "evidence_score", "updated_at"))
    completeness = recalculate_report_progress(report)
    total = (
        completeness * Decimal(".30")
        + consistency * Decimal(".25")
        + verification * Decimal(".20")
        + timeliness * Decimal(".15")
        + evidence * Decimal(".10")
    ).quantize(Decimal("0.01"))
    report.completeness_percentage = completeness
    report.data_quality_score = total
    report.save(update_fields=("completeness_percentage", "data_quality_score", "updated_at"))
    return report.quality_issues.filter(resolved=False)
