from django.core.exceptions import ValidationError
from django.db import transaction

from apps.audit.services import record_event
from apps.core.historical import require_master_editor

from .models import IVDPProject


PROJECT_MASTER_FIELDS = {
    "project_name",
    "project_category",
    "problem_being_addressed",
    "baseline_value",
    "target_value",
    "measurement_unit",
    "priority",
    "responsible_person",
    "responsible_organisation",
    "planned_start_date",
    "planned_end_date",
    "actual_start_date",
    "actual_end_date",
    "estimated_budget",
    "approved_budget",
    "actual_expenditure",
    "currency_code",
    "funding_source",
    "project_status",
    "physical_progress_percentage",
    "financial_progress_percentage",
    "expected_beneficiaries",
    "male_beneficiaries",
    "female_beneficiaries",
    "youth_beneficiaries",
    "is_active",
}


@transaction.atomic
def update_project_master(*, project: IVDPProject, user, effective_date, reason, **changes):
    locked = IVDPProject.objects.select_for_update().get(pk=project.pk)
    require_master_editor(user, locked.village)
    if not reason.strip():
        raise ValidationError("A project master change reason is required.")
    unknown = set(changes) - PROJECT_MASTER_FIELDS
    if unknown:
        raise ValidationError(f"Unsupported project change fields: {', '.join(sorted(unknown))}.")
    for field, value in changes.items():
        setattr(locked, field, value)
    locked.record_version += 1
    locked.full_clean()
    locked.save(update_fields=(*changes.keys(), "record_version", "updated_at"))
    record_event(actor=user, action="projects.IVDPProject.changed", instance=locked, summary="Changed IVDP project master record", metadata={"effective_date": str(effective_date), "reason": reason})
    return locked
