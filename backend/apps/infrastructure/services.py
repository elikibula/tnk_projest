from django.core.exceptions import ValidationError
from django.db import transaction

from apps.audit.services import record_event
from apps.core.historical import require_master_editor

from .models import AssetMovement, VillageAsset, VillageEnergyAsset, VillageWaterSource


def _clone_values(instance):
    excluded = {"id", "uuid", "created_at", "updated_at", "record_version"}
    values = {}
    for field in instance._meta.concrete_fields:
        if field.name in excluded or field.primary_key or field.auto_created:
            continue
        values[field.name] = getattr(instance, field.name)
    return values


@transaction.atomic
def _replace_lifecycle_record(*, current, user, effective_date, reason, changes):
    model = type(current)
    locked = model._default_manager.select_for_update().get(pk=current.pk)
    require_master_editor(user, locked.village)
    if not locked.is_active:
        raise ValidationError("Only an active master record can be replaced.")
    if not reason.strip():
        raise ValidationError("A replacement reason is required.")
    locked.is_active = False
    locked.record_version += 1
    locked.save(update_fields=("is_active", "record_version", "updated_at"))
    values = _clone_values(locked)
    values.update(changes)
    values["is_active"] = True
    replacement = model(**values)
    replacement.full_clean()
    replacement.save()
    record_event(
        actor=user,
        action=f"{locked._meta.label}.replaced",
        instance=replacement,
        summary=f"Replaced {locked._meta.verbose_name}",
        metadata={"previous_uuid": str(locked.uuid), "effective_date": str(effective_date), "reason": reason},
    )
    return locked, replacement


def replace_village_asset(*, current: VillageAsset, user, effective_date, reason, **changes):
    old, replacement = _replace_lifecycle_record(current=current, user=user, effective_date=effective_date, reason=reason, changes=changes)
    AssetMovement.objects.create(
        asset=old,
        movement_type="replacement",
        movement_date=effective_date,
        old_quantity=old.quantity,
        new_quantity=replacement.quantity,
        old_condition=old.condition,
        new_condition=replacement.condition,
        reason=reason,
    )
    return replacement


def replace_water_source(*, current: VillageWaterSource, user, effective_date, reason, **changes):
    return _replace_lifecycle_record(current=current, user=user, effective_date=effective_date, reason=reason, changes=changes)[1]


def replace_energy_asset(*, current: VillageEnergyAsset, user, effective_date, reason, **changes):
    return _replace_lifecycle_record(current=current, user=user, effective_date=effective_date, reason=reason, changes=changes)[1]
