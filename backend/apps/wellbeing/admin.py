from django.contrib import admin
from .models import CommunitySafetyIncident, DisabilitySnapshot, DisabilityType, HealthCondition, HealthConditionSnapshot, OffenceType, VillageHealthAccessSnapshot
from apps.core.admin import GlobalReferenceAdmin, SensitiveRecordAdmin
admin.site.register((HealthCondition, DisabilityType, OffenceType), GlobalReferenceAdmin)
admin.site.register((HealthConditionSnapshot, VillageHealthAccessSnapshot, DisabilitySnapshot, CommunitySafetyIncident), SensitiveRecordAdmin)
