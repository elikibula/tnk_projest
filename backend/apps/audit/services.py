from .models import AuditEvent


def _event_location(instance):
    village = getattr(instance, "village", None)
    tikina = getattr(instance, "tikina", None)
    province = getattr(instance, "province", None)
    if village is None and tikina is None and province is None:
        from apps.core.security import village_for_record

        village = village_for_record(instance)
    if village is not None:
        tikina = village.tikina
        province = tikina.province
    elif tikina is not None:
        province = tikina.province
    return province, tikina, village


def record_event(
    *,
    actor,
    action: str,
    instance,
    summary: str,
    metadata: dict | None = None,
    ip_address=None,
    user_agent="",
) -> AuditEvent:
    details = dict(metadata or {})
    if ip_address is not None:
        details["ip_address"] = ip_address
    if user_agent:
        details["user_agent"] = user_agent
    province, tikina, village = _event_location(instance)
    return AuditEvent.objects.create(
        actor=actor,
        action=action,
        object_type=instance._meta.label,
        object_uuid=getattr(instance, "uuid", None),
        summary=summary,
        metadata=details,
        province=province,
        tikina=tikina,
        village=village,
    )
