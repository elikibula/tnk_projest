from decimal import Decimal

from django.db import transaction

from apps.locations.models import Province, Tikina
from apps.reporting.models import TNKReport

from .calculations import IndicatorResult, calculate_health_preview, calculate_report_results
from .catalogue import CATALOGUE, CATALOGUE_EFFECTIVE_FROM
from .models import IndicatorDefinition, IndicatorValue


AVERAGE_CODES = {
    "average_household_size",
    "average_water_outage_days",
    "average_energy_availability_hours",
    "average_health_facility_travel_time",
    "average_food_shortage_days",
    "physical_progress_average",
    "financial_progress_average",
}
PER_THOUSAND_CODES = {"new_cases_per_1000", "existing_cases_per_1000"}
QUALITY_ORDER = {"high": 4, "medium": 3, "low": 2, "unknown": 1, "no_data": 0, "unavailable": 0}
FOUR_PLACES = Decimal("0.0001")


def stored_decimal(value):
    return value.quantize(FOUR_PLACES) if value is not None else None


def seed_indicator_definitions():
    definitions = []
    for spec in CATALOGUE:
        definition, _ = IndicatorDefinition.objects.update_or_create(
            code=spec.code,
            version=1,
            defaults={
                "name_en": spec.name_en,
                "description": spec.formula,
                "numerator_definition": spec.numerator,
                "denominator_definition": spec.denominator,
                "formula_description": spec.formula,
                "measurement_unit": spec.unit,
                "frequency": "quarterly",
                "geographic_level": "village, Tikina, province",
                "data_source": spec.source,
                "disaggregation": spec.disaggregation,
                "missing_value_rule": spec.missing,
                "verification_requirement": spec.verification,
                "implementation_status": "available" if spec.available else "unavailable",
                "unavailable_reason": spec.unavailable_reason,
                "effective_from": CATALOGUE_EFFECTIVE_FROM,
                "is_active": True,
            },
        )
        definitions.append(definition)
    return definitions


def quality_rating(report, result):
    if result.status != "calculated":
        return result.status
    score = report.data_quality_score
    if score is None:
        return "unknown"
    if score >= 80:
        return "high"
    if score >= 60:
        return "medium"
    return "low"


def _location_defaults(village):
    return {"province": village.tikina.province, "tikina": village.tikina, "village": village}


@transaction.atomic
def calculate_village_indicators(report, *, refresh=None):
    if refresh is None:
        refresh = report.is_editable
    definitions = {definition.code: definition for definition in seed_indicator_definitions()}
    results = calculate_report_results(report)
    values = []
    for code, result in results.items():
        defaults = {
            **_location_defaults(report.village),
            "value": stored_decimal(result.value),
            "numerator_value": stored_decimal(result.numerator),
            "denominator_value": stored_decimal(result.denominator),
            "breakdown": result.breakdown,
            "calculation_status": result.status,
            "calculation_notes": result.notes,
            "source_report_count": 1,
            "data_quality_rating": quality_rating(report, result),
        }
        value, created = IndicatorValue.objects.get_or_create(
            indicator=definitions[code],
            reporting_period=report.reporting_period,
            village=report.village,
            defaults=defaults,
        )
        if not created and refresh:
            for field_name, field_value in defaults.items():
                setattr(value, field_name, field_value)
            value.save(update_fields=(*defaults.keys(), "calculated_at"))
        values.append(value)
    return values


def preview_health_indicators(report, *, health_condition=None, gender=None, age_group=None):
    return calculate_health_preview(
        report,
        health_condition_id=getattr(health_condition, "pk", health_condition),
        gender=gender,
        age_group_id=getattr(age_group, "pk", age_group),
    )


def _aggregate_scale(code):
    if code in PER_THOUSAND_CODES:
        return Decimal("1000")
    if code in AVERAGE_CODES:
        return Decimal("1")
    return Decimal("100")


def _combine_results(code, values):
    calculated_values = [value for value in values if value.calculation_status == "calculated"]
    if not calculated_values:
        status = "unavailable" if values and all(value.calculation_status == "unavailable" for value in values) else "no_data"
        notes = next((value.calculation_notes for value in values if value.calculation_notes), "No calculated village values are available.")
        return IndicatorResult(None, status=status, notes=notes)
    breakdown = {}
    for value in calculated_values:
        for key, count in value.breakdown.items():
            breakdown[key] = breakdown.get(key, 0) + count
    with_denominator = [
        value
        for value in calculated_values
        if getattr(value, "authoritative_denominator", value.denominator_value) is not None
    ]
    if with_denominator:
        numerator = sum(
            (getattr(value, "authoritative_numerator", value.numerator_value) or Decimal("0"))
            for value in with_denominator
        )
        denominator = sum(
            (getattr(value, "authoritative_denominator", value.denominator_value) or Decimal("0"))
            for value in with_denominator
        )
        if denominator == 0:
            return IndicatorResult(None, numerator, denominator, "no_data", "The aggregate denominator is zero.", breakdown)
        return IndicatorResult(numerator / denominator * _aggregate_scale(code), numerator, denominator, breakdown=breakdown)
    total = sum((getattr(value, "authoritative_value", value.value) or Decimal("0")) for value in calculated_values)
    return IndicatorResult(total, total, None, breakdown=breakdown)


def _worst_quality(values):
    ratings = [value.data_quality_rating for value in values]
    return min(ratings, key=lambda rating: QUALITY_ORDER.get(rating, 1), default="unknown")


@transaction.atomic
def aggregate_indicators(reporting_period, location):
    if isinstance(location, Tikina):
        village_values = IndicatorValue.objects.filter(reporting_period=reporting_period, village__tikina=location)
        location_fields = {"province": location.province, "tikina": location, "village": None}
        lookup = {"tikina": location, "village": None}
    elif isinstance(location, Province):
        village_values = IndicatorValue.objects.filter(reporting_period=reporting_period, village__tikina__province=location)
        location_fields = {"province": location, "tikina": None, "village": None}
        lookup = {"province": location, "tikina": None, "village": None}
    else:
        raise TypeError("Indicator aggregation requires a Tikina or Province.")
    definitions = seed_indicator_definitions()
    from apps.reporting.amendments import apply_indicator_overrides

    output = []
    for definition in definitions:
        sources = apply_indicator_overrides(village_values.filter(indicator=definition))
        result = _combine_results(definition.code, sources)
        defaults = {
            **location_fields,
            "value": stored_decimal(result.value),
            "numerator_value": stored_decimal(result.numerator),
            "denominator_value": stored_decimal(result.denominator),
            "breakdown": result.breakdown,
            "calculation_status": result.status,
            "calculation_notes": result.notes,
            "source_report_count": len({value.village_id for value in sources}),
            "data_quality_rating": _worst_quality(sources),
        }
        value, _ = IndicatorValue.objects.update_or_create(
            indicator=definition,
            reporting_period=reporting_period,
            defaults=defaults,
            **lookup,
        )
        output.append(value)
    return output


def calculate_period_indicators(reporting_period, *, statuses=None):
    statuses = statuses or (TNKReport.Status.APPROVED, TNKReport.Status.LOCKED, TNKReport.Status.ARCHIVED)
    reports = TNKReport.objects.filter(reporting_period=reporting_period, status__in=statuses).select_related(
        "village__tikina__province", "reporting_period"
    )
    output = []
    tikinas, provinces = set(), set()
    for report in reports:
        output.extend(calculate_village_indicators(report))
        tikinas.add(report.village.tikina)
        provinces.add(report.village.tikina.province)
    for tikina in tikinas:
        output.extend(aggregate_indicators(reporting_period, tikina))
    for province in provinces:
        output.extend(aggregate_indicators(reporting_period, province))
    return output
