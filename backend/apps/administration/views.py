from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.accounts.models import Role
from apps.locations.models import Province, Tikina, Village
from apps.reporting.models import ReportingPeriod

from .forms import AdministrativePasswordForm, AdministrativeUserForm, ProvinceForm, ReportingPeriodForm, TikinaForm, VillageForm
from .permissions import administration_required, is_system_administrator
from .selectors import audit_events_for_admin, locations_for_admin, province_ids_for_admin, user_location_label, users_for_admin
from .services import audit_change, snapshot_user


def _page(request, queryset, size=25):
    return Paginator(queryset, size).get_page(request.GET.get("page"))


def _system_only(request):
    if not is_system_administrator(request.user):
        raise PermissionDenied("Only a System Administrator can perform this action.")


@administration_required
def dashboard(request):
    users = users_for_admin(request.user)
    periods = ReportingPeriod.objects.all()
    provinces, tikina, villages = locations_for_admin(request.user)
    return render(request, "administration/dashboard.html", {
        "total_users": users.count(), "active_users": users.filter(is_active=True).count(),
        "inactive_users": users.filter(is_active=False).count(),
        "administrator_count": users.filter(role_assignments__is_active=True, role_assignments__role__code__in=(Role.Codes.SYSTEM_ADMIN, Role.Codes.PROVINCIAL_ADMIN)).distinct().count(),
        "reporting_user_count": users.filter(role_assignments__is_active=True, role_assignments__role__code__in=(Role.Codes.TURAGA_NI_KORO, Role.Codes.VILLAGE_DATA_ASSISTANT)).distinct().count(),
        "open_periods": periods.filter(is_open=True, is_locked=False).count(), "closed_periods": periods.filter(is_open=False).count(),
        "current_period": periods.filter(is_open=True, is_locked=False).order_by("-start_date").first(),
        "province_count": provinces.count(), "tikina_count": tikina.count(), "village_count": villages.count(),
        "recent_events": audit_events_for_admin(request.user)[:6], "is_system_administrator": is_system_administrator(request.user),
    })


@administration_required
def user_list(request):
    users = users_for_admin(request.user)
    query = request.GET.get("q", "").strip()
    if query:
        users = users.filter(Q(username__icontains=query) | Q(first_name__icontains=query) | Q(last_name__icontains=query) | Q(email__icontains=query))
    if request.GET.get("role"):
        users = users.filter(role_assignments__is_active=True, role_assignments__role__code=request.GET["role"])
    if request.GET.get("status") in ("active", "inactive"):
        users = users.filter(is_active=request.GET["status"] == "active")
    if request.GET.get("province"):
        province = request.GET["province"]
        users = users.filter(Q(location_assignments__province_id=province) | Q(location_assignments__tikina__province_id=province) | Q(location_assignments__village__tikina__province_id=province)).distinct()
    page = _page(request, users.order_by("first_name", "last_name", "username"))
    rows = [{"user": item, "role": next((a.role for a in item.role_assignments.all() if a.is_active), None), "location": user_location_label(item)} for item in page.object_list]
    page.object_list = rows
    return render(request, "administration/users/list.html", {"page_obj": page, "roles": Role.objects.filter(is_active=True), "provinces": locations_for_admin(request.user)[0], "filters": request.GET})


def _scoped_user(request, user_uuid):
    return get_object_or_404(users_for_admin(request.user), uuid=user_uuid)


@administration_required
def user_detail(request, user_uuid):
    target = _scoped_user(request, user_uuid)
    return render(request, "administration/users/detail.html", {"target": target, "roles": target.role_assignments.select_related("role"), "locations": target.location_assignments.select_related("province", "tikina", "village")})


@administration_required
def user_create(request):
    form = AdministrativeUserForm(request.POST or None, actor=request.user)
    if request.method == "POST" and form.is_valid():
        target = form.save()
        audit_change(request, "user.created", target, f"Created user {target.username}", current=snapshot_user(target))
        messages.success(request, "User created successfully.")
        return redirect("administration:user_detail", user_uuid=target.uuid)
    return render(request, "administration/users/form.html", {"form": form, "heading": "Create user", "submit_label": "Create user"})


@administration_required
def user_edit(request, user_uuid):
    target = _scoped_user(request, user_uuid)
    previous = snapshot_user(target)
    form = AdministrativeUserForm(request.POST or None, instance=target, actor=request.user)
    if request.method == "POST" and form.is_valid():
        target = form.save()
        audit_change(request, "user.updated", target, f"Updated user {target.username}", previous, snapshot_user(target))
        messages.success(request, "User updated successfully.")
        return redirect("administration:user_detail", user_uuid=target.uuid)
    return render(request, "administration/users/form.html", {"form": form, "heading": "Edit user", "submit_label": "Save changes", "target": target})


@administration_required
@require_POST
def user_toggle_active(request, user_uuid):
    target = _scoped_user(request, user_uuid)
    if target == request.user:
        raise PermissionDenied("You cannot deactivate your own account.")
    if target.is_active and is_system_administrator(target):
        another_system_admin = users_for_admin(request.user).filter(
            is_active=True,
            role_assignments__is_active=True,
            role_assignments__role__code=Role.Codes.SYSTEM_ADMIN,
        ).exclude(pk=target.pk).exists()
        if not another_system_admin:
            raise PermissionDenied("The last active System Administrator cannot be deactivated.")
    previous = snapshot_user(target)
    target.is_active = not target.is_active
    target.save(update_fields=("is_active",))
    action = "activated" if target.is_active else "deactivated"
    audit_change(request, f"user.{action}", target, f"{action.title()} user {target.username}", previous, snapshot_user(target))
    messages.success(request, f"User has been {action}.")
    return redirect("administration:user_detail", user_uuid=target.uuid)


@administration_required
def user_password(request, user_uuid):
    target = _scoped_user(request, user_uuid)
    form = AdministrativePasswordForm(target, request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        audit_change(request, "user.password_reset", target, f"Reset password for {target.username}")
        messages.success(request, "The temporary password was set securely.")
        return redirect("administration:user_detail", user_uuid=target.uuid)
    return render(request, "administration/users/form.html", {"form": form, "heading": "Set temporary password", "submit_label": "Set password", "target": target})


@administration_required
def period_list(request):
    return render(request, "administration/periods/list.html", {"page_obj": _page(request, ReportingPeriod.objects.all()), "is_system_administrator": is_system_administrator(request.user)})


@administration_required
def period_form(request, period_uuid=None):
    _system_only(request)
    instance = get_object_or_404(ReportingPeriod, uuid=period_uuid) if period_uuid else None
    previous = {f: str(getattr(instance, f)) for f in ("year", "quarter", "start_date", "end_date", "submission_due_date", "is_open", "is_locked")} if instance else None
    form = ReportingPeriodForm(request.POST or None, instance=instance)
    if request.method == "POST" and form.is_valid():
        period = form.save()
        current = {f: str(getattr(period, f)) for f in ("year", "quarter", "start_date", "end_date", "submission_due_date", "is_open", "is_locked")}
        audit_change(request, "reporting_period.updated" if instance else "reporting_period.created", period, f"Saved reporting period {period}", previous, current)
        messages.success(request, "Reporting period saved successfully.")
        return redirect("administration:period_list")
    return render(request, "administration/generic_form.html", {"form": form, "heading": "Edit reporting period" if instance else "Create reporting period", "cancel_url": "administration:period_list"})


@administration_required
@require_POST
def period_toggle(request, period_uuid, action):
    _system_only(request)
    period = get_object_or_404(ReportingPeriod, uuid=period_uuid)
    previous = {"is_open": period.is_open, "is_locked": period.is_locked}
    if action == "open":
        period.is_open, period.is_locked = True, False
    elif action == "close":
        period.is_open = False
    elif action == "lock":
        period.is_open, period.is_locked = False, True
    else:
        raise PermissionDenied("Unsupported reporting-period action.")
    period.full_clean()
    period.save(update_fields=("is_open", "is_locked", "updated_at"))
    action_label = {"open": "Opened", "close": "Closed", "lock": "Locked"}[action]
    audit_change(request, f"reporting_period.{action}", period, f"{action_label} reporting period {period}", previous, {"is_open": period.is_open, "is_locked": period.is_locked})
    messages.success(request, f"Reporting period {action} action completed.")
    return redirect("administration:period_list")


@administration_required
def location_index(request):
    provinces, tikina, villages = locations_for_admin(request.user)
    query = request.GET.get("q", "").strip()
    location_type = request.GET.get("type", "province")
    mapping = {"province": provinces, "tikina": tikina, "village": villages}
    queryset = mapping.get(location_type, provinces)
    if query:
        queryset = queryset.filter(Q(code__icontains=query) | Q(name_en__icontains=query) | Q(name_fj__icontains=query))
    return render(request, "administration/locations/list.html", {"page_obj": _page(request, queryset), "location_type": location_type, "query": query, "is_system_administrator": is_system_administrator(request.user)})


@administration_required
def location_form(request, location_type, location_uuid=None):
    model_forms = {"province": (Province, ProvinceForm), "tikina": (Tikina, TikinaForm), "village": (Village, VillageForm)}
    if location_type not in model_forms:
        raise PermissionDenied("Unknown location type.")
    if location_type == "province":
        _system_only(request)
    model, form_class = model_forms[location_type]
    allowed = locations_for_admin(request.user)[{"province": 0, "tikina": 1, "village": 2}[location_type]]
    instance = get_object_or_404(allowed, uuid=location_uuid) if location_uuid else None
    kwargs = {"instance": instance}
    if location_type != "province":
        kwargs["actor"] = request.user
    form = form_class(request.POST or None, **kwargs)
    if request.method == "POST" and form.is_valid():
        location = form.save()
        audit_change(request, f"location.{location_type}.updated" if instance else f"location.{location_type}.created", location, f"Saved {location_type} {location}")
        messages.success(request, "Location saved successfully.")
        return redirect("administration:location_list")
    return render(request, "administration/generic_form.html", {"form": form, "heading": f"{'Edit' if instance else 'Add'} {location_type.title()}", "cancel_url": "administration:location_list"})


@administration_required
def audit_list(request):
    events = audit_events_for_admin(request.user)
    query = request.GET.get("q", "").strip()
    if query:
        events = events.filter(Q(summary__icontains=query) | Q(action__icontains=query) | Q(actor__username__icontains=query) | Q(object_type__icontains=query))
    return render(request, "administration/audit/list.html", {"page_obj": _page(request, events, 50), "query": query})


@administration_required
def location_options(request):
    province_ids = province_ids_for_admin(request.user)
    for field in ("province", "tikina"):
        if request.GET.get(field) and (not request.GET[field].isascii() or not request.GET[field].isdigit() or len(request.GET[field]) > 18):
            return JsonResponse({"results": [], "error": "Select a valid location ID."}, status=400)
    if request.GET.get("province"):
        rows = Tikina.objects.filter(province_id=request.GET["province"], province_id__in=province_ids, province__is_active=True, is_active=True).values("id", "uuid", "name_en")
    elif request.GET.get("tikina"):
        rows = Village.objects.filter(tikina_id=request.GET["tikina"], tikina__province_id__in=province_ids, tikina__is_active=True, tikina__province__is_active=True, is_active=True).values("id", "uuid", "name_en")
    else:
        rows = []
    return JsonResponse({"results": list(rows)})
