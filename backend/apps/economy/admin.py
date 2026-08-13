from django.contrib import admin
from .models import BusinessMovement, CropProductionSnapshot, CropType, FoodSecuritySnapshot, VillageBusiness, VillageFinancialAccount, VillageFinancialSnapshot
from apps.core.admin import GlobalReferenceAdmin, ProtectedReportLinkedAdmin
admin.site.register(CropType, GlobalReferenceAdmin)
admin.site.register((CropProductionSnapshot,FoodSecuritySnapshot,VillageBusiness,BusinessMovement,VillageFinancialAccount,VillageFinancialSnapshot), ProtectedReportLinkedAdmin)
