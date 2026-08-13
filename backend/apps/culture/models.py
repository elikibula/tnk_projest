from django.core.exceptions import ValidationError
from django.db import models
from apps.core.models import UUIDTimeStampedModel
class TraditionalUnit(UUIDTimeStampedModel):
    village=models.ForeignKey("locations.Village",on_delete=models.PROTECT,related_name="traditional_units"); unit_type=models.CharField(max_length=20,choices=(("yavusa","Yavusa"),("mataqali","Mataqali"),("tokatoka","Tokatoka"),("other","Other"))); name=models.CharField(max_length=160); is_active=models.BooleanField(default=True)
class TraditionalTitle(UUIDTimeStampedModel):
    traditional_unit=models.ForeignKey(TraditionalUnit,on_delete=models.PROTECT,related_name="titles"); title_type=models.CharField(max_length=80); title_name=models.CharField(max_length=160); status=models.CharField(max_length=30); vacancy_start_date=models.DateField(null=True,blank=True); confirmation_stage=models.CharField(max_length=40,choices=((x,x.replace("_"," ").title()) for x in ("vacant","community_discussion","village_meeting_completed","documentation_in_progress","submitted","under_review","confirmed","disputed"))); confirmation_date=models.DateField(null=True,blank=True); next_action=models.TextField(blank=True); responsible_party=models.CharField(max_length=160,blank=True)
    def clean(self):
        if self.confirmation_stage == "confirmed" and not self.confirmation_date:
            raise ValidationError({"confirmation_date": "A confirmed title requires a confirmation date."})
class TraditionalTitleAppointment(UUIDTimeStampedModel):
    title=models.ForeignKey(TraditionalTitle,on_delete=models.PROTECT,related_name="appointments"); person=models.ForeignKey("governance.PersonReference",on_delete=models.PROTECT,related_name="traditional_appointments"); effective_from=models.DateField(); effective_to=models.DateField(null=True,blank=True); confirmation_reference=models.CharField(max_length=160,blank=True); is_current=models.BooleanField(default=True)
    def clean(self):
        if self.is_current and self.effective_to: raise ValidationError({"is_current":"A current title appointment cannot have an end date."})
        if self.effective_to and self.effective_to < self.effective_from: raise ValidationError({"effective_to":"End date cannot precede start date."})
class CulturalKnowledgeRecord(UUIDTimeStampedModel):
    village=models.ForeignKey("locations.Village",on_delete=models.PROTECT,related_name="cultural_knowledge"); knowledge_category=models.CharField(max_length=80); knowledge_name=models.CharField(max_length=180); description=models.TextField(); number_of_knowledge_holders=models.PositiveIntegerField(null=True,blank=True); youngest_knowledge_holder_age=models.PositiveIntegerField(null=True,blank=True); transmission_status=models.CharField(max_length=40); preservation_activity=models.TextField(blank=True); activity_frequency=models.CharField(max_length=80,blank=True); youth_participation=models.BooleanField(null=True,blank=True); documentation_available=models.BooleanField(null=True,blank=True); evidence_document=models.FileField(upload_to="culture/%Y/%m/",null=True,blank=True); risk_level=models.CharField(max_length=30,choices=((x,x.replace("_"," ").title()) for x in ("secure","requires_support","at_risk","critically_at_risk")))
