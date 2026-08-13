import uuid
from django.conf import settings
from django.db import models
class IndicatorDefinition(models.Model):
    class ImplementationStatus(models.TextChoices):
        AVAILABLE = "available", "Available"
        UNAVAILABLE = "unavailable", "Unavailable with current data model"
    code=models.CharField(max_length=80); name_en=models.CharField(max_length=160); name_fj=models.CharField(max_length=160,blank=True); description=models.TextField(); numerator_definition=models.TextField(blank=True); denominator_definition=models.TextField(blank=True); formula_description=models.TextField(); measurement_unit=models.CharField(max_length=40); frequency=models.CharField(max_length=40,default="quarterly"); geographic_level=models.CharField(max_length=30); data_source=models.TextField(blank=True); disaggregation=models.TextField(blank=True); missing_value_rule=models.TextField(blank=True); verification_requirement=models.TextField(blank=True); implementation_status=models.CharField(max_length=20,choices=ImplementationStatus.choices,default=ImplementationStatus.AVAILABLE); unavailable_reason=models.TextField(blank=True); version=models.PositiveIntegerField(default=1); effective_from=models.DateField(); is_active=models.BooleanField(default=True)
    class Meta:
        constraints=[models.UniqueConstraint(fields=("code","version"),name="unique_indicator_code_version"),models.UniqueConstraint(fields=("code",),condition=models.Q(is_active=True),name="unique_active_indicator_code")]
        ordering=("code","-version")
class IndicatorValue(models.Model):
    class CalculationStatus(models.TextChoices):
        CALCULATED = "calculated", "Calculated"
        NO_DATA = "no_data", "No data"
        UNAVAILABLE = "unavailable", "Unavailable"
    uuid=models.UUIDField(default=uuid.uuid4,editable=False,unique=True); indicator=models.ForeignKey(IndicatorDefinition,on_delete=models.PROTECT,related_name="values"); reporting_period=models.ForeignKey("reporting.ReportingPeriod",on_delete=models.PROTECT); province=models.ForeignKey("locations.Province",null=True,blank=True,on_delete=models.PROTECT); tikina=models.ForeignKey("locations.Tikina",null=True,blank=True,on_delete=models.PROTECT); village=models.ForeignKey("locations.Village",null=True,blank=True,on_delete=models.PROTECT); value=models.DecimalField(max_digits=18,decimal_places=4,null=True); numerator_value=models.DecimalField(max_digits=18,decimal_places=4,null=True,blank=True); denominator_value=models.DecimalField(max_digits=18,decimal_places=4,null=True,blank=True); breakdown=models.JSONField(default=dict,blank=True); calculation_status=models.CharField(max_length=20,choices=CalculationStatus.choices,default=CalculationStatus.CALCULATED); calculation_notes=models.TextField(blank=True); source_report_count=models.PositiveIntegerField(default=1); calculated_at=models.DateTimeField(auto_now=True); data_quality_rating=models.CharField(max_length=20,default="unknown")
    class Meta:
        constraints=[
            models.UniqueConstraint(fields=("indicator","reporting_period","village"),condition=models.Q(village__isnull=False),name="unique_village_indicator_value"),
            models.UniqueConstraint(fields=("indicator","reporting_period","tikina"),condition=models.Q(village__isnull=True,tikina__isnull=False),name="unique_tikina_indicator_value"),
            models.UniqueConstraint(fields=("indicator","reporting_period","province"),condition=models.Q(village__isnull=True,tikina__isnull=True,province__isnull=False),name="unique_province_indicator_value"),
        ]
class DataExportAudit(models.Model):
    uuid=models.UUIDField(default=uuid.uuid4,editable=False,unique=True); generated_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT); generated_at=models.DateTimeField(auto_now_add=True); report_type=models.CharField(max_length=80); filters_used=models.JSONField(default=dict); number_of_records=models.PositiveIntegerField(); export_reason=models.TextField(blank=True); format=models.CharField(max_length=10)
class DataDictionaryEntry(models.Model):
    field_code=models.CharField(max_length=120,unique=True); label_en=models.CharField(max_length=180); label_fj=models.CharField(max_length=180,blank=True); definition_en=models.TextField(); definition_fj=models.TextField(blank=True); data_type=models.CharField(max_length=40); allowed_values=models.TextField(blank=True); measurement_unit=models.CharField(max_length=40,blank=True); required_status=models.CharField(max_length=30); data_source=models.CharField(max_length=80,blank=True); update_frequency=models.CharField(max_length=40); validation_rule=models.TextField(blank=True); confidentiality_level=models.CharField(max_length=30)
