from django.contrib import admin
from apps.core.admin import ProtectedReportLinkedAdmin
from .models import CulturalKnowledgeRecord, TraditionalTitle, TraditionalTitleAppointment, TraditionalUnit
admin.site.register((TraditionalUnit,TraditionalTitle,TraditionalTitleAppointment,CulturalKnowledgeRecord), ProtectedReportLinkedAdmin)
