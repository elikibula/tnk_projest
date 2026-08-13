from django.core.exceptions import ValidationError
from django.db import transaction

from apps.audit.services import record_event
from apps.core.historical import close_and_replace, require_master_editor

from .models import TraditionalTitle, TraditionalTitleAppointment


def replace_traditional_title_appointment(*, current: TraditionalTitleAppointment, user, **changes):
    return close_and_replace(current=current, user=user, changes=changes)


@transaction.atomic
def update_traditional_title_state(*, title: TraditionalTitle, user, effective_date, reason, **changes):
    locked = TraditionalTitle.objects.select_for_update().get(pk=title.pk)
    require_master_editor(user, locked.traditional_unit.village)
    if not reason.strip():
        raise ValidationError("A title-state change reason is required.")
    allowed = {"status", "vacancy_start_date", "confirmation_stage", "confirmation_date", "next_action", "responsible_party"}
    for field, value in changes.items():
        if field not in allowed:
            raise ValidationError(f"{field} cannot be changed through the title-state service.")
        setattr(locked, field, value)
    locked.record_version += 1
    locked.full_clean()
    locked.save(update_fields=(*changes.keys(), "record_version", "updated_at"))
    record_event(actor=user, action="culture.TraditionalTitle.state_changed", instance=locked, summary="Changed traditional title state", metadata={"effective_date": str(effective_date), "reason": reason})
    return locked
