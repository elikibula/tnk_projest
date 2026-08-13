from django.db import models
from apps.core.models import UUIDTimeStampedModel

class Province(UUIDTimeStampedModel):
    code = models.CharField(max_length=20, unique=True)
    name_en = models.CharField(max_length=120)
    name_fj = models.CharField(max_length=120, blank=True)
    is_active = models.BooleanField(default=True)
    class Meta: ordering = ("name_en",)
    def __str__(self): return self.name_en

class Tikina(UUIDTimeStampedModel):
    province = models.ForeignKey(Province, on_delete=models.PROTECT, related_name="tikina")
    code = models.CharField(max_length=20)
    name_en = models.CharField(max_length=120)
    name_fj = models.CharField(max_length=120, blank=True)
    is_active = models.BooleanField(default=True)
    class Meta:
        ordering = ("province__name_en", "name_en")
        constraints = [models.UniqueConstraint(fields=("province", "code"), name="unique_tikina_code_per_province")]
    def __str__(self): return self.name_en

class Village(UUIDTimeStampedModel):
    tikina = models.ForeignKey(Tikina, on_delete=models.PROTECT, related_name="villages")
    code = models.CharField(max_length=20)
    name_en = models.CharField(max_length=120)
    name_fj = models.CharField(max_length=120, blank=True)
    island_name = models.CharField(max_length=120, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    postal_address = models.TextField(blank=True)
    contact_phone = models.CharField(max_length=40, blank=True)
    contact_email = models.EmailField(blank=True)
    is_active = models.BooleanField(default=True)
    class Meta:
        ordering = ("tikina__name_en", "name_en")
        constraints = [models.UniqueConstraint(fields=("tikina", "code"), name="unique_village_code_per_tikina")]
    def __str__(self): return self.name_en
