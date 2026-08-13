import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class TNKReportQuerySet(models.QuerySet):
    def delete(self):
        if self.filter(status__in=(TNKReport.Status.APPROVED, TNKReport.Status.LOCKED, TNKReport.Status.ARCHIVED)).exists():
            raise ValidationError("Official report history cannot be deleted. Archive the report instead.")
        return super().delete()


class TNKReport(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        READY_FOR_VALIDATION = "ready_for_validation", "Ready for validation"
        SUBMITTED = "submitted", "Submitted"
        UNDER_TIKINA_REVIEW = "under_tikina_review", "Under Tikina review"
        RETURNED_TO_VILLAGE = "returned_to_village", "Returned to village"
        UNDER_PROVINCIAL_REVIEW = "under_provincial_review", "Under provincial review"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        LOCKED = "locked", "Locked"
        ARCHIVED = "archived", "Archived"

    class RiskLevel(models.TextChoices):
        UNKNOWN = "unknown", "Unknown"
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    village = models.ForeignKey("locations.Village", on_delete=models.PROTECT, related_name="tnk_reports")
    reporting_period = models.ForeignKey("reporting.ReportingPeriod", on_delete=models.PROTECT, related_name="reports")
    previous_report = models.ForeignKey("self", null=True, blank=True, on_delete=models.PROTECT, related_name="subsequent_reports")
    status = models.CharField(max_length=40, choices=Status.choices, default=Status.DRAFT, db_index=True)
    prepared_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="prepared_tnk_reports")
    collection_started_at = models.DateTimeField()
    submitted_at = models.DateTimeField(null=True, blank=True)
    district_reviewed_at = models.DateTimeField(null=True, blank=True)
    provincial_reviewed_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    locked_at = models.DateTimeField(null=True, blank=True)
    completeness_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    data_quality_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    verification_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    timeliness_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    evidence_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    overall_risk_level = models.CharField(max_length=20, choices=RiskLevel.choices, default=RiskLevel.UNKNOWN)
    roko_veivuke_comment = models.TextField(blank=True)
    provincial_comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    record_version = models.PositiveIntegerField(default=1)
    master_snapshot_captured_at = models.DateTimeField(null=True, blank=True, editable=False)

    objects = TNKReportQuerySet.as_manager()

    class Meta:
        ordering = ("-reporting_period__year", "-reporting_period__quarter", "village__name_en")
        constraints = [models.UniqueConstraint(fields=("village", "reporting_period"), name="unique_village_reporting_period")]
        indexes = [models.Index(fields=("status", "reporting_period"), name="report_status_period_idx")]

    @property
    def is_editable(self):
        return self.status in (self.Status.DRAFT, self.Status.RETURNED_TO_VILLAGE)

    def save(self, *args, **kwargs):
        update_fields = kwargs.get("update_fields")
        status_may_change = update_fields is None or "status" in update_fields
        if self.pk and status_may_change and not getattr(self, "_workflow_transition_authorized", False):
            previous_status = type(self).objects.filter(pk=self.pk).values_list("status", flat=True).first()
            if previous_status is not None and previous_status != self.status:
                raise ValidationError("Report status can only be changed through the workflow service.")
        return super().save(*args, **kwargs)

    def clean(self):
        errors = {}
        if self.previous_report_id:
            if self.previous_report_id == self.pk:
                errors["previous_report"] = "A report cannot refer to itself."
            elif self.previous_report.village_id != self.village_id:
                errors["previous_report"] = "Previous report must belong to the same village."
            elif self.previous_report.reporting_period.start_date >= self.reporting_period.start_date:
                errors["previous_report"] = "Previous report must be from an earlier reporting period."
            elif self.previous_report.status not in (self.Status.APPROVED, self.Status.LOCKED, self.Status.ARCHIVED):
                errors["previous_report"] = "Previous report must be approved, locked, or archived."
        if errors:
            raise ValidationError(errors)

    def delete(self, *args, **kwargs):
        if self.status in (self.Status.APPROVED, self.Status.LOCKED, self.Status.ARCHIVED):
            raise ValidationError("Official report history cannot be deleted. Archive the report instead.")
        return super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.village} - {self.reporting_period}"
