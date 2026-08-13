from django.contrib import admin
from django.utils import timezone

from .models import MobileDevice


@admin.action(description="Revoke selected mobile devices")
def revoke_devices(modeladmin, request, queryset):
    queryset.filter(is_active=True).update(is_active=False, revoked_at=timezone.now())


@admin.register(MobileDevice)
class MobileDeviceAdmin(admin.ModelAdmin):
    list_display = ("uuid", "user", "platform", "app_version", "is_active", "last_seen_at")
    list_filter = ("platform", "is_active")
    search_fields = ("user__username", "device_identifier", "device_name")
    readonly_fields = ("uuid", "user", "device_identifier", "platform", "registered_at", "last_seen_at", "last_sync_at", "revoked_at")
    actions = (revoke_devices,)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
