import csv
import json
import logging

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from apps.core.security import can_export_report_summary, can_view_analytics
from apps.locations.models import Province, Tikina, Village
from apps.reporting.models import TNKReport
from apps.reporting.selectors import reports_for_user

from .decision_support import can_view_national, insights, location_rows, missing_reports, percentage_change, periods, scope_breadcrumbs, scoped_provinces, scoped_villages, selected_period, summary, trends
from .exports import csv_export, pdf_export, xlsx_export

export_logger = logging.getLogger("tnk.export")
FILTER_LOOKUPS = {"year": "reporting_period__year", "quarter": "reporting_period__quarter", "province": "village__tikina__province_id", "tikina": "village__tikina_id", "village": "village_id"}


def apply_report_filters(reports, values):
    """Apply only well-formed filters; invalid query strings must not cause a 500."""
    applied = {}
    for key, lookup in FILTER_LOOKUPS.items():
        raw = values.get(key, "")
        if raw and str(raw).isdigit():
            number = int(raw)
            if key == "quarter" and number not in range(1, 5):
                continue
            reports = reports.filter(**{lookup: number})
            applied[key] = str(number)
    status = values.get("status", "")
    if status in TNKReport.Status.values:
        reports = reports.filter(status=status)
        applied["status"] = status
    return reports, applied


def analytics_required(view):
    @login_required
    def wrapped(request, *args, **kwargs):
        if not can_view_analytics(request.user):
            raise PermissionDenied("Your role cannot access TNK analytics.")
        return view(request, *args, **kwargs)
    return wrapped


def _previous_period(period):
    return periods().filter(start_date__lt=period.start_date).order_by("-start_date").first() if period else None


def _context(request, scope=None):
    period = selected_period(request.GET.get("period"))
    current = summary(request.user, period, scope) if period else None
    comparison_period = selected_period(request.GET.get("compare_period")) if request.GET.get("compare_period") else _previous_period(period)
    previous = summary(request.user, comparison_period, scope) if comparison_period else None
    rows = location_rows(request.user, period, scope) if period else []
    comparison = []
    if current and previous:
        for key, item in current["indicators"].items():
            old = previous["indicators"][key]
            comparison.append({"key": key, "label": item["label"], "current": item["value"], "previous": old["value"], "unit": item["unit"], "change": percentage_change(old["value"], item["value"]), "has_current": item["has_data"], "has_previous": old["has_data"]})
    map_villages = scoped_villages(request.user)
    if isinstance(scope, Province):
        map_villages = map_villages.filter(tikina__province=scope)
    elif isinstance(scope, Tikina):
        map_villages = map_villages.filter(tikina=scope)
    elif isinstance(scope, Village):
        map_villages = map_villages.filter(pk=scope.pk)
    map_data = [{"name": village.name_en, "lat": float(village.latitude), "lng": float(village.longitude)} for village in map_villages.exclude(latitude__isnull=True).exclude(longitude__isnull=True)]
    return {"scope": scope, "scope_type": scope._meta.model_name if scope else "national", "breadcrumbs": scope_breadcrumbs(scope), "periods": periods(), "selected_period": period, "comparison_period": comparison_period, "summary": current, "comparison": comparison, "rows": rows, "insights": insights(current, previous) if current else [], "missing_rows": missing_reports(request.user, period, scope) if period else [], "trends_json": json.dumps(trends(request.user, scope)), "comparison_json": json.dumps({"labels": [row["location"].name_en for row in rows], "completion": [float(row["reporting"]["completion"]) for row in rows], "population": [float(row["indicators"]["population"]["value"] or 0) for row in rows]}), "villages_json": json.dumps(map_data), "is_national_user": can_view_national(request.user), "data_scope_label": "Approved, locked and archived reports for indicators; received workflow states for compliance"}


@analytics_required
def dashboard(request):
    scope = None if can_view_national(request.user) else scoped_provinces(request.user).first()
    return render(request, "analytics/decision_dashboard.html", _context(request, scope))


@analytics_required
def national(request):
    if not can_view_national(request.user):
        raise PermissionDenied("National analytics requires national authority.")
    return render(request, "analytics/decision_dashboard.html", _context(request))


def _scoped_location(request, model, **lookup):
    villages = scoped_villages(request.user)
    if model is Province:
        queryset = Province.objects.filter(tikina__villages__in=villages).distinct()
    elif model is Tikina:
        queryset = Tikina.objects.filter(villages__in=villages).select_related("province").distinct()
    else:
        queryset = villages
    return get_object_or_404(queryset, **lookup)


@analytics_required
def province(request, location_uuid):
    return render(request, "analytics/decision_dashboard.html", _context(request, _scoped_location(request, Province, uuid=location_uuid)))


@analytics_required
def tikina(request, location_uuid):
    return render(request, "analytics/decision_dashboard.html", _context(request, _scoped_location(request, Tikina, uuid=location_uuid)))


@analytics_required
def village(request, location_uuid):
    return render(request, "analytics/decision_dashboard.html", _context(request, _scoped_location(request, Village, uuid=location_uuid)))


def _comparison_choices(user, level):
    villages = scoped_villages(user)
    if level == "province":
        return Province.objects.filter(tikina__villages__in=villages).distinct().order_by("name_en")
    if level == "tikina":
        return Tikina.objects.filter(villages__in=villages).distinct().order_by("name_en")
    return villages.order_by("name_en")


@analytics_required
def compare(request):
    level = request.GET.get("level", "province")
    level = level if level in {"province", "tikina", "village"} else "province"
    choices, period = _comparison_choices(request.user, level), selected_period(request.GET.get("period"))
    selected = []
    for raw in request.GET.getlist("locations")[:5]:
        if str(raw).isdigit():
            location = choices.filter(pk=int(raw)).first()
            if location:
                selected.append({"location": location, **summary(request.user, period, location)})
    return render(request, "analytics/compare.html", {"level": level, "choices": choices, "selected": selected, "periods": periods(), "selected_period": period})


@analytics_required
def reporting(request):
    scope = None if can_view_national(request.user) else scoped_provinces(request.user).first()
    return render(request, "analytics/reporting.html", _context(request, scope))


@analytics_required
def data_quality(request):
    from apps.data_quality.models import DataQualityIssue

    scope = None if can_view_national(request.user) else scoped_provinces(request.user).first()
    period = selected_period(request.GET.get("period"))
    reports = TNKReport.objects.filter(village__in=scoped_villages(request.user))
    if period:
        reports = reports.filter(reporting_period=period)
    issues = DataQualityIssue.objects.filter(report__in=reports, resolved=False).select_related("report__village__tikina__province", "report__reporting_period", "rule")
    context = {"periods": periods(), "selected_period": period, "issues": issues.order_by("-created_at")[:250], "issue_count": issues.count(), "critical_count": issues.filter(severity__in=("critical", "error")).count(), "incomplete_reports": reports.filter(completeness_percentage__lt=100).count(), "scope": scope, "is_national_user": can_view_national(request.user)}
    return render(request, "analytics/data_quality.html", context)


@analytics_required
def search_locations(request):
    query, results = request.GET.get("q", "").strip(), []
    if query:
        groups = ((scoped_provinces(request.user).filter(name_en__icontains=query)[:5], "province"), (Tikina.objects.filter(villages__in=scoped_villages(request.user), name_en__icontains=query).distinct()[:5], "tikina"), (scoped_villages(request.user).filter(name_en__icontains=query)[:10], "village"))
        for queryset, name in groups:
            for location in queryset:
                results.append({"name": location.name_en, "type": name, "url": reverse(f"analytics:{name}", args=(location.uuid,))})
    return render(request, "analytics/search_results.html", {"results": results, "query": query})


@analytics_required
def export_summary(request):
    if not can_export_report_summary(request.user):
        raise PermissionDenied("Your role cannot export TNK analytics.")
    scope_type, scope_uuid, scope = request.GET.get("scope_type", "national"), request.GET.get("scope"), None
    if scope_type in {"province", "tikina", "village"} and scope_uuid:
        scope = _scoped_location(request, {"province": Province, "tikina": Tikina, "village": Village}[scope_type], uuid=scope_uuid)
    elif not can_view_national(request.user):
        scope = scoped_provinces(request.user).first()
    period, rows = selected_period(request.GET.get("period")), []
    if period:
        rows = location_rows(request.user, period, scope)
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="tnk-analytics-summary.csv"'
    response.write("\ufeff")
    writer = csv.writer(response)
    writer.writerow(("Location", "Expected reports", "Received reports", "Completion %", "Population", "Households", "Projects", "Water interruptions", "Health cases"))
    for row in rows:
        indicator = row["indicators"]
        metric = lambda key: indicator[key]["value"] if indicator[key]["has_data"] else "No Data"
        writer.writerow((row["location"].name_en, row["reporting"]["expected"], row["reporting"]["received"], row["reporting"]["completion"], metric("population"), metric("households"), metric("projects"), metric("water_issues"), metric("health_cases")))
    from .models import DataExportAudit
    DataExportAudit.objects.create(generated_by=request.user, report_type="analytics_summary", filters_used={"period": period.pk if period else None, "scope_type": scope_type, "scope": scope_uuid}, number_of_records=len(rows), export_reason=request.GET.get("reason", ""), format="csv")
    return response


@login_required
def export_reports(request, format):
    if not can_export_report_summary(request.user):
        raise PermissionDenied("Your role cannot export TNK analytics.")
    exporters = {"csv": csv_export, "xlsx": xlsx_export, "pdf": pdf_export}
    if format not in exporters:
        raise Http404
    reports, filters = apply_report_filters(reports_for_user(request.user), request.GET)
    try:
        return exporters[format](request.user, reports, filters, request.GET.get("reason", ""))
    except Exception:
        export_logger.exception("Report export failed", extra={"event": "export.failed", "request_id": getattr(request, "request_id", "")})
        raise
