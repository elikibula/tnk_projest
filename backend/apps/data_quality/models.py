import uuid
from django.conf import settings
from django.db import models
class DataQualityRule(models.Model):
    SEVERITIES=(("information","Information"),("warning","Warning"),("error","Error"),("critical","Critical"))
    code=models.CharField(max_length=80,unique=True); section=models.CharField(max_length=40); description=models.TextField(); severity=models.CharField(max_length=20,choices=SEVERITIES); is_active=models.BooleanField(default=True); configurable_parameters=models.JSONField(default=dict,blank=True)
class DataQualityIssue(models.Model):
    uuid=models.UUIDField(default=uuid.uuid4,editable=False,unique=True); report=models.ForeignKey("reporting.TNKReport",on_delete=models.CASCADE,related_name="quality_issues"); section=models.CharField(max_length=40); field_name=models.CharField(max_length=120,blank=True); rule=models.ForeignKey(DataQualityRule,on_delete=models.PROTECT); severity=models.CharField(max_length=20,choices=DataQualityRule.SEVERITIES); message=models.TextField(); current_value=models.TextField(blank=True); previous_value=models.TextField(blank=True); resolved=models.BooleanField(default=False); resolution_comment=models.TextField(blank=True); resolved_by=models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,on_delete=models.PROTECT); resolved_at=models.DateTimeField(null=True,blank=True); created_at=models.DateTimeField(auto_now_add=True)
    class Meta: indexes=[models.Index(fields=("report","resolved","severity"),name="quality_report_open_idx")]
