from django.contrib import admin
from .models import IVDPProject, IVDPProjectProgress, ProjectMilestone, ProjectRisk
from apps.core.admin import ProtectedReportLinkedAdmin
admin.site.register((IVDPProject,ProjectMilestone,IVDPProjectProgress,ProjectRisk), ProtectedReportLinkedAdmin)
