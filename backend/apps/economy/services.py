from django.core.exceptions import ValidationError
from django.db import transaction

from apps.audit.services import record_event
from apps.core.historical import require_master_editor

from .models import BusinessMovement, VillageBusiness


BUSINESS_CHANGE_FIELDS = {
    "business_name",
    "business_sector",
    "owner_type",
    "owner_person",
    "owner_name",
    "owner_gender",
    "owner_age_group",
    "closure_date",
    "licence_status",
    "licence_expiry_date",
    "operating_status",
    "full_time_employees",
    "part_time_employees",
    "male_employees",
    "female_employees",
    "youth_employees",
    "revenue_band",
    "primary_market",
    "support_required",
    "is_active",
}


@transaction.atomic
def record_business_change(*, business: VillageBusiness, user, effective_date, reason, **changes):
    locked = VillageBusiness.objects.select_for_update().get(pk=business.pk)
    require_master_editor(user, locked.village)
    if not reason.strip():
        raise ValidationError("A business change reason is required.")
    unknown = set(changes) - BUSINESS_CHANGE_FIELDS
    if unknown:
        raise ValidationError(f"Unsupported business change fields: {', '.join(sorted(unknown))}.")
    old_status = locked.operating_status
    for field, value in changes.items():
        setattr(locked, field, value)
    locked.record_version += 1
    locked.full_clean()
    locked.save(update_fields=(*changes.keys(), "record_version", "updated_at"))
    BusinessMovement.objects.create(
        business=locked,
        movement_type="quarterly_master_change",
        movement_date=effective_date,
        old_status=old_status,
        new_status=locked.operating_status,
        reason=reason,
    )
    record_event(actor=user, action="economy.VillageBusiness.changed", instance=locked, summary="Changed village business master record", metadata={"effective_date": str(effective_date), "reason": reason})
    return locked
