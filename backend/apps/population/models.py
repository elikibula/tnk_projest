from django.core.exceptions import ValidationError
from django.db import models
from apps.core.models import AnalyticalRecord, UUIDTimeStampedModel
from apps.core.validation import validate_subcounts

class AgeGroup(models.Model):
    code = models.CharField(max_length=20, unique=True); name_en = models.CharField(max_length=50); name_fj = models.CharField(max_length=50, blank=True)
    minimum_age = models.PositiveSmallIntegerField(); maximum_age = models.PositiveSmallIntegerField(null=True, blank=True); sort_order = models.PositiveSmallIntegerField(default=0); is_active = models.BooleanField(default=True)
    class Meta: ordering = ("sort_order",)
    def __str__(self): return self.name_en

class PopulationSnapshot(AnalyticalRecord):
    RESIDENT_STATUSES = (("permanent_resident","Permanent resident"),("temporary_resident","Temporary resident"),("away_for_education","Away for education"),("away_for_employment","Away for employment"),("temporarily_absent","Temporarily absent"),("unknown","Unknown"))
    report = models.ForeignKey("reporting.TNKReport", on_delete=models.PROTECT, related_name="population_snapshots")
    village = models.ForeignKey("locations.Village", on_delete=models.PROTECT, related_name="population_snapshots")
    age_group = models.ForeignKey(AgeGroup, on_delete=models.PROTECT); gender = models.CharField(max_length=30); resident_status = models.CharField(max_length=30, choices=RESIDENT_STATUSES); count = models.PositiveIntegerField(null=True, blank=True)
    class Meta: constraints = [models.UniqueConstraint(fields=("report", "age_group", "gender", "resident_status"), name="unique_population_snapshot_grain")]
    def clean(self):
        if self.report_id and self.village_id and self.report.village_id != self.village_id: raise ValidationError({"village": "Village must match the report."})

class PopulationMovement(UUIDTimeStampedModel):
    MOVEMENT_TYPES = (("birth","Birth"),("death","Death"),("moved_in","Moved in"),("moved_out","Moved out"),("temporarily_left","Temporarily left"),("returned","Returned"))
    village = models.ForeignKey("locations.Village", on_delete=models.PROTECT, related_name="population_movements"); reporting_period = models.ForeignKey("reporting.ReportingPeriod", on_delete=models.PROTECT, related_name="population_movements")
    movement_type = models.CharField(max_length=30, choices=MOVEMENT_TYPES); movement_date = models.DateField(); gender = models.CharField(max_length=30, blank=True); age_group = models.ForeignKey(AgeGroup, null=True, blank=True, on_delete=models.PROTECT); count = models.PositiveIntegerField()
    origin_or_destination = models.CharField(max_length=200, blank=True); reason = models.TextField(blank=True); data_source = models.CharField(max_length=40, choices=AnalyticalRecord.DataSource.choices); verified = models.BooleanField(default=False)

class Household(UUIDTimeStampedModel):
    household_code = models.CharField(max_length=50); village = models.ForeignKey("locations.Village", on_delete=models.PROTECT, related_name="households"); household_head_name = models.CharField(max_length=200)
    household_size = models.PositiveIntegerField(null=True, blank=True); male_count = models.PositiveIntegerField(null=True, blank=True); female_count = models.PositiveIntegerField(null=True, blank=True); child_count = models.PositiveIntegerField(null=True, blank=True); elderly_count = models.PositiveIntegerField(null=True, blank=True); disability_count = models.PositiveIntegerField(null=True, blank=True)
    primary_livelihood = models.CharField(max_length=120, blank=True); housing_type = models.CharField(max_length=120, blank=True); water_source = models.CharField(max_length=120, blank=True); toilet_type = models.CharField(max_length=120, blank=True); energy_source = models.CharField(max_length=120, blank=True); vulnerability_status = models.CharField(max_length=80, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True); longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    effective_from = models.DateField(); effective_to = models.DateField(null=True, blank=True); is_active = models.BooleanField(default=True)
    verification_status = models.CharField(max_length=30, choices=AnalyticalRecord.VerificationStatus.choices, default=AnalyticalRecord.VerificationStatus.UNVERIFIED)
    class Meta: constraints = [models.UniqueConstraint(fields=("village", "household_code", "effective_from"), name="unique_household_effective_record")]
    def clean(self):
        if self.effective_to and self.effective_to < self.effective_from: raise ValidationError({"effective_to": "End date cannot precede start date."})
        if self.is_active and self.effective_to: raise ValidationError({"is_active": "An inactive historical household version must be used when an end date is set."})
        validate_subcounts(
            self.household_size,
            child_count=self.child_count,
            elderly_count=self.elderly_count,
            disability_count=self.disability_count,
        )
        if self.household_size is not None and sum((self.male_count or 0, self.female_count or 0)) > self.household_size:
            raise ValidationError({"household_size": "Male and female household members cannot exceed household size."})
