from datetime import timedelta

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import models, transaction

from apps.accounts.models import Role
from apps.accounts.permissions import REPORT_AUTHOR_ROLE_CODES, user_has_any_role
from apps.accounts.selectors import villages_for_user
from apps.audit.services import record_event


MASTER_EDITOR_ROLES = set(REPORT_AUTHOR_ROLE_CODES) | {
    Role.Codes.SYSTEM_ADMIN,
    Role.Codes.PROVINCIAL_ADMIN,
}

EFFECTIVE_RECORDS = {
    "governance.OfficialAppointment": ("effective_from", "effective_to", "is_current"),
    "governance.CommitteeMember": ("joined_date", "left_date", "is_active"),
    "culture.TraditionalTitleAppointment": ("effective_from", "effective_to", "is_current"),
    "population.Household": ("effective_from", "effective_to", "is_active"),
}


def record_village(instance):
    label = instance._meta.label
    if label == "governance.CommitteeMember":
        return instance.committee.village
    if label == "culture.TraditionalTitleAppointment":
        return instance.title.traditional_unit.village
    return instance.village


def require_master_editor(user, village):
    if not user_has_any_role(user, MASTER_EDITOR_ROLES):
        raise PermissionDenied("Your role cannot change historical master data.")
    if not villages_for_user(user).filter(pk=village.pk).exists():
        raise PermissionDenied("You are not assigned to this village.")


def supports_close_and_replace(instance):
    return instance._meta.label in EFFECTIVE_RECORDS


def _clone_values(instance):
    values = {}
    excluded = {"id", "uuid", "created_at", "updated_at", "record_version"}
    for field in instance._meta.concrete_fields:
        if field.name in excluded or field.primary_key or field.auto_created:
            continue
        if isinstance(field, models.ForeignKey):
            values[field.name] = getattr(instance, field.name)
        else:
            values[field.name] = getattr(instance, field.name)
    return values


@transaction.atomic
def close_and_replace(*, current, user, changes):
    label = current._meta.label
    if label not in EFFECTIVE_RECORDS:
        raise ValidationError("This master record does not use effective-dated replacement.")
    model = type(current)
    locked = model._default_manager.select_for_update().get(pk=current.pk)
    village = record_village(locked)
    require_master_editor(user, village)
    start_field, end_field, current_field = EFFECTIVE_RECORDS[label]
    if not getattr(locked, current_field):
        raise ValidationError("Only the current record can be replaced.")
    new_start = changes.get(start_field)
    old_start = getattr(locked, start_field)
    if new_start is None or new_start <= old_start:
        raise ValidationError({start_field: f"Enter a date later than {old_start} to create the replacement record."})
    if label == "governance.OfficialAppointment" and not str(changes.get("change_reason", "")).strip():
        raise ValidationError({"change_reason": "Explain why the appointment is changing."})

    setattr(locked, end_field, new_start - timedelta(days=1))
    setattr(locked, current_field, False)
    locked.record_version += 1
    locked.full_clean()
    locked.save(update_fields=(end_field, current_field, "record_version", "updated_at"))

    replacement_values = _clone_values(locked)
    replacement_values.update(changes)
    replacement_values[end_field] = None
    replacement_values[current_field] = True
    replacement = model(**replacement_values)
    replacement.full_clean()
    replacement.save()
    record_event(
        actor=user,
        action=f"{label}.replaced",
        instance=replacement,
        summary=f"Replaced effective-dated {label}",
        metadata={"previous_uuid": str(locked.uuid), "effective_from": str(new_start)},
    )
    return replacement
