from django.db.models import Q

from apps.accounts.models import Role, User
from apps.accounts.selectors import villages_for_user
from apps.audit.models import AuditEvent
from apps.locations.models import Province, Tikina, Village

from .permissions import is_system_administrator


def province_ids_for_admin(user):
    if is_system_administrator(user):
        return Province.objects.values_list("pk", flat=True)
    return villages_for_user(user).values_list("tikina__province_id", flat=True).distinct()


def users_for_admin(user):
    queryset = User.objects.prefetch_related(
        "role_assignments__role",
        "location_assignments__province",
        "location_assignments__tikina",
        "location_assignments__village",
    )
    if is_system_administrator(user):
        return queryset
    province_ids = province_ids_for_admin(user)
    return queryset.filter(
        Q(location_assignments__province_id__in=province_ids)
        | Q(location_assignments__tikina__province_id__in=province_ids)
        | Q(location_assignments__village__tikina__province_id__in=province_ids),
        location_assignments__is_active=True,
    ).exclude(
        Q(is_superuser=True)
        | Q(role_assignments__is_active=True, role_assignments__role__code__in=(Role.Codes.SYSTEM_ADMIN, Role.Codes.PROVINCIAL_ADMIN))
    ).distinct()


def locations_for_admin(user):
    province_ids = province_ids_for_admin(user)
    return (
        Province.objects.filter(pk__in=province_ids),
        Tikina.objects.filter(province_id__in=province_ids).select_related("province"),
        Village.objects.filter(tikina__province_id__in=province_ids).select_related("tikina__province"),
    )


def audit_events_for_admin(user):
    queryset = AuditEvent.objects.select_related("actor", "province", "tikina", "village")
    if is_system_administrator(user):
        return queryset
    province_ids = province_ids_for_admin(user)
    return queryset.filter(
        Q(province_id__in=province_ids)
        | Q(tikina__province_id__in=province_ids)
        | Q(village__tikina__province_id__in=province_ids)
    ).distinct()


def user_location_label(user):
    assignment = next((item for item in user.location_assignments.all() if item.is_active), None)
    return str(assignment.village or assignment.tikina or assignment.province) if assignment else "Unassigned"

