from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.audit.services import record_event
from apps.core.historical import close_and_replace, require_master_editor

from .models import CommitteeMember, OfficialAppointment, VillageCommittee


def replace_official_appointment(*, current: OfficialAppointment, user, **changes):
    return close_and_replace(current=current, user=user, changes=changes)


def replace_committee_member(*, current: CommitteeMember, user, **changes):
    return close_and_replace(current=current, user=user, changes=changes)


@transaction.atomic
def replace_committee(*, current: VillageCommittee, user, formed_date, reason, **changes):
    locked = VillageCommittee.objects.select_for_update().get(pk=current.pk)
    require_master_editor(user, locked.village)
    if not locked.is_active:
        raise ValidationError("Only an active committee can be replaced.")
    if not reason.strip():
        raise ValidationError("A committee replacement reason is required.")
    if locked.formed_date and formed_date <= locked.formed_date:
        raise ValidationError({"formed_date": "Replacement committee date must follow the original formation date."})
    locked.dissolved_date = formed_date - timedelta(days=1)
    locked.is_active = False
    locked.record_version += 1
    locked.full_clean()
    locked.save(update_fields=("dissolved_date", "is_active", "record_version", "updated_at"))
    values = {
        "village": locked.village,
        "committee_type": locked.committee_type,
        "name": locked.name,
        "formed_date": formed_date,
        "mandate": locked.mandate,
        "chairperson": locked.chairperson,
        "secretary": locked.secretary,
        "constitution_available": locked.constitution_available,
        "annual_plan_available": locked.annual_plan_available,
        "bank_account_available": locked.bank_account_available,
        "is_active": True,
    }
    values.update(changes)
    replacement = VillageCommittee(**values)
    replacement.full_clean()
    replacement.save()
    record_event(actor=user, action="governance.VillageCommittee.replaced", instance=replacement, summary="Replaced village committee", metadata={"previous_uuid": str(locked.uuid), "reason": reason})
    return replacement
