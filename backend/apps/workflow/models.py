import uuid
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
class ApprovalAction(models.Model):
    uuid=models.UUIDField(default=uuid.uuid4,editable=False,unique=True); report=models.ForeignKey("reporting.TNKReport",on_delete=models.PROTECT,related_name="approval_actions"); user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT); user_full_name=models.CharField(max_length=200); user_role=models.CharField(max_length=100); action_type=models.CharField(max_length=30,choices=((x,x.replace("_"," ").title()) for x in ("submit","comment","request_correction","return","forward","verify","approve","reject","reopen","lock","archive"))); from_status=models.CharField(max_length=40); to_status=models.CharField(max_length=40); comment=models.TextField(blank=True); digital_acknowledgement=models.BooleanField(default=False); acted_at=models.DateTimeField(auto_now_add=True); ip_address=models.GenericIPAddressField(null=True,blank=True); user_agent=models.TextField(blank=True)
    def save(self,*args,**kwargs):
        if self.pk: raise ValidationError("Approval actions are immutable.")
        return super().save(*args,**kwargs)
    def delete(self,*args,**kwargs): raise ValidationError("Approval actions are immutable.")
class FinalDeclaration(models.Model):
    report=models.OneToOneField("reporting.TNKReport",on_delete=models.PROTECT,related_name="final_declaration"); declared_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT); declaration_text=models.TextField(); acknowledged=models.BooleanField(default=False); declared_at=models.DateTimeField(auto_now_add=True)
