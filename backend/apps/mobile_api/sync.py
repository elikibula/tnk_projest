import hashlib
import json
import uuid
from datetime import timedelta

from django.core import signing
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone

from apps.core.security import can_view_entry, permitted_section_codes
from apps.reporting.forms import build_entry_form
from apps.reporting.section_entries import entry_queryset, save_entry
from apps.reporting.section_registry import get_entry_config, SECTION_ENTRIES
from apps.reporting.selectors import reports_for_user

from .models import ApiIdempotencyRecord, MobileChangeLog


MAX_BATCH_RECORDS = 100
MAX_CHANGES = 1000


def encode_cursor(sequence=0, updated_at=None, *, cutoff=None, offset=0):
    return signing.dumps(
        {
            "s": sequence,
            "t": updated_at.isoformat() if updated_at else None,
            "c": cutoff.isoformat() if cutoff else None,
            "o": offset,
        },
        salt="mobile-sync-v1",
        compress=True,
    )


def decode_cursor(value):
    if not value:
        return 0, None, None, 0
    payload = signing.loads(value, salt="mobile-sync-v1", max_age=60 * 60 * 24 * 30)
    # Accept Phase 7 cursors while migrating devices to the paged cursor.
    since_value = payload.get("t")
    cutoff_value = payload.get("c")
    return (
        int(payload["s"]),
        timezone.datetime.fromisoformat(since_value) if since_value else None,
        timezone.datetime.fromisoformat(cutoff_value) if cutoff_value else None,
        int(payload.get("o", 0)),
    )


def serialize_value(value):
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(getattr(value, "uuid", getattr(value, "pk", value)))


def serialize_entry(config, instance, report, section_code):
    return {
        "resource_type": config.key,
        "section_code": section_code,
        "report_uuid": str(report.uuid),
        "server_uuid": str(getattr(instance, "uuid", instance.pk)),
        "record_version": getattr(instance, "record_version", 1),
        "server_updated_at": getattr(instance, "updated_at", timezone.now()).isoformat(),
        "values": {name: serialize_value(getattr(instance, name)) for name in config.fields},
    }


def authoritative_changes(user, cursor):
    sequence, since, cursor_cutoff, offset = decode_cursor(cursor)
    cutoff = cursor_cutoff or timezone.now()
    changes = []
    allowed = permitted_section_codes(user)
    for report in reports_for_user(user).select_related("village", "reporting_period"):
        for section_code, configs in SECTION_ENTRIES.items():
            if section_code not in allowed:
                continue
            for config in configs:
                if not can_view_entry(user, section_code, config.model, report.village):
                    continue
                queryset = entry_queryset(config, report)
                if any(field.name == "updated_at" for field in config.model._meta.fields):
                    queryset = queryset.filter(updated_at__lte=cutoff)
                    if since is not None:
                        queryset = queryset.filter(updated_at__gt=since)
                for instance in queryset:
                    changes.append(serialize_entry(config, instance, report, section_code))
    changes.sort(key=lambda item: (item["server_updated_at"], item["resource_type"], item["server_uuid"]))
    page = changes[offset : offset + MAX_CHANGES]
    has_more = offset + MAX_CHANGES < len(changes)
    deletions = list(
        MobileChangeLog.objects.filter(user=user, sequence__gt=sequence, operation="delete")
        .order_by("sequence")
        .values("resource_type", "resource_uuid")[:MAX_CHANGES]
    )
    latest_sequence = (
        MobileChangeLog.objects.filter(user=user).order_by("-sequence").values_list("sequence", flat=True).first() or sequence
    )
    server_time = cutoff
    next_cursor = (
        encode_cursor(sequence, since, cutoff=cutoff, offset=offset + len(page))
        if has_more
        else encode_cursor(latest_sequence, cutoff)
    )
    return {
        "next_cursor": next_cursor,
        "changes": page,
        "deletions": deletions,
        "server_time": server_time,
        "has_more": has_more,
    }


def request_hash(item):
    return hashlib.sha256(json.dumps(item, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _form_values(config, report, values):
    converted = dict(values)
    for field_name in config.fields:
        field = config.model._meta.get_field(field_name)
        if not field.is_relation or not converted.get(field_name):
            continue
        related = field.remote_field.model
        if any(candidate.name == "uuid" for candidate in related._meta.fields):
            converted[field_name] = related._default_manager.only("pk").get(uuid=converted[field_name]).pk
    return converted


@transaction.atomic
def apply_change(*, user, device, item):
    try:
        idem_key = uuid.UUID(str(item["idempotency_key"]))
    except (KeyError, TypeError, ValueError):
        return {"status": "failed", "code": "invalid_request", "local_uuid": item.get("local_uuid")}
    digest = request_hash(item)
    replay = ApiIdempotencyRecord.objects.filter(user=user, device=device, key=idem_key).first()
    if replay:
        if replay.request_hash != digest:
            return {"status": "failed", "code": "idempotency_mismatch", "local_uuid": item.get("local_uuid")}
        return replay.response_body

    result = _apply_change_once(user=user, device=device, item=item)
    ApiIdempotencyRecord.objects.create(
        user=user,
        device=device,
        key=idem_key,
        endpoint="sync/batch",
        request_hash=digest,
        response_status=200,
        response_body=result,
        expires_at=timezone.now() + timedelta(days=30),
    )
    return result


def _apply_change_once(*, user, device, item):
    local_uuid = item.get("local_uuid")
    try:
        report = reports_for_user(user).select_related("village", "reporting_period").get(uuid=item["report_uuid"])
        section_code = item["section_code"]
        config = get_entry_config(section_code, item["resource_type"])
        if config is None or not can_view_entry(user, section_code, config.model, report.village):
            raise PermissionDenied("This entry type is not authorised.")
        operation = item["operation"]
        if operation == "delete":
            return {"status": "failed", "code": "delete_not_supported", "local_uuid": local_uuid}
        instance = None
        if operation == "update":
            lookup = {"uuid": item["server_uuid"]} if any(field.name == "uuid" for field in config.model._meta.fields) else {"pk": item["server_uuid"]}
            instance = entry_queryset(config, report).get(**lookup)
            current_version = getattr(instance, "record_version", 1)
            expected = int(item.get("expected_record_version", 0))
            if current_version != expected:
                return {
                    "status": "conflict",
                    "code": "record_version_conflict",
                    "local_uuid": local_uuid,
                    "submitted_version": expected,
                    "server": serialize_entry(config, instance, report, section_code),
                    "server_value_required": not report.is_editable,
                }
        values = _form_values(config, report, item.get("values", {}))
        form = build_entry_form(config, report=report, data=values, instance=instance)
        if not form.is_valid():
            return {"status": "failed", "code": "validation_error", "local_uuid": local_uuid, "errors": form.errors.get_json_data()}
        if instance is None and hasattr(form.instance, "uuid"):
            form.instance.uuid = uuid.UUID(str(local_uuid))
        saved = save_entry(config=config, report=report, section_code=section_code, form=form, user=user)
        payload = serialize_entry(config, saved, report, section_code)
        MobileChangeLog.objects.create(
            user=user,
            device=device,
            resource_type=config.key,
            resource_uuid=payload["server_uuid"],
            operation="upsert",
            payload=payload,
        )
        return {"status": "accepted", "local_uuid": local_uuid, "record": payload}
    except (KeyError, ValueError, TypeError, ObjectDoesNotExist):
        return {"status": "failed", "code": "invalid_request", "local_uuid": local_uuid}
    except PermissionDenied:
        return {"status": "failed", "code": "permission_denied", "local_uuid": local_uuid}
    except ValidationError as error:
        return {"status": "failed", "code": "validation_error", "local_uuid": local_uuid, "errors": error.message_dict if hasattr(error, "message_dict") else error.messages}
