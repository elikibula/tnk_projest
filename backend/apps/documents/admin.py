from django.contrib import admin

from apps.core.admin import is_national_admin

from .models import EvidenceDocument, EvidenceLink


class CentralEvidenceAdmin(admin.ModelAdmin):
    list_per_page = 50

    def _trusted(self, request):
        return is_national_admin(request.user)

    def has_module_permission(self, request):
        return self._trusted(request) and super().has_module_permission(request)

    def has_view_permission(self, request, obj=None):
        return self._trusted(request) and super().has_view_permission(request, obj)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(EvidenceDocument)
class EvidenceDocumentAdmin(CentralEvidenceAdmin):
    list_display = ("title", "document_type", "confidentiality_level", "uploaded_by", "uploaded_at", "file_size")
    list_filter = ("confidentiality_level", "document_type", "uploaded_at")
    search_fields = ("title", "original_filename", "checksum", "uploaded_by__username")
    list_select_related = ("uploaded_by",)
    date_hierarchy = "uploaded_at"
    readonly_fields = tuple(field.name for field in EvidenceDocument._meta.fields)


@admin.register(EvidenceLink)
class EvidenceLinkAdmin(CentralEvidenceAdmin):
    list_display = ("document", "content_type", "object_id", "created_at")
    list_filter = ("content_type", "created_at")
    search_fields = ("document__title", "document__original_filename", "object_id")
    list_select_related = ("document", "content_type")
    date_hierarchy = "created_at"
    readonly_fields = tuple(field.name for field in EvidenceLink._meta.fields)
