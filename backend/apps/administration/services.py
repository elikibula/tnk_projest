from apps.audit.services import record_event


def request_metadata(request):
    return {"ip_address": request.META.get("REMOTE_ADDR"), "user_agent": request.META.get("HTTP_USER_AGENT", "")}


def snapshot_user(user):
    role = user.role_assignments.filter(is_active=True).select_related("role").first()
    location = user.location_assignments.filter(is_active=True).first()
    return {
        "username": user.username,
        "email": user.email,
        "name": user.get_full_name(),
        "is_active": user.is_active,
        "role": role.role.code if role else None,
        "province_id": location.province_id if location else None,
        "tikina_id": location.tikina_id if location else None,
        "village_id": location.village_id if location else None,
    }


def audit_change(request, action, instance, summary, previous=None, current=None):
    return record_event(
        actor=request.user,
        action=action,
        instance=instance,
        summary=summary,
        metadata={"previous": previous, "new": current, **request_metadata(request)},
    )

