from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models import Q

from apps.audit.services import record_event
from apps.core.admin import GlobalReferenceAdmin, is_delegated_admin, is_national_admin

from .forms import UserLocationAssignmentAdminForm
from .models import Role, User, UserLocationAssignment, UserRoleAssignment
from .selectors import villages_for_user


def _request_metadata(request):
    return {
        "ip_address": request.META.get("REMOTE_ADDR"),
        "user_agent": request.META.get("HTTP_USER_AGENT", ""),
    }


def _role_snapshot(instance):
    return {
        "user_id": instance.user_id,
        "role_id": instance.role_id,
        "role_code": instance.role.code if instance.role_id else None,
        "is_active": instance.is_active,
    }


def _location_snapshot(instance):
    return {
        "user_id": instance.user_id,
        "province_id": instance.province_id,
        "tikina_id": instance.tikina_id,
        "village_id": instance.village_id,
        "is_active": instance.is_active,
    }


def _users_in_admin_scope(user):
    if is_national_admin(user):
        return User.objects.all()
    villages = villages_for_user(user)
    return User.objects.filter(
        Q(location_assignments__village__in=villages)
        | Q(location_assignments__tikina_id__in=villages.values("tikina_id"))
        | Q(location_assignments__province_id__in=villages.values("tikina__province_id")),
        location_assignments__is_active=True,
    ).exclude(
        Q(is_superuser=True)
        | Q(
            role_assignments__is_active=True,
            role_assignments__role__code__in=(Role.Codes.SYSTEM_ADMIN, Role.Codes.PROVINCIAL_ADMIN),
        )
    ).distinct()


def _user_in_admin_scope(actor, target):
    return is_national_admin(actor) or _users_in_admin_scope(actor).filter(pk=target.pk).exists()


class ScopedUserAdmin(UserAdmin):
    list_display = ("username", "display_name", "email", "preferred_language", "is_active", "is_staff", "last_login")
    list_filter = ("is_active", "is_staff", "preferred_language", "role_assignments__role")
    search_fields = ("username", "first_name", "last_name", "email")
    ordering = ("username",)
    date_hierarchy = "date_joined"
    list_select_related = True

    @admin.display(description="Name", ordering="first_name")
    def display_name(self, obj):
        return obj.get_full_name().strip() or "-"

    def has_module_permission(self, request):
        return is_delegated_admin(request.user) and super().has_module_permission(request)

    def has_view_permission(self, request, obj=None):
        return is_delegated_admin(request.user) and (obj is None or _user_in_admin_scope(request.user, obj)) and super().has_view_permission(request, obj)

    def has_add_permission(self, request):
        # Creating a user without an atomic location assignment would create an
        # temporarily unscoped account, so only national administrators may do it.
        return is_national_admin(request.user) and super().has_add_permission(request)

    def has_change_permission(self, request, obj=None):
        return is_delegated_admin(request.user) and (obj is None or _user_in_admin_scope(request.user, obj)) and super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return is_national_admin(request.user) and super().has_delete_permission(request, obj)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if not is_delegated_admin(request.user):
            return queryset.none()
        return queryset if is_national_admin(request.user) else queryset.filter(pk__in=_users_in_admin_scope(request.user))

    def get_readonly_fields(self, request, obj=None):
        fields = list(super().get_readonly_fields(request, obj))
        if not is_national_admin(request.user):
            fields.extend(("is_staff", "is_superuser", "groups", "user_permissions"))
        return tuple(dict.fromkeys(fields))


class AssignmentAuditAdminMixin:
    snapshot_function = None
    audit_prefix = "assignment"

    def save_model(self, request, obj, form, change):
        previous = None
        if change and obj.pk:
            stored = self.model.objects.select_related().get(pk=obj.pk)
            previous = self.snapshot_function(stored)
        obj._request_audit_recorded = True
        try:
            super().save_model(request, obj, form, change)
        finally:
            del obj._request_audit_recorded
        current = self.snapshot_function(obj)
        record_event(
            actor=request.user,
            action=f"{self.audit_prefix}.{'changed' if change else 'created'}",
            instance=obj,
            summary=str(obj),
            metadata={"previous": previous, "new": current, **_request_metadata(request)},
        )

    def delete_model(self, request, obj):
        previous = self.snapshot_function(obj)
        summary = str(obj)
        obj._request_audit_recorded = True
        try:
            super().delete_model(request, obj)
        finally:
            del obj._request_audit_recorded
        record_event(
            actor=request.user,
            action=f"{self.audit_prefix}.deleted",
            instance=obj,
            summary=summary,
            metadata={"previous": previous, "new": None, **_request_metadata(request)},
        )

    def get_actions(self, request):
        actions = super().get_actions(request)
        actions.pop("delete_selected", None)
        return actions


@admin.register(Role)
class RoleAdmin(GlobalReferenceAdmin):
    list_display = ("code", "name", "is_active")
    list_filter = ("is_active",)
    search_fields = ("code", "name")


@admin.register(UserRoleAssignment)
class UserRoleAssignmentAdmin(AssignmentAuditAdminMixin, admin.ModelAdmin):
    snapshot_function = staticmethod(_role_snapshot)
    audit_prefix = "role_assignment"
    list_display = ("user_name", "role", "is_active", "assigned_at")
    list_filter = ("is_active", "role")
    search_fields = ("user__username", "user__first_name", "user__last_name", "user__email", "role__name")
    list_select_related = ("user", "role")
    ordering = ("user__first_name", "user__last_name", "user__username", "role__name")
    autocomplete_fields = ("user", "role")
    date_hierarchy = "assigned_at"

    @admin.display(description="User", ordering="user__first_name")
    def user_name(self, obj):
        return obj.user.get_full_name().strip() or obj.user.username

    def has_module_permission(self, request):
        return is_delegated_admin(request.user) and super().has_module_permission(request)

    def has_view_permission(self, request, obj=None):
        return is_delegated_admin(request.user) and (obj is None or _user_in_admin_scope(request.user, obj.user)) and super().has_view_permission(request, obj)

    def has_add_permission(self, request):
        return is_delegated_admin(request.user) and super().has_add_permission(request)

    def has_change_permission(self, request, obj=None):
        return is_delegated_admin(request.user) and (obj is None or _user_in_admin_scope(request.user, obj.user)) and super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return is_national_admin(request.user) and super().has_delete_permission(request, obj)

    def get_queryset(self, request):
        queryset = super().get_queryset(request).select_related("user", "role")
        return queryset.filter(user__in=_users_in_admin_scope(request.user)) if is_delegated_admin(request.user) else queryset.none()

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == "user" and not is_national_admin(request.user):
            formfield.queryset = _users_in_admin_scope(request.user)
        if db_field.name == "role" and not is_national_admin(request.user):
            formfield.queryset = formfield.queryset.exclude(code__in=(Role.Codes.SYSTEM_ADMIN, Role.Codes.PROVINCIAL_ADMIN))
        return formfield


@admin.register(UserLocationAssignment)
class UserLocationAssignmentAdmin(AssignmentAuditAdminMixin, admin.ModelAdmin):
    snapshot_function = staticmethod(_location_snapshot)
    audit_prefix = "location_assignment"
    form = UserLocationAssignmentAdminForm
    list_display = ("user", "scope_level", "scope_name", "is_active", "assigned_at")
    list_filter = ("is_active", "province", "tikina")
    search_fields = ("user__username", "province__name_en", "tikina__name_en", "village__name_en")
    list_select_related = ("user", "province", "tikina", "village")
    autocomplete_fields = ("user",)
    date_hierarchy = "assigned_at"

    @admin.display(description="Level")
    def scope_level(self, obj):
        return "Province" if obj.province_id else "Tikina" if obj.tikina_id else "Village"

    @admin.display(description="Location")
    def scope_name(self, obj):
        return obj.province or obj.tikina or obj.village

    def has_module_permission(self, request):
        return is_delegated_admin(request.user) and super().has_module_permission(request)

    def has_view_permission(self, request, obj=None):
        return is_delegated_admin(request.user) and (obj is None or _user_in_admin_scope(request.user, obj.user)) and super().has_view_permission(request, obj)

    def has_add_permission(self, request):
        return is_delegated_admin(request.user) and super().has_add_permission(request)

    def has_change_permission(self, request, obj=None):
        return is_delegated_admin(request.user) and (obj is None or _user_in_admin_scope(request.user, obj.user)) and super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return is_national_admin(request.user) and super().has_delete_permission(request, obj)

    def get_queryset(self, request):
        queryset = super().get_queryset(request).select_related("user", "province", "tikina", "village")
        return queryset.filter(user__in=_users_in_admin_scope(request.user)) if is_delegated_admin(request.user) else queryset.none()

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
        if not is_national_admin(request.user):
            villages = villages_for_user(request.user)
            if db_field.name == "user":
                formfield.queryset = _users_in_admin_scope(request.user)
            elif db_field.name == "province":
                formfield.queryset = formfield.queryset.filter(pk__in=villages.values("tikina__province_id"))
            elif db_field.name == "tikina":
                formfield.queryset = formfield.queryset.filter(pk__in=villages.values("tikina_id"))
            elif db_field.name == "village":
                formfield.queryset = formfield.queryset.filter(pk__in=villages)
        return formfield


admin.site.register(User, ScopedUserAdmin)
