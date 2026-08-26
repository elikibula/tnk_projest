from decimal import Decimal

from django.db.models import Count, Q

from apps.accounts.models import Role
from apps.accounts.permissions import user_has_any_role
from apps.accounts.selectors import villages_for_user
from apps.analytics.models import IndicatorValue
from apps.locations.models import Province, Tikina, Village
from apps.reporting.models import ReportingPeriod, TNKReport

OFFICIAL_STATUSES = (TNKReport.Status.APPROVED, TNKReport.Status.LOCKED, TNKReport.Status.ARCHIVED)
RECEIVED_STATUSES = (
    TNKReport.Status.SUBMITTED,
    TNKReport.Status.UNDER_TIKINA_REVIEW,
    TNKReport.Status.UNDER_PROVINCIAL_REVIEW,
    *OFFICIAL_STATUSES,
)
ATTENTION_COMPLETION = Decimal("70")

INDICATORS = {
    "population": ("total_population", "Total population", "people"),
    "households": ("average_household_size", "Households", "households"),
    "projects": ("project_completion_rate", "Development projects", "projects"),
    "water_issues": ("water_failure_count", "Water interruptions", "interruptions"),
    "health_cases": ("new_cases_per_1000", "New health cases", "cases"),
    "disability_cases": ("disability_prevalence", "Disability records", "people"),
    "climate_incidents": ("climate_incident_count", "Climate and disaster incidents", "incidents"),
}


def percentage_change(previous, current):
    if previous is None or current is None:
        return None
    previous, current = Decimal(previous), Decimal(current)
    if previous == 0:
        return Decimal("0") if current == 0 else None
    return (current - previous) / abs(previous) * 100


def can_view_national(user):
    return user.is_superuser or user_has_any_role(user, {Role.Codes.SYSTEM_ADMIN})


def periods():
    return ReportingPeriod.objects.all().order_by("-year", "-quarter")


def selected_period(raw):
    queryset = periods()
    if raw and str(raw).isdigit():
        return queryset.filter(pk=int(raw)).first() or queryset.first()
    return queryset.filter(is_open=True, is_locked=False).first() or queryset.first()


def scoped_villages(user):
    queryset = Village.objects.all() if can_view_national(user) else villages_for_user(user)
    return queryset.filter(is_active=True).select_related("tikina__province")


def scoped_provinces(user):
    return Province.objects.filter(tikina__villages__in=scoped_villages(user)).distinct().order_by("name_en")


def reports_in_scope(user, period=None):
    queryset = TNKReport.objects.filter(village__in=scoped_villages(user)).select_related("village__tikina__province", "reporting_period")
    return queryset.filter(reporting_period=period) if period else queryset


def _scope_filter(scope):
    if isinstance(scope, Province):
        return Q(village__tikina__province=scope)
    if isinstance(scope, Tikina):
        return Q(village__tikina=scope)
    if isinstance(scope, Village):
        return Q(village=scope)
    return Q()


def _villages_for_scope(user, scope=None):
    queryset = scoped_villages(user)
    if isinstance(scope, Province):
        queryset = queryset.filter(tikina__province=scope)
    elif isinstance(scope, Tikina):
        queryset = queryset.filter(tikina=scope)
    elif isinstance(scope, Village):
        queryset = queryset.filter(pk=scope.pk)
    return queryset


def reporting_summary(user, period, scope=None):
    villages = _villages_for_scope(user, scope)
    reports = TNKReport.objects.filter(village__in=villages, reporting_period=period)
    status_counts = {row["status"]: row["count"] for row in reports.values("status").annotate(count=Count("pk"))}
    expected = villages.count()
    received = reports.filter(status__in=RECEIVED_STATUSES).values("village_id").distinct().count()
    official = reports.filter(status__in=OFFICIAL_STATUSES).values("village_id").distinct().count()
    completion = Decimal(received * 100) / expected if expected else Decimal("0")
    return {
        "expected": expected,
        "received": received,
        "official": official,
        "missing": max(expected - received, 0),
        "completion": completion.quantize(Decimal("0.1")),
        "draft": status_counts.get(TNKReport.Status.DRAFT, 0) + status_counts.get(TNKReport.Status.READY_FOR_VALIDATION, 0),
        "submitted": sum(status_counts.get(code, 0) for code in RECEIVED_STATUSES),
        "approved": sum(status_counts.get(code, 0) for code in OFFICIAL_STATUSES),
        "returned": status_counts.get(TNKReport.Status.RETURNED_TO_VILLAGE, 0),
        "rejected": status_counts.get(TNKReport.Status.REJECTED, 0),
        "status_counts": status_counts,
    }


def indicator_totals(user, period, scope=None):
    villages = _villages_for_scope(user, scope)
    values = IndicatorValue.objects.filter(
        reporting_period=period,
        village__in=villages,
        calculation_status=IndicatorValue.CalculationStatus.CALCULATED,
        indicator__code__in=[spec[0] for spec in INDICATORS.values()],
    )
    from apps.reporting.amendments import apply_indicator_overrides

    rows_by_code = {}
    for value in apply_indicator_overrides(values.select_related("indicator")):
        rows_by_code.setdefault(value.indicator.code, []).append(value)
    output = {}
    for key, (code, label, unit) in INDICATORS.items():
        rows = rows_by_code.get(code, [])
        if key in {"households", "projects"}:
            numbers = [value.authoritative_denominator for value in rows if value.authoritative_denominator is not None]
        elif key in {"health_cases", "disability_cases"}:
            numbers = [value.authoritative_numerator for value in rows if value.authoritative_numerator is not None]
        else:
            numbers = [value.authoritative_value for value in rows if value.authoritative_value is not None]
        output[key] = {"value": sum(numbers, Decimal("0")) if numbers else None, "label": label, "unit": unit, "has_data": bool(numbers), "definition": code}
    return output


def summary(user, period, scope=None):
    return {"reporting": reporting_summary(user, period, scope), "indicators": indicator_totals(user, period, scope), "period": period, "scope": scope}


def child_locations(user, scope=None):
    villages = _villages_for_scope(user, scope)
    if scope is None:
        return list(Province.objects.filter(tikina__villages__in=villages).distinct().order_by("name_en"))
    if isinstance(scope, Province):
        return list(Tikina.objects.filter(province=scope, villages__in=villages).distinct().order_by("name_en"))
    if isinstance(scope, Tikina):
        return list(villages.filter(tikina=scope).order_by("name_en"))
    return []


def location_rows(user, period, scope=None):
    rows = []
    for location in child_locations(user, scope):
        data = summary(user, period, location)
        rows.append({"location": location, **data})
    return rows


def missing_reports(user, period, scope=None):
    villages = _villages_for_scope(user, scope)
    received_ids = TNKReport.objects.filter(village__in=villages, reporting_period=period, status__in=RECEIVED_STATUSES).values("village_id")
    missing = list(villages.exclude(pk__in=received_ids).order_by("tikina__province__name_en", "tikina__name_en", "name_en"))
    latest_by_village = {}
    prior = TNKReport.objects.filter(village_id__in=[item.pk for item in missing], status__in=RECEIVED_STATUSES).select_related("reporting_period").order_by("village_id", "-reporting_period__start_date")
    for report in prior:
        latest_by_village.setdefault(report.village_id, report)
    return [{"village": village, "last_report": latest_by_village.get(village.pk)} for village in missing]


def trends(user, scope=None, limit=8):
    output = []
    for period in list(periods()[:limit])[::-1]:
        data = summary(user, period, scope)
        output.append({"period": str(period), "completion": float(data["reporting"]["completion"]), "population": float(data["indicators"]["population"]["value"] or 0), "population_has_data": data["indicators"]["population"]["has_data"]})
    return output


def insights(current, previous=None):
    cards = []
    reporting = current["reporting"]
    if reporting["missing"]:
        cards.append({"status": "attention" if reporting["completion"] < ATTENTION_COMPLETION else "monitor", "title": "Reporting coverage", "text": f"{reporting['missing']} active village(s) have no received report for this period."})
    else:
        cards.append({"status": "good", "title": "Reporting coverage", "text": "All active villages in scope have a received report for this period."})
    if previous:
        change = percentage_change(previous["reporting"]["completion"], reporting["completion"])
        if change is not None:
            direction = "increased" if change > 0 else "decreased" if change < 0 else "is unchanged"
            cards.append({"status": "good" if change > 0 else "attention" if change < 0 else "stable", "title": "Period comparison", "text": f"Reporting completion {direction} by {abs(change):.1f}% relative to {previous['period']}."})
    water = current["indicators"]["water_issues"]
    if water["has_data"] and water["value"]:
        cards.append({"status": "monitor", "title": "Water and sanitation", "text": f"{water['value']:.0f} water interruption(s) were reported in official data."})
    quality_missing = reporting["received"] - reporting["official"]
    if quality_missing > 0:
        cards.append({"status": "monitor", "title": "Official data availability", "text": f"{quality_missing} received report(s) are not yet approved, locked or archived and are excluded from official indicators."})
    return cards


def scope_breadcrumbs(scope):
    if isinstance(scope, Village):
        return [scope.tikina.province, scope.tikina, scope]
    if isinstance(scope, Tikina):
        return [scope.province, scope]
    return [scope] if scope else []
