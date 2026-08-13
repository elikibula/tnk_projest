from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import models
from apps.core.models import AnalyticalRecord, UUIDTimeStampedModel
from apps.core.validation import validate_non_negative, validate_subcounts
class CropType(models.Model):
    code=models.CharField(max_length=50,unique=True); crop_group=models.CharField(max_length=80); name_en=models.CharField(max_length=120); name_fj=models.CharField(max_length=120,blank=True); default_measurement_unit=models.CharField(max_length=30)
    def __str__(self): return self.name_en
class CropProductionSnapshot(AnalyticalRecord):
    report=models.ForeignKey("reporting.TNKReport",on_delete=models.PROTECT,related_name="crop_snapshots"); crop_type=models.ForeignKey(CropType,on_delete=models.PROTECT); number_of_farmers=models.PositiveIntegerField(null=True,blank=True); number_of_gardens=models.PositiveIntegerField(null=True,blank=True); area_planted=models.DecimalField(max_digits=14,decimal_places=2,null=True,blank=True); area_unit=models.CharField(max_length=30,blank=True); quantity_harvested=models.DecimalField(max_digits=14,decimal_places=2,null=True,blank=True); quantity_unit=models.CharField(max_length=30,blank=True); quantity_consumed=models.DecimalField(max_digits=14,decimal_places=2,null=True,blank=True); quantity_sold=models.DecimalField(max_digits=14,decimal_places=2,null=True,blank=True); estimated_sales_value=models.DecimalField(max_digits=14,decimal_places=2,null=True,blank=True); currency_code=models.CharField(max_length=3,default="FJD"); quantity_lost=models.DecimalField(max_digits=14,decimal_places=2,null=True,blank=True); loss_reason=models.TextField(blank=True); planting_season=models.CharField(max_length=80,blank=True)
    def clean(self):
        validate_non_negative(area_planted=self.area_planted, quantity_harvested=self.quantity_harvested, quantity_consumed=self.quantity_consumed, quantity_sold=self.quantity_sold, estimated_sales_value=self.estimated_sales_value, quantity_lost=self.quantity_lost)
        allocated = sum((self.quantity_consumed or 0, self.quantity_sold or 0, self.quantity_lost or 0))
        if self.quantity_harvested is not None and allocated > self.quantity_harvested:
            raise ValidationError({"quantity_harvested": "Consumed, sold, and lost quantities cannot exceed the harvested quantity."})
class FoodSecuritySnapshot(AnalyticalRecord):
    report=models.OneToOneField("reporting.TNKReport",on_delete=models.PROTECT,related_name="food_security_snapshot"); households_with_food_shortage=models.PositiveIntegerField(null=True,blank=True); average_food_shortage_days=models.DecimalField(max_digits=5,decimal_places=2,null=True,blank=True); main_cause=models.TextField(blank=True); external_assistance_received=models.BooleanField(null=True,blank=True); assistance_provider=models.CharField(max_length=160,blank=True)
    def clean(self):
        validate_non_negative(average_food_shortage_days=self.average_food_shortage_days)
        if self.average_food_shortage_days is not None and self.report_id:
            period_days = (self.report.reporting_period.end_date - self.report.reporting_period.start_date).days + 1
            if self.average_food_shortage_days > period_days:
                raise ValidationError({"average_food_shortage_days": f"Food-shortage days cannot exceed the reporting period ({period_days} days)."})
class VillageBusiness(UUIDTimeStampedModel):
    village=models.ForeignKey("locations.Village",on_delete=models.PROTECT,related_name="businesses"); business_name=models.CharField(max_length=180); business_sector=models.CharField(max_length=80); owner_type=models.CharField(max_length=30); owner_person=models.ForeignKey("governance.PersonReference",null=True,blank=True,on_delete=models.PROTECT); owner_name=models.CharField(max_length=180,blank=True); owner_gender=models.CharField(max_length=30,blank=True); owner_age_group=models.ForeignKey("population.AgeGroup",null=True,blank=True,on_delete=models.PROTECT); start_date=models.DateField(null=True,blank=True); closure_date=models.DateField(null=True,blank=True); licence_status=models.CharField(max_length=40,blank=True); licence_expiry_date=models.DateField(null=True,blank=True); operating_status=models.CharField(max_length=40); full_time_employees=models.PositiveIntegerField(null=True,blank=True); part_time_employees=models.PositiveIntegerField(null=True,blank=True); male_employees=models.PositiveIntegerField(null=True,blank=True); female_employees=models.PositiveIntegerField(null=True,blank=True); youth_employees=models.PositiveIntegerField(null=True,blank=True); revenue_band=models.CharField(max_length=50,blank=True); primary_market=models.CharField(max_length=100,blank=True); support_required=models.TextField(blank=True); is_active=models.BooleanField(default=True)
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.operating_status.lower() == "closed" and not self.closure_date: raise ValidationError({"closure_date":"A closed business requires a closure date."})
        if self.closure_date and self.start_date and self.closure_date < self.start_date: raise ValidationError({"closure_date":"Closure date cannot precede the start date."})
        total = (self.full_time_employees or 0) + (self.part_time_employees or 0)
        if (self.male_employees or 0) + (self.female_employees or 0) > total:
            raise ValidationError({"full_time_employees": "Male and female employees cannot exceed total full-time and part-time employees."})
        validate_subcounts(total, youth_employees=self.youth_employees)
class BusinessMovement(UUIDTimeStampedModel):
    business=models.ForeignKey(VillageBusiness,on_delete=models.PROTECT,related_name="movements"); movement_type=models.CharField(max_length=40); movement_date=models.DateField(); old_status=models.CharField(max_length=40,blank=True); new_status=models.CharField(max_length=40); reason=models.TextField(blank=True); evidence_document=models.FileField(upload_to="business/%Y/%m/",null=True,blank=True)
class VillageFinancialAccount(UUIDTimeStampedModel):
    village=models.ForeignKey("locations.Village",on_delete=models.PROTECT,related_name="financial_accounts"); account_type=models.CharField(max_length=80); institution=models.CharField(max_length=160); account_purpose=models.CharField(max_length=200); opening_date=models.DateField(null=True,blank=True); authorised_signatories_count=models.PositiveIntegerField(null=True,blank=True); currency_code=models.CharField(max_length=3,default="FJD"); is_active=models.BooleanField(default=True)
class VillageFinancialSnapshot(UUIDTimeStampedModel):
    account=models.ForeignKey(VillageFinancialAccount,on_delete=models.PROTECT,related_name="snapshots"); report=models.ForeignKey("reporting.TNKReport",on_delete=models.PROTECT,related_name="financial_snapshots"); opening_balance=models.DecimalField(max_digits=16,decimal_places=2); deposits=models.DecimalField(max_digits=16,decimal_places=2,default=0); withdrawals=models.DecimalField(max_digits=16,decimal_places=2,default=0); interest_or_return=models.DecimalField(max_digits=16,decimal_places=2,default=0); closing_balance=models.DecimalField(max_digits=16,decimal_places=2); verified_from_statement=models.BooleanField(default=False); verification_document=models.FileField(upload_to="finance/%Y/%m/",null=True,blank=True)
    class Meta: constraints=[models.UniqueConstraint(fields=("account","report"),name="unique_financial_account_report")]
    def clean(self):
        expected=(self.opening_balance or Decimal(0))+(self.deposits or Decimal(0))+(self.interest_or_return or Decimal(0))-(self.withdrawals or Decimal(0))
        if self.closing_balance != expected: raise ValidationError({"closing_balance":f"Closing balance must equal {expected}."})
