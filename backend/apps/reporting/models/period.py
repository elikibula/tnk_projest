import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class ReportingPeriod(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    year = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(settings.TNK_REPORTING_MIN_YEAR),
            MaxValueValidator(settings.TNK_REPORTING_MAX_YEAR),
        ]
    )
    quarter = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(4)]
    )
    start_date = models.DateField()
    end_date = models.DateField()
    submission_due_date = models.DateField()
    is_open = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-year", "-quarter")
        constraints = [
            models.UniqueConstraint(fields=("year", "quarter"), name="unique_reporting_year_quarter"),
            models.CheckConstraint(condition=models.Q(quarter__gte=1, quarter__lte=4), name="valid_reporting_quarter"),
            models.CheckConstraint(condition=models.Q(start_date__lt=models.F("end_date")), name="period_start_before_end"),
            models.CheckConstraint(condition=models.Q(submission_due_date__gte=models.F("end_date")), name="period_due_on_or_after_end"),
        ]

    def clean(self):
        errors = {}
        if not settings.TNK_REPORTING_MIN_YEAR <= self.year <= settings.TNK_REPORTING_MAX_YEAR:
            errors["year"] = f"Year must be between {settings.TNK_REPORTING_MIN_YEAR} and {settings.TNK_REPORTING_MAX_YEAR}."
        if self.start_date and self.end_date and self.start_date >= self.end_date:
            errors["start_date"] = "Start date must be before end date."
        if self.submission_due_date and self.end_date and self.submission_due_date < self.end_date:
            errors["submission_due_date"] = "Submission due date must be on or after end date."
        if self.is_open and self.is_locked:
            errors["is_open"] = "A locked reporting period cannot be open."
        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"{self.year} Q{self.quarter}"
