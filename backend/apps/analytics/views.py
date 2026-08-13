import json
import logging

from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render
from django.db.models import Count
from apps.reporting.models import TNKReport
from apps.reporting.selectors import reports_for_user
from apps.core.security import can_export_report_summary, can_view_analytics
from django.core.exceptions import PermissionDenied
from .exports import csv_export,pdf_export,xlsx_export
from .models import IndicatorValue


export_logger = logging.getLogger("tnk.export")

FILTER_LOOKUPS = {
    "year": "reporting_period__year",
    "quarter": "reporting_period__quarter",
    "province": "village__tikina__province_id",
    "tikina": "village__tikina_id",
    "village": "village_id",
}


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


@login_required
def dashboard(request):
    if not can_view_analytics(request.user):
        raise PermissionDenied("Your role cannot access TNK analytics.")
    reports=reports_for_user(request.user).select_related("village__tikina__province", "reporting_period")
    provinces=reports.values("village__tikina__province_id", "village__tikina__province__name_en").distinct().order_by("village__tikina__province__name_en")
    tikinas=reports.values("village__tikina_id", "village__tikina__name_en").distinct().order_by("village__tikina__name_en")
    villages_in_scope=reports.values("village_id", "village__name_en").distinct().order_by("village__name_en")
    reports, _applied_filters = apply_report_filters(reports, request.GET)
    indicator_values = IndicatorValue.objects.filter(
        village_id__in=reports.values("village_id"),
        reporting_period_id__in=reports.values("reporting_period_id"),
        indicator__is_active=True,
    ).select_related("indicator", "village", "reporting_period").order_by("indicator__name_en", "village__name_en")[:100]
    from apps.reporting.amendments import apply_indicator_overrides

    indicator_values = apply_indicator_overrides(indicator_values)
    status_data=list(reports.values("status").annotate(count=Count("pk")).order_by("status")); villages=[{"name":r.village.name_en,"lat":float(r.village.latitude),"lng":float(r.village.longitude)} for r in reports if r.village.latitude is not None and r.village.longitude is not None]
    return render(request,"analytics/dashboard.html",{"reports":reports[:100],"indicator_values":indicator_values,"total":reports.count(),"awaiting_review":reports.filter(status__in=("submitted","under_tikina_review","under_provincial_review")).count(),"status_data_json":json.dumps(status_data),"villages_json":json.dumps(villages),"provinces":provinces,"tikinas":tikinas,"villages_in_scope":villages_in_scope,"status_choices":TNKReport.Status.choices,"selected_province":request.GET.get("province", ""),"selected_tikina":request.GET.get("tikina", ""),"selected_village":request.GET.get("village", "")})
@login_required
def export_reports(request,format):
    if not can_export_report_summary(request.user):
        raise PermissionDenied("Your role cannot export TNK analytics.")
    exporters={"csv":csv_export,"xlsx":xlsx_export,"pdf":pdf_export}
    if format not in exporters: raise Http404
    reports, filters = apply_report_filters(reports_for_user(request.user), request.GET)
    try:
        return exporters[format](request.user,reports,filters,request.GET.get("reason",""))
    except Exception:
        export_logger.exception(
            "Report export failed",
            extra={"event": "export.failed", "request_id": getattr(request, "request_id", "")},
        )
        raise
