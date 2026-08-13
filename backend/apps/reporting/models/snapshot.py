import uuid

from django.core.exceptions import ValidationError
from django.db import models


class ReportMasterSnapshotQuerySet(models.QuerySet):
    editable_statuses = ("draft", "returned_to_village")

    def bulk_create(self, objs, **kwargs):
        objs = list(objs)
        report_ids = {obj.report_id for obj in objs if obj.report_id}
        report_model = self.model._meta.get_field("report").remote_field.model
        if report_model.objects.filter(pk__in=report_ids).exclude(status__in=self.editable_statuses).exists():
            raise ValidationError("Master snapshots belonging to a frozen report are immutable.")
        return super().bulk_create(objs, **kwargs)

    def update(self, **kwargs):
        if self.exclude(report__status__in=self.editable_statuses).exists():
            raise ValidationError("Master snapshots belonging to a frozen report are immutable.")
        return super().update(**kwargs)

    def delete(self):
        if self.exclude(report__status__in=self.editable_statuses).exists():
            raise ValidationError("Master snapshots belonging to a frozen report are immutable.")
        return super().delete()


class ReportMasterSnapshot(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    report = models.ForeignKey(
        "reporting.TNKReport",
        on_delete=models.CASCADE,
        related_name="master_snapshots",
    )
    section_code = models.CharField(max_length=40)
    entry_key = models.CharField(max_length=50)
    source_model = models.CharField(max_length=120)
    source_identifier = models.CharField(max_length=80)
    summary = models.CharField(max_length=255)
    values = models.JSONField(default=dict)
    captured_at = models.DateTimeField(auto_now_add=True)

    objects = ReportMasterSnapshotQuerySet.as_manager()

    class Meta:
        ordering = ("section_code", "entry_key", "pk")
        constraints = [
            models.UniqueConstraint(
                fields=("report", "section_code", "entry_key", "source_identifier"),
                name="unique_report_master_snapshot",
            )
        ]
        indexes = [
            models.Index(
                fields=("report", "section_code", "entry_key"),
                name="master_snapshot_lookup_idx",
            )
        ]

    def save(self, *args, **kwargs):
        if not self.report.is_editable:
            raise ValidationError("Master snapshots belonging to a frozen report are immutable.")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if not self.report.is_editable:
            raise ValidationError("Master snapshots belonging to a frozen report are immutable.")
        return super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.report} — {self.summary}"
