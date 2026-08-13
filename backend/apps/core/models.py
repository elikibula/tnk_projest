import uuid
from django.conf import settings
from django.db import models

class UUIDTimeStampedModel(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    record_version = models.PositiveIntegerField(default=1)
    class Meta:
        abstract = True

class AnalyticalRecord(UUIDTimeStampedModel):
    class VerificationStatus(models.TextChoices):
        UNVERIFIED = "unverified", "Unverified"
        PENDING = "pending_verification", "Pending verification"
        VERIFIED = "verified", "Verified"
        DISPUTED = "disputed", "Disputed"
        REJECTED = "rejected", "Rejected"
    class ConfidenceLevel(models.TextChoices):
        HIGH = "high", "High"
        MEDIUM = "medium", "Medium"
        LOW = "low", "Low"
        UNKNOWN = "unknown", "Unknown"
    class DataSource(models.TextChoices):
        PHYSICAL_COUNT = "physical_count", "Physical count"
        HOUSEHOLD_REGISTER = "household_register", "Household register"
        VILLAGE_REGISTER = "village_register", "Village register"
        COMMITTEE_REGISTER = "committee_register", "Committee register"
        VILLAGE_NURSE = "village_nurse", "Village nurse"
        POLICE_RECORD = "police_record", "Police record"
        GOVERNMENT = "government_department", "Government department"
        INTERVIEW = "interview", "Interview"
        ESTIMATE = "estimate", "Estimate"
        OTHER = "other", "Other"
    measurement_date = models.DateField()
    measurement_unit = models.CharField(max_length=40, blank=True)
    data_source = models.CharField(max_length=40, choices=DataSource.choices)
    collection_method = models.CharField(max_length=80)
    source_reference = models.CharField(max_length=255, blank=True)
    verification_status = models.CharField(max_length=30, choices=VerificationStatus.choices, default=VerificationStatus.UNVERIFIED)
    verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT, related_name="verified_%(app_label)s_%(class)s_records")
    verified_at = models.DateTimeField(null=True, blank=True)
    confidence_level = models.CharField(max_length=20, choices=ConfidenceLevel.choices, default=ConfidenceLevel.UNKNOWN)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT, related_name="created_%(app_label)s_%(class)s_records")
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT, related_name="updated_%(app_label)s_%(class)s_records")
    class Meta: abstract = True
