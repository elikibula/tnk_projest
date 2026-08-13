from django.contrib import admin
from django.db.models import Q

from apps.accounts.models import Role
from apps.accounts.permissions import user_has_any_role
from apps.accounts.selectors import villages_for_user
from apps.core.security import village_for_record
from apps.locations.models import Province, Tikina, Village
from apps.reporting.models import TNKReport


ADMIN_ROLES = {Role.Codes.SYSTEM_ADMIN, Role.Codes.PROVINCIAL_ADMIN}
OFFICIAL_STATUSES = {
    TNKReport.Status.APPROVED,
    TNKReport.Status.LOCKED,
    TNKReport.Status.ARCHIVED,
}
HISTORICAL_MASTER_MODELS = {
    "governance.OfficialAppointment",
    "governance.VillageCommittee",
    "governance.CommitteeMember",
    "economy.VillageBusiness",
    "infrastructure.VillageAsset",
    "infrastructure.VillageWaterSource",
    "infrastructure.VillageEnergyAsset",
    "projects.IVDPProject",
    "culture.TraditionalTitle",
    "culture.TraditionalTitleAppointment",
    "population.Household",
}
RELATION_LOCATION_LOOKUPS = {
    "account": "account__village",
    "amendment": "amendment__original_report__village",
    "asset": "asset__village",
    "business": "business__village",
    "committee": "committee__village",
    "facility": "facility__village",
    "impact_observation": "impact_observation__village",
    "meeting": "meeting__report__village",
    "project": "project__village",
    "title": "title__traditional_unit__village",
    "traditional_unit": "traditional_unit__village",
    "training": "training__village",
    "water_source": "water_source__village",
}
SENSITIVE_LIST_FIELDS = {
    "account_number",
    "comment",
    "description",
    "email",
    "findings",
    "household_head_name",
    "metadata",
    "notes",
    "phone",
    "recommendations",
    "responsible_person",
}
DISPLAY_PRIORITY = (
    "code",
    "name_en",
    "name",
    "title",
    "project_code",
    "project_name",
    "business_name",
    "report",
    "village",
    "home_village",
    "tikina",
    "province",
    "reporting_period",
    "status",
    "verification_status",
    "measurement_date",
    "is_active",
    "created_at",
)
SEARCH_PRIORITY = (
    "code",
    "name_en",
    "name_fj",
    "name",
    "title",
    "project_code",
    "project_name",
    "business_name",
    "village__name_en",
    "village__name_fj",
    "report__village__name_en",
    "home_village__name_en",
)


def is_national_admin(user):
    return user.is_superuser or user_has_any_role(user, {Role.Codes.SYSTEM_ADMIN})


def is_delegated_admin(user):
    return is_national_admin(user) or user_has_any_role(user, {Role.Codes.PROVINCIAL_ADMIN})


def _field_names(model):
    return {field.name for field in model._meta.fields}


def location_lookup_for_model(model):
    names = _field_names(model)
    if "village" in names:
        return "village"
    if "home_village" in names:
        return "home_village"
    if "report" in names:
        return "report__village"
    if "original_report" in names:
        return "original_report__village"
    for field_name, lookup in RELATION_LOCATION_LOOKUPS.items():
        if field_name in names:
            return lookup
    return None


def scoped_queryset(queryset, user):
    if is_national_admin(user):
        return queryset
    villages = villages_for_user(user)
    model = queryset.model
    if model is Village:
        return queryset.filter(pk__in=villages)
    if model is Tikina:
        return queryset.filter(pk__in=villages.values("tikina_id"))
    if model is Province:
        return queryset.filter(pk__in=villages.values("tikina__province_id"))
    if model._meta.label == "analytics.IndicatorValue":
        return queryset.filter(
            Q(village__in=villages)
            | Q(village__isnull=True, tikina_id__in=villages.values("tikina_id"))
            | Q(village__isnull=True, tikina__isnull=True, province_id__in=villages.values("tikina__province_id"))
        ).distinct()
    lookup = location_lookup_for_model(model)
    return queryset.filter(**{f"{lookup}__in": villages}).distinct() if lookup else queryset.none()


def object_in_scope(user, obj):
    if obj is None or is_national_admin(user):
        return True
    villages = villages_for_user(user)
    if isinstance(obj, Village):
        return villages.filter(pk=obj.pk).exists()
    if isinstance(obj, Tikina):
        return villages.filter(tikina=obj).exists()
    if isinstance(obj, Province):
        return villages.filter(tikina__province=obj).exists()
    village = village_for_record(obj)
    return village is not None and villages.filter(pk=village.pk).exists()


class AdminUsabilityMixin:
    list_per_page = 50
    save_on_top = True

    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        date_fields = _field_names(model)
        for candidate in ("occurred_at", "acted_at", "requested_at", "uploaded_at", "measurement_date", "created_at"):
            if candidate in date_fields:
                self.date_hierarchy = candidate
                break

    def get_list_display(self, request):
        configured = super().get_list_display(request)
        if configured != ("__str__",):
            return configured
        names = _field_names(self.model)
        selected = [field for field in DISPLAY_PRIORITY if field in names and field not in SENSITIVE_LIST_FIELDS]
        if not selected:
            selected = [self.model._meta.pk.name]
        return tuple(selected[:6])

    def get_list_filter(self, request):
        configured = super().get_list_filter(request)
        if configured:
            return configured
        choices = []
        for field in self.model._meta.fields:
            if field.name in {"status", "verification_status", "confidentiality_level", "is_active", "reporting_period"} or field.choices:
                choices.append(field.name)
        return tuple(choices[:5])

    def get_search_fields(self, request):
        configured = super().get_search_fields(request)
        if configured:
            return configured
        names = _field_names(self.model)
        selected = []
        for lookup in SEARCH_PRIORITY:
            root = lookup.split("__", 1)[0]
            if root in names and root not in SENSITIVE_LIST_FIELDS:
                selected.append(lookup)
        return tuple(selected[:6])

    def get_list_select_related(self, request):
        configured = super().get_list_select_related(request)
        if configured is not False:
            return configured
        return tuple(field.name for field in self.model._meta.fields if field.many_to_one) or False


class LocationScopedAdmin(AdminUsabilityMixin, admin.ModelAdmin):
    """Permit only national/provincial administrators and enforce geographic scope."""

    def _trusted(self, request):
        return is_delegated_admin(request.user)

    def has_module_permission(self, request):
        return self._trusted(request) and super().has_module_permission(request)

    def has_view_permission(self, request, obj=None):
        return self._trusted(request) and object_in_scope(request.user, obj) and super().has_view_permission(request, obj)

    def has_add_permission(self, request):
        if not self._trusted(request):
            return False
        if not is_national_admin(request.user) and location_lookup_for_model(self.model) is None:
            return False
        return super().has_add_permission(request)

    def has_change_permission(self, request, obj=None):
        return self._trusted(request) and object_in_scope(request.user, obj) and super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return self._trusted(request) and object_in_scope(request.user, obj) and super().has_delete_permission(request, obj)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return scoped_queryset(queryset, request.user) if self._trusted(request) else queryset.none()

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
        related_model = getattr(db_field.remote_field, "model", None)
        is_location_bound = related_model in {Province, Tikina, Village} or (
            related_model is not None and location_lookup_for_model(related_model) is not None
        )
        if (
            formfield is not None
            and hasattr(formfield, "queryset")
            and not is_national_admin(request.user)
            and is_location_bound
        ):
            formfield.queryset = scoped_queryset(formfield.queryset, request.user)
        return formfield


class GlobalReferenceAdmin(AdminUsabilityMixin, admin.ModelAdmin):
    """Provincial administrators may inspect global references; only national admins change them."""

    def has_module_permission(self, request):
        return is_delegated_admin(request.user) and super().has_module_permission(request)

    def has_view_permission(self, request, obj=None):
        return is_delegated_admin(request.user) and super().has_view_permission(request, obj)

    def has_add_permission(self, request):
        return is_national_admin(request.user) and super().has_add_permission(request)

    def has_change_permission(self, request, obj=None):
        return is_national_admin(request.user) and super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return is_national_admin(request.user) and super().has_delete_permission(request, obj)


class ProtectedReportLinkedAdmin(LocationScopedAdmin):
    """Scope domain records and keep historical or official-report records read-only."""

    def protected_report(self, obj):
        if obj is None or not hasattr(obj, "report_id") or not obj.report_id:
            return None
        return obj.report

    def get_readonly_fields(self, request, obj=None):
        if obj and self.model._meta.label in HISTORICAL_MASTER_MODELS:
            return tuple(field.name for field in obj._meta.concrete_fields)
        report = self.protected_report(obj)
        if report and report.status in OFFICIAL_STATUSES:
            return tuple(field.name for field in obj._meta.concrete_fields)
        return super().get_readonly_fields(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj and self.model._meta.label in HISTORICAL_MASTER_MODELS:
            return False
        report = self.protected_report(obj)
        if report and report.status in OFFICIAL_STATUSES:
            return False
        return super().has_delete_permission(request, obj)

    def get_actions(self, request):
        actions = super().get_actions(request)
        if self.model._meta.label in HISTORICAL_MASTER_MODELS or "report" in _field_names(self.model):
            actions.pop("delete_selected", None)
        return actions


class SensitiveRecordAdmin(ProtectedReportLinkedAdmin):
    """Highly restricted records use the same trusted, location-scoped boundary."""
