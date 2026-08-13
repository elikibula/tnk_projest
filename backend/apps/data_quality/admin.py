from django.contrib import admin
from apps.core.admin import GlobalReferenceAdmin, LocationScopedAdmin
from .models import DataQualityIssue,DataQualityRule
admin.site.register(DataQualityRule, GlobalReferenceAdmin)


@admin.register(DataQualityIssue)
class DataQualityIssueAdmin(LocationScopedAdmin):
    list_display = ("report", "severity", "section", "field_name", "resolved", "created_at")
    list_filter = ("severity", "resolved", "section", "created_at")
    search_fields = ("report__village__name_en", "rule__code", "message", "field_name")
    readonly_fields = tuple(field.name for field in DataQualityIssue._meta.fields)
    date_hierarchy = "created_at"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
