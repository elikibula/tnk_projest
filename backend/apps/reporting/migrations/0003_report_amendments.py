import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("analytics", "0002_indicator_catalogue_and_value_metadata"),
        ("reporting", "0002_reportmastersnapshot_and_capture_time"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ReportAmendment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("uuid", models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ("amendment_number", models.PositiveIntegerField()),
                ("reason", models.TextField()),
                ("requested_at", models.DateTimeField(auto_now_add=True)),
                ("submitted_at", models.DateTimeField(blank=True, null=True)),
                ("approved_at", models.DateTimeField(blank=True, null=True)),
                ("rejected_at", models.DateTimeField(blank=True, null=True)),
                ("status", models.CharField(choices=[("draft", "Draft"), ("submitted", "Submitted"), ("approved", "Approved"), ("rejected", "Rejected"), ("withdrawn", "Withdrawn")], default="draft", max_length=20)),
                ("supersedes_previous", models.BooleanField(default=False)),
                ("notes", models.TextField(blank=True)),
                ("review_comment", models.TextField(blank=True)),
                ("record_version", models.PositiveIntegerField(default=1)),
                ("approved_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="approved_report_amendments", to=settings.AUTH_USER_MODEL)),
                ("original_report", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="amendments", to="reporting.tnkreport")),
                ("rejected_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="rejected_report_amendments", to=settings.AUTH_USER_MODEL)),
                ("requested_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="requested_report_amendments", to=settings.AUTH_USER_MODEL)),
                ("supersedes_amendment", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="superseded_by", to="reporting.reportamendment")),
            ],
            options={"ordering": ("original_report", "amendment_number")},
        ),
        migrations.CreateModel(
            name="ReportAmendmentChange",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("uuid", models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ("section_code", models.CharField(max_length=40)),
                ("entry_key", models.CharField(max_length=50)),
                ("source_model", models.CharField(max_length=120)),
                ("source_identifier", models.CharField(max_length=80)),
                ("field_name", models.CharField(max_length=120)),
                ("field_label", models.CharField(max_length=180)),
                ("original_value", models.JSONField(blank=True, null=True)),
                ("amended_value", models.JSONField(blank=True, null=True)),
                ("change_reason", models.TextField()),
                ("affects_analytics", models.BooleanField(default=False)),
                ("original_indicator_value", models.DecimalField(blank=True, decimal_places=4, max_digits=18, null=True)),
                ("amended_indicator_value", models.DecimalField(blank=True, decimal_places=4, max_digits=18, null=True)),
                ("original_indicator_numerator", models.DecimalField(blank=True, decimal_places=4, max_digits=18, null=True)),
                ("amended_indicator_numerator", models.DecimalField(blank=True, decimal_places=4, max_digits=18, null=True)),
                ("original_indicator_denominator", models.DecimalField(blank=True, decimal_places=4, max_digits=18, null=True)),
                ("amended_indicator_denominator", models.DecimalField(blank=True, decimal_places=4, max_digits=18, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("amendment", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="changes", to="reporting.reportamendment")),
                ("created_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="created_amendment_changes", to=settings.AUTH_USER_MODEL)),
                ("indicator", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="amendment_changes", to="analytics.indicatordefinition")),
            ],
            options={"ordering": ("pk",)},
        ),
        migrations.AddConstraint(model_name="reportamendment", constraint=models.UniqueConstraint(fields=("original_report", "amendment_number"), name="unique_report_amendment_number")),
        migrations.AddConstraint(model_name="reportamendmentchange", constraint=models.UniqueConstraint(fields=("amendment", "section_code", "entry_key", "source_identifier", "field_name"), name="unique_amendment_record_field_change")),
        migrations.AddConstraint(model_name="reportamendmentchange", constraint=models.UniqueConstraint(condition=models.Q(("indicator__isnull", False)), fields=("amendment", "indicator"), name="unique_amendment_indicator_override")),
    ]
