import uuid

from django.conf import settings
from django.db import models


class MobileDevice(models.Model):
    class Platform(models.TextChoices):
        ANDROID = "android", "Android"
        IOS = "ios", "iOS"

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="mobile_devices")
    device_identifier = models.UUIDField()
    platform = models.CharField(max_length=20, choices=Platform.choices)
    app_version = models.CharField(max_length=40)
    device_name = models.CharField(max_length=120, blank=True)
    registered_at = models.DateTimeField(auto_now_add=True)
    last_seen_at = models.DateTimeField(auto_now=True)
    last_sync_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    revoked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=("user", "device_identifier"), name="unique_mobile_installation_per_user")]
        indexes = [models.Index(fields=("user", "is_active"), name="mobile_device_active_idx")]

    def __str__(self):
        return f"{self.user} - {self.platform} - {self.device_identifier}"


class ApiIdempotencyRecord(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    device = models.ForeignKey(MobileDevice, on_delete=models.CASCADE)
    key = models.UUIDField()
    endpoint = models.CharField(max_length=120)
    request_hash = models.CharField(max_length=64)
    response_status = models.PositiveSmallIntegerField()
    response_body = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        constraints = [models.UniqueConstraint(fields=("user", "device", "key"), name="unique_mobile_idempotency_key")]
        indexes = [models.Index(fields=("expires_at",), name="mobile_idem_expiry_idx")]


class MobileChangeLog(models.Model):
    sequence = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    device = models.ForeignKey(MobileDevice, on_delete=models.CASCADE)
    resource_type = models.CharField(max_length=80)
    resource_uuid = models.CharField(max_length=80)
    operation = models.CharField(max_length=20)
    payload = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=("user", "sequence"), name="mobile_change_cursor_idx")]


class MobileSyncSession(models.Model):
    class Status(models.TextChoices):
        RUNNING = "running", "Running"
        COMPLETED = "completed", "Completed"
        PARTIAL = "partial", "Partial"
        FAILED = "failed", "Failed"

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    device = models.ForeignKey(MobileDevice, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    uploaded_count = models.PositiveIntegerField(default=0)
    downloaded_count = models.PositiveIntegerField(default=0)
    conflict_count = models.PositiveIntegerField(default=0)
    failed_count = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.RUNNING)
