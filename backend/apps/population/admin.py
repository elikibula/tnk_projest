from django.contrib import admin
from .models import AgeGroup, Household, PopulationMovement, PopulationSnapshot
from apps.core.admin import GlobalReferenceAdmin, ProtectedReportLinkedAdmin
admin.site.register(AgeGroup, GlobalReferenceAdmin)
admin.site.register((Household, PopulationMovement, PopulationSnapshot), ProtectedReportLinkedAdmin)
