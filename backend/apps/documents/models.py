import hashlib,uuid
from django.core.validators import MaxValueValidator, MinValueValidator
from pathlib import Path
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from .validators import validate_evidence_file
class EvidenceDocument(models.Model):
    LEVELS=(("public","Public"),("internal","Internal"),("restricted","Restricted"),("highly_restricted","Highly restricted"))
    uuid=models.UUIDField(default=uuid.uuid4,editable=False,unique=True); title=models.CharField(max_length=200); document_type=models.CharField(max_length=80); file=models.FileField(upload_to="protected/%Y/%m/",validators=[validate_evidence_file]); original_filename=models.CharField(max_length=255); file_size=models.PositiveBigIntegerField(); mime_type=models.CharField(max_length=120); checksum=models.CharField(max_length=64); description=models.TextField(blank=True); confidentiality_level=models.CharField(max_length=30,choices=LEVELS,default="restricted"); uploaded_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT); uploaded_at=models.DateTimeField(auto_now_add=True)
    captured_at=models.DateTimeField(null=True,blank=True)
    latitude=models.DecimalField(max_digits=9,decimal_places=6,null=True,blank=True,validators=[MinValueValidator(-90),MaxValueValidator(90)])
    longitude=models.DecimalField(max_digits=9,decimal_places=6,null=True,blank=True,validators=[MinValueValidator(-180),MaxValueValidator(180)])
    location_accuracy_metres=models.DecimalField(max_digits=9,decimal_places=2,null=True,blank=True,validators=[MinValueValidator(0)])
    def save(self,*args,**kwargs):
        if self.file and not self.original_filename: self.original_filename=Path(self.file.name).name
        if self.file:
            self.file_size=self.file.size
            position=self.file.tell() if hasattr(self.file,"tell") else 0
            self.file.seek(0); digest=hashlib.sha256()
            for chunk in self.file.chunks(): digest.update(chunk)
            self.checksum=digest.hexdigest(); self.file.seek(position)
        super().save(*args,**kwargs)
class EvidenceLink(models.Model):
    document=models.ForeignKey(EvidenceDocument,on_delete=models.CASCADE,related_name="links"); content_type=models.ForeignKey(ContentType,on_delete=models.CASCADE); object_id=models.PositiveBigIntegerField(); content_object=GenericForeignKey(); created_at=models.DateTimeField(auto_now_add=True)
    class Meta: constraints=[models.UniqueConstraint(fields=("document","content_type","object_id"),name="unique_evidence_link")]
