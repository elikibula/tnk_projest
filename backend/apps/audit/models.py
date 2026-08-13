import uuid
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class AuditEventQuerySet(models.QuerySet):
    def update(self, **kwargs):
        raise ValidationError("Audit events are immutable.")

    def delete(self):
        raise ValidationError("Audit events are immutable.")


class AuditEvent(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=80)
    object_type = models.CharField(max_length=120)
    object_uuid = models.UUIDField(null=True, blank=True)
    summary = models.CharField(max_length=255)
    metadata = models.JSONField(default=dict, blank=True)
    province = models.ForeignKey("locations.Province", null=True, blank=True, on_delete=models.PROTECT, related_name="audit_events")
    tikina = models.ForeignKey("locations.Tikina", null=True, blank=True, on_delete=models.PROTECT, related_name="audit_events")
    village = models.ForeignKey("locations.Village", null=True, blank=True, on_delete=models.PROTECT, related_name="audit_events")
    occurred_at = models.DateTimeField(auto_now_add=True, db_index=True)
    objects = AuditEventQuerySet.as_manager()
    class Meta: ordering = ("-occurred_at",)

    def save(self, *args, **kwargs):
        if self.pk:
            raise ValidationError("Audit events are immutable.")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("Audit events are immutable.")
