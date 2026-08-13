from decimal import Decimal, InvalidOperation

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, transaction
from django.db.models import Max
from django.utils import timezone

from apps.accounts.models import Role
from apps.accounts.permissions import REPORT_AUTHOR_ROLE_CODES, user_has_any_role
from apps.audit.services import record_event
from apps.core.security import can_view_entry, can_view_report
from apps.reporting.history import _json_value
from apps.reporting.models import ReportAmendment, ReportAmendmentChange, ReportMasterSnapshot, TNKReport
from apps.reporting.section_entries import entry_queryset
from apps.reporting.section_registry import get_entry_config
from apps.reporting.selectors import reports_for_user


OFFICIAL_STATUSES = {TNKReport.Status.APPROVED, TNKReport.Status.LOCKED, TNKReport.Status.ARCHIVED}
REQUEST_ROLES = frozenset(REPORT_AUTHOR_ROLE_CODES) | {Role.Codes.PROVINCIAL_ADMIN, Role.Codes.SYSTEM_ADMIN}
ADMIN_EDIT_ROLES = {Role.Codes.PROVINCIAL_ADMIN, Role.Codes.SYSTEM_ADMIN}
APPROVE_ROLES = {Role.Codes.ROKO_TUI, Role.Codes.SYSTEM_ADMIN}


def _require_report_scope(user, report):
    if not can_view_report(user, report) or not reports_for_user(user).filter(pk=report.pk).exists():
        raise PermissionDenied("You are not assigned to this report location.")


def _require_draft_editor(user, amendment):
    _require_report_scope(user, amendment.original_report)
    if amendment.status != ReportAmendment.Status.DRAFT:
        raise ValidationError("Only a draft amendment can be changed.")
    if amendment.requested_by_id != user.pk and not user_has_any_role(user, ADMIN_EDIT_ROLES):
        raise PermissionDenied("Only the requester or an authorised administrator can edit this draft amendment.")


@transaction.atomic
def create_amendment(*, report, user, reason, notes=""):
    locked_report = TNKReport.objects.select_for_update().get(pk=report.pk)
    _require_report_scope(user, locked_report)
    if not user_has_any_role(user, REQUEST_ROLES):
        raise PermissionDenied("Your role cannot request an official-report amendment.")
    if locked_report.status not in OFFICIAL_STATUSES:
        raise ValidationError("Amendments can be requested only for approved, locked, or archived reports.")
    if not reason.strip():
        raise ValidationError({"reason": "Explain why this official report needs an amendment."})
    latest_number = ReportAmendment.objects.filter(original_report=locked_report).aggregate(value=Max("amendment_number"))["value"] or 0
    previous = ReportAmendment.objects.filter(original_report=locked_report, status=ReportAmendment.Status.APPROVED).order_by("-amendment_number").first()
    try:
        amendment = ReportAmendment.objects.create(
            original_report=locked_report,
            amendment_number=latest_number + 1,
            reason=reason.strip(),
            notes=notes.strip(),
            requested_by=user,
            supersedes_previous=previous is not None,
            supersedes_amendment=previous,
        )
    except IntegrityError as error:
        raise ValidationError("Another amendment was created at the same time. Refresh and try again.") from error
    record_event(actor=user, action="report.amendment_created", instance=amendment, summary=f"Created amendment {amendment.amendment_number} for {locked_report}")
    return amendment


def _resolve_original_value(report, section_code, entry_key, source_identifier, field_name):
    config = get_entry_config(section_code, entry_key)
    if config is None:
        raise ValidationError("The selected entry type does not belong to the selected section.")
    if field_name not in config.fields:
        raise ValidationError({"field_name": "The selected field is not part of this report entry."})
    snapshot = ReportMasterSnapshot.objects.filter(
        report=report,
        section_code=section_code,
        entry_key=entry_key,
        source_identifier=str(source_identifier),
    ).first()
    if snapshot is not None:
        if field_name not in snapshot.values:
            raise ValidationError({"field_name": "The historical snapshot does not contain this field."})
        return config, snapshot.source_model, snapshot.values[field_name]
    lookup = {"uuid": source_identifier} if any(field.name == "uuid" for field in config.model._meta.fields) else {"pk": source_identifier}
    instance = entry_queryset(config, report).filter(**lookup).first()
    if instance is None:
        raise ValidationError({"source_identifier": "No record in this official report matches that identifier."})
    return config, instance._meta.label, _json_value(getattr(instance, field_name))


@transaction.atomic
def add_amendment_change(
    *,
    amendment,
    user,
    section_code,
    entry_key,
    source_identifier,
    field_name,
    amended_value,
    change_reason,
    indicator_code="",
    amended_indicator_value=None,
    amended_indicator_numerator=None,
    amended_indicator_denominator=None,
):
    locked = ReportAmendment.objects.select_for_update().select_related("original_report", "requested_by").get(pk=amendment.pk)
    _require_draft_editor(user, locked)
    config, source_model, original_value = _resolve_original_value(
        locked.original_report, section_code, entry_key, source_identifier, field_name
    )
    if not can_view_entry(user, section_code, config.model, locked.original_report.village):
        raise PermissionDenied("Your role cannot amend this report entry type.")
    try:
        field_label = str(config.model._meta.get_field(field_name).verbose_name).replace("_", " ").title()
    except Exception:
        field_label = field_name.replace("_", " ").title()

    analytics = {}
    if indicator_code:
        from apps.analytics.models import IndicatorDefinition, IndicatorValue

        indicator = IndicatorDefinition.objects.filter(code=indicator_code, is_active=True).first()
        if indicator is None:
            raise ValidationError({"indicator_code": "Select an active indicator definition."})
        indicator_value = IndicatorValue.objects.filter(
            indicator=indicator,
            reporting_period=locked.original_report.reporting_period,
            village=locked.original_report.village,
        ).first()
        if indicator_value is None or indicator_value.calculation_status != IndicatorValue.CalculationStatus.CALCULATED:
            raise ValidationError({"indicator_code": "This report has no calculated value for that indicator."})
        try:
            amended_number = Decimal(str(amended_indicator_value))
            amended_numerator = Decimal(str(amended_indicator_numerator)) if amended_indicator_numerator not in (None, "") else None
            amended_denominator = Decimal(str(amended_indicator_denominator)) if amended_indicator_denominator not in (None, "") else None
        except (InvalidOperation, TypeError) as error:
            raise ValidationError({"amended_indicator_value": "Enter valid numeric analytics values."}) from error
        if amended_number == indicator_value.value:
            raise ValidationError({"amended_indicator_value": "The amended indicator value must differ from the original."})
        if indicator_value.denominator_value is not None and (amended_numerator is None or amended_denominator is None):
            raise ValidationError({"amended_indicator_denominator": "Rate and average overrides require an amended numerator and denominator."})
        if amended_denominator is not None:
            if amended_denominator <= 0:
                raise ValidationError({"amended_indicator_denominator": "The amended denominator must be greater than zero."})
            from apps.analytics.services import _aggregate_scale, stored_decimal

            calculated_override = stored_decimal(amended_numerator / amended_denominator * _aggregate_scale(indicator.code))
            if stored_decimal(amended_number) != calculated_override:
                raise ValidationError(
                    {"amended_indicator_value": "The amended value does not match its numerator and denominator."}
                )
        analytics = {
            "affects_analytics": True,
            "indicator": indicator,
            "original_indicator_value": indicator_value.value,
            "amended_indicator_value": amended_number,
            "original_indicator_numerator": indicator_value.numerator_value,
            "amended_indicator_numerator": amended_numerator if amended_numerator is not None else amended_number,
            "original_indicator_denominator": indicator_value.denominator_value,
            "amended_indicator_denominator": amended_denominator,
        }
    change = ReportAmendmentChange(
        amendment=locked,
        section_code=section_code,
        entry_key=entry_key,
        source_model=source_model,
        source_identifier=str(source_identifier),
        field_name=field_name,
        field_label=field_label,
        original_value=original_value,
        amended_value=amended_value,
        change_reason=change_reason.strip(),
        created_by=user,
        **analytics,
    )
    change.full_clean()
    change.save()
    record_event(actor=user, action="report.amendment_change_added", instance=change, summary=f"Added {field_label} correction to amendment {locked.amendment_number}")
    return change


@transaction.atomic
def transition_amendment(*, amendment, user, action, comment="", acknowledged=False):
    locked = ReportAmendment.objects.select_for_update().select_related("original_report", "requested_by").get(pk=amendment.pk)
    _require_report_scope(user, locked.original_report)
    now = timezone.now()
    updates = {"record_version": locked.record_version + 1}
    if action == "submit":
        _require_draft_editor(user, locked)
        if not locked.changes.exists():
            raise ValidationError("Add at least one original/amended value before submission.")
        updates.update(status=ReportAmendment.Status.SUBMITTED, submitted_at=now)
    elif action == "approve":
        if locked.status != ReportAmendment.Status.SUBMITTED:
            raise ValidationError("Only a submitted amendment can be approved.")
        if not user_has_any_role(user, APPROVE_ROLES):
            raise PermissionDenied("Your role cannot approve report amendments.")
        if locked.requested_by_id == user.pk:
            raise PermissionDenied("The requester cannot approve their own amendment.")
        if not acknowledged:
            raise ValidationError("Acknowledge the amendment approval before continuing.")
        updates.update(status=ReportAmendment.Status.APPROVED, approved_by=user, approved_at=now, review_comment=comment.strip())
    elif action == "reject":
        if locked.status != ReportAmendment.Status.SUBMITTED:
            raise ValidationError("Only a submitted amendment can be rejected.")
        if not user_has_any_role(user, APPROVE_ROLES):
            raise PermissionDenied("Your role cannot reject report amendments.")
        if not comment.strip():
            raise ValidationError("Explain why the amendment is being rejected.")
        updates.update(status=ReportAmendment.Status.REJECTED, rejected_by=user, rejected_at=now, review_comment=comment.strip())
    elif action == "withdraw":
        if locked.status not in (ReportAmendment.Status.DRAFT, ReportAmendment.Status.SUBMITTED):
            raise ValidationError("Only a draft or submitted amendment can be withdrawn.")
        if locked.requested_by_id != user.pk and not user_has_any_role(user, ADMIN_EDIT_ROLES):
            raise PermissionDenied("Only the requester or an authorised administrator can withdraw this amendment.")
        updates.update(status=ReportAmendment.Status.WITHDRAWN, review_comment=comment.strip())
    else:
        raise ValidationError("Unsupported amendment workflow action.")
    ReportAmendment.objects.filter(pk=locked.pk).update(**updates)
    locked.refresh_from_db()
    record_event(actor=user, action=f"report.amendment_{action}", instance=locked, summary=f"{action.title()} amendment {locked.amendment_number} for {locked.original_report}", metadata={"comment": comment.strip()})
    if action == "approve" and locked.changes.filter(affects_analytics=True).exists():
        from apps.analytics.services import aggregate_indicators

        aggregate_indicators(locked.original_report.reporting_period, locked.original_report.village.tikina)
        aggregate_indicators(locked.original_report.reporting_period, locked.original_report.village.tikina.province)
    amendment.status = locked.status
    amendment.record_version = locked.record_version
    return locked


def authoritative_amendment(report):
    return report.amendments.filter(status=ReportAmendment.Status.APPROVED).order_by("-amendment_number").first()


def authoritative_changes(report, *, section_code=None):
    queryset = ReportAmendmentChange.objects.filter(
        amendment__original_report=report,
        amendment__status=ReportAmendment.Status.APPROVED,
    ).select_related("amendment", "indicator").order_by("amendment__amendment_number", "pk")
    if section_code:
        queryset = queryset.filter(section_code=section_code)
    effective = {}
    for change in queryset:
        key = (change.section_code, change.entry_key, change.source_identifier, change.field_name)
        effective[key] = change
    return list(effective.values())


def apply_indicator_overrides(values):
    values = list(values)
    if not values:
        return values
    report_by_location = {
        (report.reporting_period_id, report.village_id): report
        for report in TNKReport.objects.filter(
            reporting_period_id__in={value.reporting_period_id for value in values},
            village_id__in={value.village_id for value in values if value.village_id},
        )
    }
    report_ids = {report.pk for report in report_by_location.values()}
    overrides = {}
    for change in ReportAmendmentChange.objects.filter(
        amendment__original_report_id__in=report_ids,
        amendment__status=ReportAmendment.Status.APPROVED,
        affects_analytics=True,
    ).select_related("amendment").order_by("amendment__amendment_number", "pk"):
        overrides[(change.amendment.original_report_id, change.indicator_id)] = change
    for value in values:
        report = report_by_location.get((value.reporting_period_id, value.village_id))
        change = overrides.get((report.pk, value.indicator_id)) if report else None
        value.authoritative_value = change.amended_indicator_value if change else value.value
        value.authoritative_numerator = change.amended_indicator_numerator if change else value.numerator_value
        value.authoritative_denominator = change.amended_indicator_denominator if change else value.denominator_value
        value.authoritative_amendment = change.amendment if change else None
    return values
