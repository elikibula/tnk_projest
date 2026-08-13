from django.core.exceptions import ValidationError
from django.db import models
from apps.core.models import AnalyticalRecord
from apps.core.validation import validate_subcounts
class HealthCondition(models.Model):
    code=models.CharField(max_length=50,unique=True); name_en=models.CharField(max_length=120); name_fj=models.CharField(max_length=120,blank=True); category=models.CharField(max_length=80); is_communicable=models.BooleanField(default=False); is_active=models.BooleanField(default=True)
    def __str__(self): return self.name_en
class HealthConditionSnapshot(AnalyticalRecord):
    report=models.ForeignKey("reporting.TNKReport",on_delete=models.PROTECT,related_name="health_snapshots"); health_condition=models.ForeignKey(HealthCondition,on_delete=models.PROTECT); age_group=models.ForeignKey("population.AgeGroup",on_delete=models.PROTECT); gender=models.CharField(max_length=30); new_cases=models.PositiveIntegerField(null=True,blank=True); existing_cases=models.PositiveIntegerField(null=True,blank=True); referred_cases=models.PositiveIntegerField(null=True,blank=True); hospitalised_cases=models.PositiveIntegerField(null=True,blank=True); recovered_cases=models.PositiveIntegerField(null=True,blank=True); deaths=models.PositiveIntegerField(null=True,blank=True)
    def clean(self):
        total = (self.new_cases or 0) + (self.existing_cases or 0)
        validate_subcounts(total, referred_cases=self.referred_cases, hospitalised_cases=self.hospitalised_cases, recovered_cases=self.recovered_cases, deaths=self.deaths)
class VillageHealthAccessSnapshot(AnalyticalRecord):
    report=models.OneToOneField("reporting.TNKReport",on_delete=models.PROTECT,related_name="health_access_snapshot"); village_nurse_available=models.BooleanField(null=True,blank=True); nurse_visits_count=models.PositiveIntegerField(null=True,blank=True); health_team_visits_count=models.PositiveIntegerField(null=True,blank=True); nearest_health_facility=models.CharField(max_length=160,blank=True); travel_time_minutes=models.PositiveIntegerField(null=True,blank=True); transport_available=models.BooleanField(null=True,blank=True); medicine_shortage_days=models.PositiveIntegerField(null=True,blank=True); emergency_referrals_count=models.PositiveIntegerField(null=True,blank=True)
class DisabilityType(models.Model):
    code=models.CharField(max_length=50,unique=True); name_en=models.CharField(max_length=120); name_fj=models.CharField(max_length=120,blank=True); category=models.CharField(max_length=80); is_active=models.BooleanField(default=True)
    def __str__(self): return self.name_en
class DisabilitySnapshot(AnalyticalRecord):
    report=models.ForeignKey("reporting.TNKReport",on_delete=models.PROTECT,related_name="disability_snapshots"); disability_type=models.ForeignKey(DisabilityType,on_delete=models.PROTECT); age_group=models.ForeignKey("population.AgeGroup",on_delete=models.PROTECT); gender=models.CharField(max_length=30); count=models.PositiveIntegerField(null=True,blank=True); receiving_support_count=models.PositiveIntegerField(null=True,blank=True); attending_school_count=models.PositiveIntegerField(null=True,blank=True); employed_count=models.PositiveIntegerField(null=True,blank=True); support_required=models.TextField(blank=True)
    def clean(self):
        validate_subcounts(self.count, receiving_support_count=self.receiving_support_count, attending_school_count=self.attending_school_count, employed_count=self.employed_count)
class OffenceType(models.Model):
    code=models.CharField(max_length=50,unique=True); category=models.CharField(max_length=80); name_en=models.CharField(max_length=120); name_fj=models.CharField(max_length=120,blank=True); default_severity=models.CharField(max_length=20); is_active=models.BooleanField(default=True)
    def __str__(self): return self.name_en
class CommunitySafetyIncident(AnalyticalRecord):
    village=models.ForeignKey("locations.Village",on_delete=models.PROTECT,related_name="safety_incidents"); report=models.ForeignKey("reporting.TNKReport",on_delete=models.PROTECT,related_name="safety_incidents"); offence_type=models.ForeignKey(OffenceType,on_delete=models.PROTECT); incident_date=models.DateField(); number_of_incidents=models.PositiveIntegerField(); severity=models.CharField(max_length=20); victim_age_group=models.ForeignKey("population.AgeGroup",null=True,blank=True,on_delete=models.PROTECT); victim_gender=models.CharField(max_length=30,blank=True); reported_to_authority=models.BooleanField(null=True,blank=True); authority_reported_to=models.CharField(max_length=120,blank=True); report_date=models.DateField(null=True,blank=True); action_taken=models.TextField(blank=True); case_status=models.CharField(max_length=40,blank=True); reason_not_reported=models.TextField(blank=True)
    def clean(self):
        errors = {}
        if self.reported_to_authority is False and not self.reason_not_reported.strip():
            errors["reason_not_reported"] = "Explain why the incident was not reported."
        if self.reported_to_authority is True and not self.authority_reported_to.strip():
            errors["authority_reported_to"] = "Enter the authority the incident was reported to."
        if self.report_date and self.report_date < self.incident_date:
            errors["report_date"] = "Report date cannot precede the incident date."
        if errors:
            raise ValidationError(errors)
