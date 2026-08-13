from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator,MinValueValidator
from django.db import models
from apps.core.models import UUIDTimeStampedModel
from apps.core.validation import validate_non_negative, validate_subcounts
PERCENT=[MinValueValidator(0),MaxValueValidator(100)]
class IVDPProject(UUIDTimeStampedModel):
    project_code=models.CharField(max_length=50); village=models.ForeignKey("locations.Village",on_delete=models.PROTECT,related_name="ivdp_projects"); project_name=models.CharField(max_length=200); project_category=models.CharField(max_length=80); problem_being_addressed=models.TextField(); baseline_value=models.DecimalField(max_digits=14,decimal_places=2,null=True,blank=True); target_value=models.DecimalField(max_digits=14,decimal_places=2,null=True,blank=True); measurement_unit=models.CharField(max_length=40,blank=True); priority=models.CharField(max_length=20); responsible_person=models.CharField(max_length=160,blank=True); responsible_organisation=models.CharField(max_length=160,blank=True); planned_start_date=models.DateField(null=True,blank=True); planned_end_date=models.DateField(null=True,blank=True); actual_start_date=models.DateField(null=True,blank=True); actual_end_date=models.DateField(null=True,blank=True); estimated_budget=models.DecimalField(max_digits=16,decimal_places=2,null=True,blank=True); approved_budget=models.DecimalField(max_digits=16,decimal_places=2,null=True,blank=True); actual_expenditure=models.DecimalField(max_digits=16,decimal_places=2,null=True,blank=True); currency_code=models.CharField(max_length=3,default="FJD"); funding_source=models.CharField(max_length=160,blank=True); project_status=models.CharField(max_length=40); physical_progress_percentage=models.DecimalField(max_digits=5,decimal_places=2,default=0,validators=PERCENT); financial_progress_percentage=models.DecimalField(max_digits=5,decimal_places=2,default=0,validators=PERCENT); expected_beneficiaries=models.PositiveIntegerField(null=True,blank=True); male_beneficiaries=models.PositiveIntegerField(null=True,blank=True); female_beneficiaries=models.PositiveIntegerField(null=True,blank=True); youth_beneficiaries=models.PositiveIntegerField(null=True,blank=True); is_active=models.BooleanField(default=True)
    class Meta: constraints=[models.UniqueConstraint(fields=("village","project_code"),name="unique_village_project_code")]
    def clean(self):
        if self.project_status=="completed" and not self.actual_end_date: raise ValidationError({"actual_end_date":"Completed projects require an actual completion date."})
        errors = {}
        if self.planned_start_date and self.planned_end_date and self.planned_end_date < self.planned_start_date:
            errors["planned_end_date"] = "Planned end date cannot precede planned start date."
        if self.actual_start_date and self.actual_end_date and self.actual_end_date < self.actual_start_date:
            errors["actual_end_date"] = "Actual end date cannot precede actual start date."
        if errors:
            raise ValidationError(errors)
        validate_non_negative(estimated_budget=self.estimated_budget, approved_budget=self.approved_budget, actual_expenditure=self.actual_expenditure)
        validate_subcounts(self.expected_beneficiaries, male_beneficiaries=self.male_beneficiaries, female_beneficiaries=self.female_beneficiaries, youth_beneficiaries=self.youth_beneficiaries)
        if self.expected_beneficiaries is not None and (self.male_beneficiaries or 0) + (self.female_beneficiaries or 0) > self.expected_beneficiaries:
            raise ValidationError({"expected_beneficiaries": "Male and female beneficiaries cannot exceed expected beneficiaries."})
class ProjectMilestone(UUIDTimeStampedModel):
    project=models.ForeignKey(IVDPProject,on_delete=models.PROTECT,related_name="milestones"); title=models.CharField(max_length=180); planned_date=models.DateField(null=True,blank=True); completed_date=models.DateField(null=True,blank=True); percentage_weight=models.DecimalField(max_digits=5,decimal_places=2,validators=PERCENT); status=models.CharField(max_length=30)
class IVDPProjectProgress(UUIDTimeStampedModel):
    project=models.ForeignKey(IVDPProject,on_delete=models.PROTECT,related_name="progress_records"); report=models.ForeignKey("reporting.TNKReport",on_delete=models.PROTECT,related_name="project_progress"); reporting_date=models.DateField(); work_completed=models.TextField(); milestone=models.ForeignKey(ProjectMilestone,null=True,blank=True,on_delete=models.PROTECT); progress_percentage=models.DecimalField(max_digits=5,decimal_places=2,validators=PERCENT); expenditure_to_date=models.DecimalField(max_digits=16,decimal_places=2,null=True,blank=True); materials_received=models.TextField(blank=True); challenges=models.TextField(blank=True); corrective_action=models.TextField(blank=True); next_activity=models.TextField(blank=True); next_activity_due_date=models.DateField(null=True,blank=True); risk_level=models.CharField(max_length=20); evidence_document=models.FileField(upload_to="projects/%Y/%m/",null=True,blank=True)
    def clean(self):
        validate_non_negative(expenditure_to_date=self.expenditure_to_date)
        if self.milestone_id and self.milestone.project_id != self.project_id:
            raise ValidationError({"milestone": "Milestone must belong to the selected project."})
class ProjectRisk(UUIDTimeStampedModel):
    project=models.ForeignKey(IVDPProject,on_delete=models.PROTECT,related_name="risks"); risk_type=models.CharField(max_length=80); description=models.TextField(); likelihood=models.CharField(max_length=20); impact=models.CharField(max_length=20); mitigation=models.TextField(blank=True); owner=models.CharField(max_length=160,blank=True); status=models.CharField(max_length=30)
