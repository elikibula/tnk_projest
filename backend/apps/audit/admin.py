from django.contrib import admin
from django.db.models import Q

from apps.accounts.models import Role
from apps.accounts.permissions import user_has_any_role
from apps.accounts.selectors import villages_for_user
from apps.core.admin import is_national_admin

from .models import AuditEvent


@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    trusted_roles = {Role.Codes.SYSTEM_ADMIN, Role.Codes.PROVINCIAL_ADMIN, Role.Codes.AUDITOR}
    list_display = ("occurred_at", "actor", "action", "object_type", "location", "summary")
    list_filter = ("action", "object_type", "province", "tikina")
    search_fields = ("actor__username", "actor__first_name", "actor__last_name", "action", "object_type", "summary", "object_uuid")
    list_select_related = ("actor", "province", "tikina", "village")
    date_hierarchy = "occurred_at"
    list_per_page = 100
    readonly_fields = tuple(field.name for field in AuditEvent._meta.fields)

    @admin.display(description="Location")
    def location(self, obj):
        return obj.village or obj.tikina or obj.province or "Central / unscoped"

    def _trusted(self, request):
        return user_has_any_role(request.user, self.trusted_roles)

    def has_module_permission(self, request):
        return self._trusted(request) and super().has_module_permission(request)

    def has_view_permission(self, request, obj=None):
        if not self._trusted(request):
            return False
        if obj is not None and not is_national_admin(request.user):
            villages = villages_for_user(request.user)
            return (
                (obj.village_id and villages.filter(pk=obj.village_id).exists())
                or (obj.tikina_id and villages.filter(tikina_id=obj.tikina_id).exists())
                or (obj.province_id and villages.filter(tikina__province_id=obj.province_id).exists())
            ) and super().has_view_permission(request, obj)
        return super().has_view_permission(request, obj)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if not self._trusted(request):
            return queryset.none()
        if is_national_admin(request.user):
            return queryset
        villages = villages_for_user(request.user)
        return queryset.filter(
            Q(village__in=villages)
            | Q(tikina_id__in=villages.values("tikina_id"))
            | Q(province_id__in=villages.values("tikina__province_id"))
        ).distinct()

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
