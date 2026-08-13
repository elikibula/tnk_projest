from django.contrib import admin
from apps.core.admin import GlobalReferenceAdmin, LocationScopedAdmin, is_national_admin
from .models import DataDictionaryEntry,DataExportAudit,IndicatorDefinition,IndicatorValue
admin.site.register((DataDictionaryEntry, IndicatorDefinition), GlobalReferenceAdmin)


@admin.register(IndicatorValue)
class IndicatorValueAdmin(LocationScopedAdmin):
    list_display = ("indicator", "reporting_period", "village", "tikina", "province", "value", "calculation_status", "data_quality_rating")
    list_filter = ("calculation_status", "data_quality_rating", "reporting_period")
    search_fields = ("indicator__code", "indicator__name_en", "village__name_en", "tikina__name_en", "province__name_en")

    def get_readonly_fields(self, request, obj=None):
        return tuple(field.name for field in self.model._meta.concrete_fields)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        actions = super().get_actions(request)
        actions.pop("delete_selected", None)
        return actions


@admin.register(DataExportAudit)
class DataExportAuditAdmin(admin.ModelAdmin):
    list_display = ("generated_at", "generated_by", "report_type", "format", "number_of_records", "export_reason")
    list_filter = ("format", "report_type", "generated_at")
    search_fields = ("generated_by__username", "export_reason")
    list_select_related = ("generated_by",)
    date_hierarchy = "generated_at"
    readonly_fields = tuple(field.name for field in DataExportAudit._meta.concrete_fields)

    def has_module_permission(self, request):
        return is_national_admin(request.user) and super().has_module_permission(request)

    def has_view_permission(self, request, obj=None):
        return is_national_admin(request.user) and super().has_view_permission(request, obj)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False
