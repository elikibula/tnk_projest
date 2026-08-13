from dataclasses import dataclass

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import Role
from apps.accounts.permissions import REPORT_AUTHOR_ROLE_CODES, user_has_any_role
from apps.audit.services import record_event
from apps.data_quality.services import validate_report
from apps.reporting.models import TNKReport
from apps.reporting.selectors import reports_for_user

from .models import ApprovalAction, FinalDeclaration


@dataclass(frozen=True)
class TransitionDefinition:
    target: str
    roles_by_source: dict[str, frozenset[str]]
    action_type: str
    requires_comment: bool = False
    requires_acknowledgement: bool = False
    requires_declaration: bool = False
    validates_quality: bool = False
    prevents_self_action: bool = False
    timestamp_field: str | None = None

    @property
    def sources(self):
        return tuple(self.roles_by_source)

    def roles_for(self, status):
        return self.roles_by_source.get(status, frozenset())


AUTHOR_ROLES = frozenset(REPORT_AUTHOR_ROLE_CODES)
TURAGA_ROLES = frozenset({Role.Codes.TURAGA_NI_KORO})
TIKINA_REVIEW_ROLES = frozenset({Role.Codes.MATA_NI_TIKINA, Role.Codes.ROKO_VEIVUKE})
PROVINCIAL_REVIEW_ROLES = frozenset({Role.Codes.ROKO_TUI})
LOCKING_ROLES = frozenset({Role.Codes.ROKO_TUI, Role.Codes.SYSTEM_ADMIN})


TRANSITIONS = {
    "mark_ready": TransitionDefinition(
        target=TNKReport.Status.READY_FOR_VALIDATION,
        roles_by_source={
            TNKReport.Status.DRAFT: AUTHOR_ROLES,
            TNKReport.Status.RETURNED_TO_VILLAGE: AUTHOR_ROLES,
        },
        action_type="verify",
        requires_declaration=True,
        validates_quality=True,
    ),
    "reopen_draft": TransitionDefinition(
        target=TNKReport.Status.DRAFT,
        roles_by_source={TNKReport.Status.READY_FOR_VALIDATION: AUTHOR_ROLES},
        action_type="reopen",
    ),
    "submit": TransitionDefinition(
        target=TNKReport.Status.SUBMITTED,
        roles_by_source={TNKReport.Status.READY_FOR_VALIDATION: TURAGA_ROLES},
        action_type="submit",
        requires_declaration=True,
        validates_quality=True,
        timestamp_field="submitted_at",
    ),
    "start_tikina_review": TransitionDefinition(
        target=TNKReport.Status.UNDER_TIKINA_REVIEW,
        roles_by_source={TNKReport.Status.SUBMITTED: TIKINA_REVIEW_ROLES},
        action_type="verify",
        timestamp_field="district_reviewed_at",
    ),
    "return": TransitionDefinition(
        target=TNKReport.Status.RETURNED_TO_VILLAGE,
        roles_by_source={
            TNKReport.Status.SUBMITTED: TIKINA_REVIEW_ROLES,
            TNKReport.Status.UNDER_TIKINA_REVIEW: TIKINA_REVIEW_ROLES,
            TNKReport.Status.UNDER_PROVINCIAL_REVIEW: PROVINCIAL_REVIEW_ROLES,
        },
        action_type="return",
        requires_comment=True,
    ),
    "forward": TransitionDefinition(
        target=TNKReport.Status.UNDER_PROVINCIAL_REVIEW,
        roles_by_source={TNKReport.Status.UNDER_TIKINA_REVIEW: TIKINA_REVIEW_ROLES},
        action_type="forward",
        timestamp_field="provincial_reviewed_at",
    ),
    "reject": TransitionDefinition(
        target=TNKReport.Status.REJECTED,
        roles_by_source={
            TNKReport.Status.UNDER_TIKINA_REVIEW: TIKINA_REVIEW_ROLES,
            TNKReport.Status.UNDER_PROVINCIAL_REVIEW: PROVINCIAL_REVIEW_ROLES,
        },
        action_type="reject",
        requires_comment=True,
    ),
    "approve": TransitionDefinition(
        target=TNKReport.Status.APPROVED,
        roles_by_source={TNKReport.Status.UNDER_PROVINCIAL_REVIEW: PROVINCIAL_REVIEW_ROLES},
        action_type="approve",
        requires_acknowledgement=True,
        validates_quality=True,
        prevents_self_action=True,
        timestamp_field="approved_at",
    ),
    "lock": TransitionDefinition(
        target=TNKReport.Status.LOCKED,
        roles_by_source={TNKReport.Status.APPROVED: LOCKING_ROLES},
        action_type="lock",
        requires_acknowledgement=True,
        prevents_self_action=True,
        timestamp_field="locked_at",
    ),
    "archive": TransitionDefinition(
        target=TNKReport.Status.ARCHIVED,
        roles_by_source={TNKReport.Status.LOCKED: LOCKING_ROLES},
        action_type="archive",
        requires_comment=True,
        requires_acknowledgement=True,
        prevents_self_action=True,
    ),
}


def available_actions(report, user):
    if not reports_for_user(user).filter(pk=report.pk).exists():
        return []
    actions = []
    for action, definition in TRANSITIONS.items():
        roles = definition.roles_for(report.status)
        if not roles or not user_has_any_role(user, roles):
            continue
        if definition.prevents_self_action and report.prepared_by_id == user.id:
            continue
        actions.append(action)
    return actions


def _critical_issue_messages(report):
    return list(
        validate_report(report)
        .filter(severity="critical", resolved=False)
        .values_list("message", flat=True)
    )


def _require_quality(report, action):
    critical_issues = _critical_issue_messages(report)
    if not critical_issues:
        return
    label = "marked ready" if action == "mark_ready" else "submitted" if action == "submit" else "approved"
    details = " ".join(critical_issues)
    raise ValidationError(
        f"This report cannot be {label} yet. {details} "
        "Open the highlighted sections, complete or confirm them unchanged, then validate the report again."
    )


def _require_declaration(report):
    declaration = getattr(report, "final_declaration", None)
    if declaration is None or not declaration.acknowledged:
        raise ValidationError("Save and acknowledge the final declaration before continuing.")


def _invalidate_declaration(report):
    FinalDeclaration.objects.filter(report=report, acknowledged=True).update(acknowledged=False)


@transaction.atomic
def transition_report(*, report, user, action, comment="", acknowledged=False, ip_address=None, user_agent=""):
    definition = TRANSITIONS.get(action)
    if definition is None:
        raise ValidationError("Unsupported workflow action.")
    if not reports_for_user(user).filter(pk=report.pk).exists():
        raise PermissionDenied("You are not assigned to this report location.")

    locked = TNKReport.objects.select_for_update().select_related("prepared_by").get(pk=report.pk)
    roles = definition.roles_for(locked.status)
    if not roles:
        raise ValidationError(
            f"'{action.replace('_', ' ')}' is not allowed while the report is {locked.get_status_display().lower()}."
        )
    if not user_has_any_role(user, roles):
        raise PermissionDenied("Your role cannot perform this workflow action.")
    if definition.prevents_self_action and locked.prepared_by_id == user.id:
        raise PermissionDenied("You cannot approve, lock, or archive a report you prepared.")
    if definition.requires_comment and not comment.strip():
        raise ValidationError("A clear reason or correction comment is required for this action.")
    if definition.requires_acknowledgement and not acknowledged:
        raise ValidationError("Digital acknowledgement is required for this action.")
    if definition.requires_declaration:
        _require_declaration(locked)
    if definition.validates_quality:
        _require_quality(locked, action)
    if action == "mark_ready":
        from apps.reporting.history import capture_master_snapshots

        capture_master_snapshots(locked)

    old_status = locked.status
    locked.status = definition.target
    locked.record_version += 1
    update_fields = ["status", "record_version", "updated_at"]
    if action == "mark_ready":
        update_fields.append("master_snapshot_captured_at")
    if definition.timestamp_field:
        setattr(locked, definition.timestamp_field, timezone.now())
        update_fields.append(definition.timestamp_field)
    locked._workflow_transition_authorized = True
    try:
        locked.save(update_fields=update_fields)
    finally:
        del locked._workflow_transition_authorized

    if action in {"return", "reopen_draft"}:
        _invalidate_declaration(locked)

    assignment = (
        user.role_assignments.filter(is_active=True, role__is_active=True, role__code__in=roles)
        .select_related("role")
        .first()
    )
    role_name = assignment.role.name if assignment else "System Administrator"
    immutable_action = ApprovalAction.objects.create(
        report=locked,
        user=user,
        user_full_name=user.get_full_name() or user.username,
        user_role=role_name,
        action_type=definition.action_type,
        from_status=old_status,
        to_status=definition.target,
        comment=comment.strip(),
        digital_acknowledgement=acknowledged,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    record_event(
        actor=user,
        action=f"report.{action}",
        instance=locked,
        summary=f"{action.replace('_', ' ').title()}: {locked}",
        metadata={"from": old_status, "to": definition.target},
    )
    if action == "approve":
        from apps.analytics.services import aggregate_indicators, calculate_village_indicators

        calculate_village_indicators(locked)
        aggregate_indicators(locked.reporting_period, locked.village.tikina)
        aggregate_indicators(locked.reporting_period, locked.village.tikina.province)
    report.status = locked.status
    report.record_version = locked.record_version
    return immutable_action


def mark_ready_for_validation(**kwargs):
    return transition_report(action="mark_ready", **kwargs)


def reopen_draft(**kwargs):
    return transition_report(action="reopen_draft", **kwargs)


def submit_report(**kwargs):
    return transition_report(action="submit", **kwargs)


def start_tikina_review(**kwargs):
    return transition_report(action="start_tikina_review", **kwargs)


def return_report(**kwargs):
    return transition_report(action="return", **kwargs)


def forward_to_province(**kwargs):
    return transition_report(action="forward", **kwargs)


def reject_report(**kwargs):
    return transition_report(action="reject", **kwargs)


def approve_report(**kwargs):
    return transition_report(action="approve", **kwargs)


def lock_report(**kwargs):
    return transition_report(action="lock", **kwargs)


def archive_report(**kwargs):
    return transition_report(action="archive", **kwargs)
