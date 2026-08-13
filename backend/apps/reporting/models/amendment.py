import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class ReportAmendmentQuerySet(models.QuerySet):
    def delete(self):
        if self.exclude(status="draft").exists():
            raise ValidationError("Submitted amendment records are immutable.")
        return super().delete()


class ReportAmendment(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SUBMITTED = "submitted", "Submitted"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        WITHDRAWN = "withdrawn", "Withdrawn"

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    original_report = models.ForeignKey("reporting.TNKReport", on_delete=models.PROTECT, related_name="amendments")
    amendment_number = models.PositiveIntegerField()
    reason = models.TextField()
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="requested_report_amendments")
    requested_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT, related_name="approved_report_amendments")
    approved_at = models.DateTimeField(null=True, blank=True)
    rejected_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT, related_name="rejected_report_amendments")
    rejected_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    supersedes_previous = models.BooleanField(default=False)
    supersedes_amendment = models.ForeignKey("self", null=True, blank=True, on_delete=models.PROTECT, related_name="superseded_by")
    notes = models.TextField(blank=True)
    review_comment = models.TextField(blank=True)
    record_version = models.PositiveIntegerField(default=1)

    objects = ReportAmendmentQuerySet.as_manager()

    class Meta:
        ordering = ("original_report", "amendment_number")
        constraints = [
            models.UniqueConstraint(fields=("original_report", "amendment_number"), name="unique_report_amendment_number"),
        ]

    def clean(self):
        errors = {}
        if not self.reason.strip():
            errors["reason"] = "Explain why this official report needs an amendment."
        if self.supersedes_previous and self.supersedes_amendment is None:
            errors["supersedes_amendment"] = "Select the approved amendment being superseded."
        if self.supersedes_amendment_id:
            if self.supersedes_amendment.original_report_id != self.original_report_id:
                errors["supersedes_amendment"] = "An amendment can supersede only an amendment to the same report."
            elif self.supersedes_amendment.status != self.Status.APPROVED:
                errors["supersedes_amendment"] = "Only an approved amendment can be superseded."
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self.pk:
            previous = type(self).objects.filter(pk=self.pk).values("status").first()
            if previous and previous["status"] != self.Status.DRAFT:
                raise ValidationError("Submitted amendment records are immutable.")
            if previous and self.status != previous["status"]:
                raise ValidationError("Amendment status can change only through the amendment workflow service.")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.status != self.Status.DRAFT:
            raise ValidationError("Submitted amendment records are immutable.")
        return super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.original_report} — Amendment {self.amendment_number}"


class ReportAmendmentChangeQuerySet(models.QuerySet):
    def update(self, **kwargs):
        if self.exclude(amendment__status="draft").exists():
            raise ValidationError("Changes belonging to a submitted amendment are immutable.")
        return super().update(**kwargs)

    def delete(self):
        if self.exclude(amendment__status="draft").exists():
            raise ValidationError("Changes belonging to a submitted amendment are immutable.")
        return super().delete()


class ReportAmendmentChange(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    amendment = models.ForeignKey(ReportAmendment, on_delete=models.CASCADE, related_name="changes")
    section_code = models.CharField(max_length=40)
    entry_key = models.CharField(max_length=50)
    source_model = models.CharField(max_length=120)
    source_identifier = models.CharField(max_length=80)
    field_name = models.CharField(max_length=120)
    field_label = models.CharField(max_length=180)
    original_value = models.JSONField(null=True, blank=True)
    amended_value = models.JSONField(null=True, blank=True)
    change_reason = models.TextField()
    affects_analytics = models.BooleanField(default=False)
    indicator = models.ForeignKey("analytics.IndicatorDefinition", null=True, blank=True, on_delete=models.PROTECT, related_name="amendment_changes")
    original_indicator_value = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    amended_indicator_value = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    original_indicator_numerator = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    amended_indicator_numerator = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    original_indicator_denominator = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    amended_indicator_denominator = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="created_amendment_changes")
    created_at = models.DateTimeField(auto_now_add=True)

    objects = ReportAmendmentChangeQuerySet.as_manager()

    class Meta:
        ordering = ("pk",)
        constraints = [
            models.UniqueConstraint(
                fields=("amendment", "section_code", "entry_key", "source_identifier", "field_name"),
                name="unique_amendment_record_field_change",
            ),
            models.UniqueConstraint(
                fields=("amendment", "indicator"),
                condition=models.Q(indicator__isnull=False),
                name="unique_amendment_indicator_override",
            ),
        ]

    def clean(self):
        errors = {}
        if self.amendment_id and ReportAmendment.objects.filter(pk=self.amendment_id).exclude(
            status=ReportAmendment.Status.DRAFT
        ).exists():
            errors["amendment"] = "Changes can be edited only while the amendment is in draft."
        if self.original_value == self.amended_value:
            errors["amended_value"] = "The amended value must differ from the original value."
        if not self.change_reason.strip():
            errors["change_reason"] = "Explain this specific correction."
        if self.affects_analytics:
            if self.indicator_id is None or self.amended_indicator_value is None:
                errors["indicator"] = "Select an indicator and enter its amended value."
            if self.original_indicator_denominator is not None and (
                self.amended_indicator_numerator is None or self.amended_indicator_denominator is None
            ):
                errors["amended_indicator_denominator"] = "Rate and average overrides require an amended numerator and denominator."
        elif any(
            value is not None
            for value in (
                self.indicator_id,
                self.original_indicator_value,
                self.amended_indicator_value,
                self.original_indicator_numerator,
                self.amended_indicator_numerator,
                self.original_indicator_denominator,
                self.amended_indicator_denominator,
            )
        ):
            errors["affects_analytics"] = "Enable analytics impact before entering indicator values."
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self.amendment_id and ReportAmendment.objects.filter(pk=self.amendment_id).exclude(
            status=ReportAmendment.Status.DRAFT
        ).exists():
            raise ValidationError("Changes belonging to a submitted amendment are immutable.")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.amendment_id and ReportAmendment.objects.filter(pk=self.amendment_id).exclude(
            status=ReportAmendment.Status.DRAFT
        ).exists():
            raise ValidationError("Changes belonging to a submitted amendment are immutable.")
        return super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.field_label}: {self.original_value} → {self.amended_value}"
