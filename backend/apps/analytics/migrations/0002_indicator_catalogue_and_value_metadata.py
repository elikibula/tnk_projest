from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("analytics", "0001_initial")]

    operations = [
        migrations.AlterField(model_name="indicatordefinition", name="code", field=models.CharField(max_length=80)),
        migrations.AddField(model_name="indicatordefinition", name="data_source", field=models.TextField(blank=True)),
        migrations.AddField(model_name="indicatordefinition", name="disaggregation", field=models.TextField(blank=True)),
        migrations.AddField(model_name="indicatordefinition", name="implementation_status", field=models.CharField(choices=[("available", "Available"), ("unavailable", "Unavailable with current data model")], default="available", max_length=20)),
        migrations.AddField(model_name="indicatordefinition", name="missing_value_rule", field=models.TextField(blank=True)),
        migrations.AddField(model_name="indicatordefinition", name="unavailable_reason", field=models.TextField(blank=True)),
        migrations.AddField(model_name="indicatordefinition", name="verification_requirement", field=models.TextField(blank=True)),
        migrations.AddField(model_name="indicatorvalue", name="breakdown", field=models.JSONField(blank=True, default=dict)),
        migrations.AddField(model_name="indicatorvalue", name="calculation_notes", field=models.TextField(blank=True)),
        migrations.AddField(model_name="indicatorvalue", name="calculation_status", field=models.CharField(choices=[("calculated", "Calculated"), ("no_data", "No data"), ("unavailable", "Unavailable")], default="calculated", max_length=20)),
        migrations.AddField(model_name="indicatorvalue", name="source_report_count", field=models.PositiveIntegerField(default=1)),
        migrations.AddConstraint(model_name="indicatordefinition", constraint=models.UniqueConstraint(fields=("code", "version"), name="unique_indicator_code_version")),
        migrations.AddConstraint(model_name="indicatordefinition", constraint=models.UniqueConstraint(condition=models.Q(("is_active", True)), fields=("code",), name="unique_active_indicator_code")),
        migrations.AddConstraint(model_name="indicatorvalue", constraint=models.UniqueConstraint(condition=models.Q(("village__isnull", False)), fields=("indicator", "reporting_period", "village"), name="unique_village_indicator_value")),
        migrations.AddConstraint(model_name="indicatorvalue", constraint=models.UniqueConstraint(condition=models.Q(("tikina__isnull", False), ("village__isnull", True)), fields=("indicator", "reporting_period", "tikina"), name="unique_tikina_indicator_value")),
        migrations.AddConstraint(model_name="indicatorvalue", constraint=models.UniqueConstraint(condition=models.Q(("province__isnull", False), ("tikina__isnull", True), ("village__isnull", True)), fields=("indicator", "reporting_period", "province"), name="unique_province_indicator_value")),
        migrations.AlterModelOptions(name="indicatordefinition", options={"ordering": ("code", "-version")}),
    ]
