from django.contrib import admin
from apps.core.admin import GlobalReferenceAdmin, LocationScopedAdmin

from .models import ReportAmendment, ReportAmendmentChange, ReportMasterSnapshot, ReportingPeriod, ReportSectionStatus, TNKReport


@admin.register(ReportingPeriod)
class ReportingPeriodAdmin(GlobalReferenceAdmin):
    list_display = ("year", "quarter", "start_date", "end_date", "is_open", "is_locked")
    list_filter = ("year", "is_open", "is_locked")


class ReportSectionStatusInline(admin.TabularInline):
    model = ReportSectionStatus
    extra = 0
    readonly_fields = ("last_updated_at",)

    def has_add_permission(self, request, obj=None):
        return bool(obj and obj.is_editable) and super().has_add_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        return bool(obj is None or obj.is_editable) and super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return bool(obj and obj.is_editable) and super().has_delete_permission(request, obj)


@admin.register(TNKReport)
class TNKReportAdmin(LocationScopedAdmin):
    list_display = ("village", "reporting_period", "status", "completeness_percentage", "prepared_by")
    list_filter = ("status", "reporting_period")
    search_fields = ("village__name_en", "village__name_fj")
    inlines = (ReportSectionStatusInline,)

    readonly_fields = tuple(field.name for field in TNKReport._meta.fields)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ReportMasterSnapshot)
class ReportMasterSnapshotAdmin(LocationScopedAdmin):
    list_display = ("report", "section_code", "entry_key", "summary", "captured_at")
    list_filter = ("section_code", "entry_key", "captured_at")
    search_fields = ("report__village__name_en", "summary", "source_identifier")
    readonly_fields = tuple(field.name for field in ReportMasterSnapshot._meta.fields)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class ReportAmendmentChangeInline(admin.TabularInline):
    model = ReportAmendmentChange
    extra = 0
    readonly_fields = tuple(field.name for field in ReportAmendmentChange._meta.fields)

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ReportAmendment)
class ReportAmendmentAdmin(LocationScopedAdmin):
    list_display = ("original_report", "amendment_number", "status", "requested_by", "approved_by", "requested_at")
    list_filter = ("status", "original_report__reporting_period")
    search_fields = ("original_report__village__name_en", "reason", "requested_by__username")
    readonly_fields = tuple(field.name for field in ReportAmendment._meta.fields)
    inlines = (ReportAmendmentChangeInline,)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ReportAmendmentChange)
class ReportAmendmentChangeAdmin(LocationScopedAdmin):
    list_display = ("amendment", "section_code", "entry_key", "field_label", "affects_analytics", "created_by")
    list_filter = ("affects_analytics", "section_code", "amendment__status")
    search_fields = ("amendment__original_report__village__name_en", "field_label", "change_reason")
    readonly_fields = tuple(field.name for field in ReportAmendmentChange._meta.fields)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
