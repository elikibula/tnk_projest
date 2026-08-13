from dataclasses import dataclass, field
from decimal import Decimal

from django.db.models import Count, F, Q, Sum

from apps.culture.models import CulturalKnowledgeRecord, TraditionalTitle
from apps.economy.models import CropProductionSnapshot, FoodSecuritySnapshot, VillageBusiness, VillageFinancialSnapshot
from apps.governance.models import CommitteeMeeting, CommitteeMember, MeetingDecision, VillageCommittee
from apps.infrastructure.models import EnergySnapshot, SanitationSnapshot, VillageWaterSource, WaterInterruption, WaterQualityTest
from apps.population.models import Household, PopulationMovement, PopulationSnapshot
from apps.projects.models import IVDPProject, IVDPProjectProgress, ProjectMilestone
from apps.reporting.models import ReportSectionStatus, TNKReport
from apps.resilience.models import ClimateImpactObservation, ClimateResponseAction, DisasterIncident, EvacuationCentre, VillageDisasterPreparedness
from apps.wellbeing.models import DisabilitySnapshot, HealthConditionSnapshot, VillageHealthAccessSnapshot

from .catalogue import CATALOGUE, CATALOGUE_BY_CODE


ZERO = Decimal("0")
HUNDRED = Decimal("100")
THOUSAND = Decimal("1000")


@dataclass(frozen=True)
class IndicatorResult:
    value: Decimal | None
    numerator: Decimal | None = None
    denominator: Decimal | None = None
    status: str = "calculated"
    notes: str = ""
    breakdown: dict = field(default_factory=dict)


def decimal(value):
    return None if value is None else Decimal(value)


def calculated(value, numerator=None, denominator=None, *, breakdown=None, notes=""):
    return IndicatorResult(decimal(value), decimal(numerator), decimal(denominator), "calculated", notes, breakdown or {})


def no_data(notes="Required source data is missing."):
    return IndicatorResult(None, status="no_data", notes=notes)


def unavailable(reason):
    return IndicatorResult(None, status="unavailable", notes=reason)


def ratio(numerator, denominator, scale=HUNDRED):
    if numerator is None or denominator is None:
        return no_data()
    numerator, denominator = decimal(numerator), decimal(denominator)
    if denominator == 0:
        return no_data("The denominator is zero; the indicator is undefined, not zero.")
    return calculated(numerator / denominator * scale, numerator, denominator)


def average(total, count):
    return ratio(total, count, Decimal("1"))


def sum_or_none(queryset, field_name):
    aggregate = queryset.exclude(**{f"{field_name}__isnull": True}).aggregate(value=Sum(field_name), rows=Count("pk"))
    return (decimal(aggregate["value"]), aggregate["rows"])


def section_confirmed(report, section_code):
    return report.section_statuses.filter(
        section_code=section_code,
        status__in=(ReportSectionStatus.Status.COMPLETE, ReportSectionStatus.Status.VERIFIED),
    ).exists()


def count_metric(value, observed):
    if not observed:
        return no_data()
    return calculated(value, value, None)


def effective_households(report):
    period = report.reporting_period
    return Household.objects.filter(village=report.village, effective_from__lte=period.end_date).filter(
        Q(effective_to__isnull=True) | Q(effective_to__gte=period.start_date)
    )


def verified_population(report):
    return PopulationSnapshot.objects.filter(report=report, verification_status="verified")


def age_band(queryset, minimum, maximum=None):
    queryset = queryset.filter(age_group__minimum_age__gte=minimum)
    if maximum is not None:
        queryset = queryset.filter(age_group__maximum_age__isnull=False, age_group__maximum_age__lte=maximum)
    return queryset


def _population_results(report):
    rows = verified_population(report)
    total, total_rows = sum_or_none(rows, "count")
    male, male_rows = sum_or_none(rows.filter(gender__iexact="male"), "count")
    female, female_rows = sum_or_none(rows.filter(gender__iexact="female"), "count")
    children, child_rows = sum_or_none(age_band(rows, 0, 14), "count")
    working, working_rows = sum_or_none(age_band(rows, 15, 64), "count")
    elderly, elderly_rows = sum_or_none(rows.filter(age_group__minimum_age__gte=65), "count")
    movements = PopulationMovement.objects.filter(village=report.village, reporting_period=report.reporting_period)
    births, birth_rows = sum_or_none(movements.filter(movement_type="birth"), "count")
    deaths, death_rows = sum_or_none(movements.filter(movement_type="death"), "count")
    incoming, incoming_rows = sum_or_none(movements.filter(movement_type__in=("moved_in", "returned")), "count")
    outgoing, outgoing_rows = sum_or_none(movements.filter(movement_type__in=("moved_out", "temporarily_left")), "count")
    population_section_confirmed = section_confirmed(report, "population_households")
    incoming_observed = bool(incoming_rows or population_section_confirmed)
    outgoing_observed = bool(outgoing_rows or population_section_confirmed)
    household_count = effective_households(report).count()

    previous = report.previous_report
    if previous is None:
        previous = (
            TNKReport.objects.filter(
                village=report.village,
                reporting_period__end_date__lt=report.reporting_period.start_date,
                status__in=(TNKReport.Status.APPROVED, TNKReport.Status.LOCKED, TNKReport.Status.ARCHIVED),
            )
            .order_by("-reporting_period__end_date")
            .first()
        )
    previous_total = None
    if previous:
        previous_total, _ = sum_or_none(verified_population(previous), "count")

    return {
        "total_population": count_metric(total or ZERO, bool(total_rows)),
        "male_population": count_metric(male or ZERO, bool(male_rows)),
        "female_population": count_metric(female or ZERO, bool(female_rows)),
        "child_population_percentage": ratio(children, total),
        "working_age_percentage": ratio(working, total),
        "elderly_population_percentage": ratio(elderly, total),
        "dependency_ratio": ratio((children or ZERO) + (elderly or ZERO) if child_rows and elderly_rows else None, working),
        "sex_ratio": ratio(male, female),
        "births_this_period": count_metric(births or ZERO, bool(birth_rows or population_section_confirmed)),
        "deaths_this_period": count_metric(deaths or ZERO, bool(death_rows or population_section_confirmed)),
        "net_migration": count_metric((incoming or ZERO) - (outgoing or ZERO), incoming_observed and outgoing_observed),
        "population_growth_rate": ratio(total - previous_total if total is not None and previous_total is not None else None, previous_total),
        "average_household_size": average(total, household_count if household_count else None),
    }


def _governance_results(report):
    period = report.reporting_period
    committees = VillageCommittee.objects.filter(village=report.village).filter(
        Q(formed_date__isnull=True) | Q(formed_date__lte=period.end_date),
        Q(dissolved_date__isnull=True) | Q(dissolved_date__gte=period.start_date),
    )
    active = committees.filter(Q(dissolved_date__isnull=True) | Q(dissolved_date__gte=period.end_date))
    committee_count, active_count = committees.count(), active.count()
    meetings = CommitteeMeeting.objects.filter(report=report)
    committees_met = meetings.filter(committee__in=active).values("committee_id").distinct().count()
    members = CommitteeMember.objects.filter(committee__in=active, joined_date__lte=period.end_date).filter(
        Q(left_date__isnull=True) | Q(left_date__gte=period.end_date)
    )
    member_count = members.count()
    female_count = members.filter(gender__iexact="female").count()
    youth_count = age_band(members, 15, 35).count()
    decisions = MeetingDecision.objects.filter(meeting__report=report)
    completed = decisions.filter(Q(status__iexact="completed") | Q(completion_percentage=100)).count()
    overdue = decisions.filter(due_date__lt=period.end_date).exclude(Q(status__iexact="completed") | Q(completion_percentage=100)).count()
    section_is_confirmed = section_confirmed(report, "leadership_governance")
    return {
        "active_committee_rate": ratio(active_count, committee_count),
        "committee_meeting_rate": ratio(committees_met, active_count),
        "female_committee_representation": ratio(female_count, member_count),
        "youth_committee_representation": ratio(youth_count, member_count),
        "decision_completion_rate": ratio(completed, decisions.count()),
        "overdue_decision_count": count_metric(overdue, bool(decisions.exists() or section_is_confirmed)),
        "committees_with_annual_plan_percentage": ratio(active.filter(annual_plan_available=True).count(), active_count),
    }


def _water_results(report):
    sources = VillageWaterSource.objects.filter(village=report.village, is_active=True)
    interruptions = WaterInterruption.objects.filter(report=report)
    duration, duration_rows = sum_or_none(interruptions, "duration_hours")
    tested = WaterQualityTest.objects.filter(
        water_source__in=sources,
        test_date__range=(report.reporting_period.start_date, report.reporting_period.end_date),
    ).values("water_source_id").distinct().count()
    observed = bool(interruptions.exists() or section_confirmed(report, "water"))
    return {
        "average_water_outage_days": average(duration / Decimal("24") if duration is not None else None, duration_rows),
        "water_failure_count": count_metric(interruptions.count(), observed),
        "percentage_water_sources_tested": ratio(tested, sources.count()),
    }


def _sanitation_results(report):
    rows = SanitationSnapshot.objects.filter(report=report, verification_status="verified")
    functional, functional_rows = sum_or_none(rows, "functional_count")
    nonfunctional, nonfunctional_rows = sum_or_none(rows, "non_functional_count")
    shared, _ = sum_or_none(rows, "shared_count")
    safe, _ = sum_or_none(rows, "safely_managed_count")
    flood, _ = sum_or_none(rows, "flood_vulnerable_count")
    total = (functional or ZERO) + (nonfunctional or ZERO) if functional_rows or nonfunctional_rows else None
    households = effective_households(report).count()
    return {
        "toilet_coverage": ratio(total, households if households else None),
        "functional_sanitation_rate": ratio(functional, total),
        "households_without_toilet": count_metric(max(Decimal(households) - total, ZERO), True) if total is not None and households else no_data(),
        "shared_toilet_rate": ratio(shared, total),
        "safely_managed_sanitation_rate": ratio(safe, total),
        "flood_vulnerable_sanitation_rate": ratio(flood, total),
    }


def _energy_results(report):
    rows = EnergySnapshot.objects.filter(report=report, verification_status="verified", primary_or_backup__iexact="primary")
    connected, connected_rows = sum_or_none(rows, "households_connected")
    working, _ = sum_or_none(rows, "households_with_working_supply")
    solar, solar_rows = sum_or_none(rows.filter(energy_source__icontains="solar"), "households_connected")
    generator, generator_rows = sum_or_none(rows.filter(energy_source__icontains="generator"), "households_connected")
    weighted = ZERO
    weighted_denominator = ZERO
    for row in rows.exclude(average_hours_available_per_day__isnull=True).exclude(households_connected__isnull=True):
        weighted += row.average_hours_available_per_day * row.households_connected
        weighted_denominator += row.households_connected
    households = effective_households(report).count()
    return {
        "electrification_rate": ratio(connected, households if households else None),
        "reliable_energy_coverage": ratio(working, connected),
        "solar_household_coverage": ratio(solar if solar_rows else ZERO, households if households and connected_rows else None),
        "generator_dependency_rate": ratio(generator if generator_rows else ZERO, connected),
        "households_without_electricity": count_metric(max(Decimal(households) - connected, ZERO), True) if connected is not None and households else no_data(),
        "average_energy_availability_hours": average(weighted, weighted_denominator),
    }


def _health_results(report, filters=None):
    filters = filters or {}
    rows = HealthConditionSnapshot.objects.filter(report=report, verification_status="verified")
    for name in ("health_condition_id", "gender", "age_group_id"):
        if filters.get(name) not in (None, ""):
            rows = rows.filter(**{name: filters[name]})
    new, new_rows = sum_or_none(rows, "new_cases")
    existing, existing_rows = sum_or_none(rows, "existing_cases")
    referred, _ = sum_or_none(rows, "referred_cases")
    recovered, _ = sum_or_none(rows, "recovered_cases")
    deaths, death_rows = sum_or_none(rows, "deaths")
    cases = (new or ZERO) + (existing or ZERO) if new_rows or existing_rows else None
    population_rows = verified_population(report)
    if filters.get("gender") not in (None, ""):
        population_rows = population_rows.filter(gender=filters["gender"])
    if filters.get("age_group_id") not in (None, ""):
        population_rows = population_rows.filter(age_group_id=filters["age_group_id"])
    population, _ = sum_or_none(population_rows, "count")
    access = VillageHealthAccessSnapshot.objects.filter(report=report, verification_status="verified")
    emergency, emergency_rows = sum_or_none(access, "emergency_referrals_count")
    travel, travel_rows = sum_or_none(access, "travel_time_minutes")
    shortage, shortage_rows = sum_or_none(access, "medicine_shortage_days")
    period_days = Decimal((report.reporting_period.end_date - report.reporting_period.start_date).days + 1)
    return {
        "new_cases_per_1000": ratio(new, population, THOUSAND),
        "existing_cases_per_1000": ratio(existing, population, THOUSAND),
        "referral_rate": ratio(referred, cases),
        "recovery_rate": ratio(recovered, cases),
        "mortality_count": count_metric(deaths or ZERO, bool(death_rows or section_confirmed(report, "health"))),
        "emergency_referral_rate": ratio(emergency if emergency_rows else None, cases),
        "average_health_facility_travel_time": average(travel, travel_rows),
        "medicine_shortage_frequency": ratio(shortage, period_days * shortage_rows if shortage_rows else None),
    }


def _disability_results(report):
    rows = DisabilitySnapshot.objects.filter(report=report, verification_status="verified")
    count, count_rows = sum_or_none(rows, "count")
    supported, supported_rows = sum_or_none(rows, "receiving_support_count")
    school_rows = age_band(rows, 5, 18)
    school_count, _ = sum_or_none(school_rows, "count")
    school_attending, _ = sum_or_none(school_rows, "attending_school_count")
    work_rows = age_band(rows, 15, 64)
    work_count, _ = sum_or_none(work_rows, "count")
    employed, _ = sum_or_none(work_rows, "employed_count")
    population, _ = sum_or_none(verified_population(report), "count")
    return {
        "disability_prevalence": ratio(count, population),
        "disability_support_coverage": ratio(supported, count),
        "school_inclusion_rate": ratio(school_attending, school_count),
        "employment_inclusion_rate": ratio(employed, work_count),
        "unmet_support_count": count_metric((count or ZERO) - (supported or ZERO), bool(count_rows and supported_rows)),
    }


def _agriculture_results(report):
    crops = CropProductionSnapshot.objects.filter(report=report, verification_status="verified")
    units = set(crops.exclude(quantity_unit="").values_list("quantity_unit", flat=True))
    currencies = set(crops.exclude(currency_code="").values_list("currency_code", flat=True))
    harvested, harvested_rows = sum_or_none(crops, "quantity_harvested")
    lost, lost_rows = sum_or_none(crops, "quantity_lost")
    sales, sales_rows = sum_or_none(crops, "estimated_sales_value")
    production = count_metric(harvested or ZERO, bool(harvested_rows)) if len(units) <= 1 else no_data("Harvest quantities use incompatible units and were not summed.")
    loss = ratio(lost, harvested) if len(units) <= 1 else no_data("Crop quantities use incompatible units.")
    sale_result = count_metric(sales or ZERO, bool(sales_rows)) if len(currencies) <= 1 else no_data("Agricultural sales use multiple currencies and were not summed.")
    food = FoodSecuritySnapshot.objects.filter(report=report, verification_status="verified").first()
    households = effective_households(report).count()
    return {
        "crop_production_total": production,
        "crop_loss_rate": loss,
        "estimated_agricultural_sales": sale_result,
        "crop_diversity_count": count_metric(crops.values("crop_type_id").distinct().count(), bool(crops.exists() or section_confirmed(report, "agriculture_food"))),
        "food_shortage_household_rate": ratio(food.households_with_food_shortage if food else None, households if households else None),
        "average_food_shortage_days": calculated(food.average_food_shortage_days, food.average_food_shortage_days, 1) if food and food.average_food_shortage_days is not None else no_data(),
    }


def _economy_results(report):
    period = report.reporting_period
    businesses = VillageBusiness.objects.filter(village=report.village).filter(Q(start_date__isnull=True) | Q(start_date__lte=period.end_date))
    active = businesses.filter(is_active=True).exclude(operating_status__iexact="closed")
    active_count = active.count()
    households = effective_households(report).count()
    full_time, full_rows = sum_or_none(active, "full_time_employees")
    part_time, part_rows = sum_or_none(active, "part_time_employees")
    cohort = businesses.filter(Q(start_date__isnull=True) | Q(start_date__lte=period.start_date))
    survived = cohort.filter(Q(closure_date__isnull=True) | Q(closure_date__gt=period.end_date)).count()
    finance = VillageFinancialSnapshot.objects.filter(report=report, verified_from_statement=True)
    opening, opening_rows = sum_or_none(finance, "opening_balance")
    closing, closing_rows = sum_or_none(finance, "closing_balance")
    return {
        "active_businesses_per_100_households": ratio(active_count, households if households else None),
        "licensed_business_rate": ratio(active.filter(licence_status__iregex=r"^(licensed|current|valid)$").count(), active_count),
        "full_time_employment_created": count_metric(full_time or ZERO, bool(full_rows or (active_count and section_confirmed(report, "business_finance")))),
        "part_time_employment_created": count_metric(part_time or ZERO, bool(part_rows or (active_count and section_confirmed(report, "business_finance")))),
        "women_owned_business_rate": ratio(active.filter(owner_gender__iexact="female").count(), active_count),
        "youth_owned_business_rate": ratio(active.filter(owner_age_group__minimum_age__gte=15, owner_age_group__maximum_age__isnull=False, owner_age_group__maximum_age__lte=35).count(), active_count),
        "business_survival_rate": ratio(survived, cohort.count()),
        "village_savings_growth": ratio(closing - opening if opening is not None and closing is not None and opening_rows and closing_rows else None, opening),
    }


def _project_results(report):
    period = report.reporting_period
    projects = IVDPProject.objects.filter(village=report.village, is_active=True)
    count = projects.count()
    completed = projects.filter(project_status__iexact="completed")
    comparable = completed.exclude(planned_end_date__isnull=True).exclude(actual_end_date__isnull=True)
    on_time = comparable.filter(actual_end_date__lte=F("planned_end_date")).count()
    delayed = projects.filter(planned_end_date__lt=period.end_date).exclude(project_status__iexact="completed").count()
    approved, _ = sum_or_none(projects, "approved_budget")
    spent, _ = sum_or_none(projects, "actual_expenditure")
    physical, physical_rows = sum_or_none(projects, "physical_progress_percentage")
    financial, financial_rows = sum_or_none(projects, "financial_progress_percentage")
    milestones = ProjectMilestone.objects.filter(project__in=projects, planned_date__lt=period.end_date).exclude(status__iexact="completed")
    progress = IVDPProjectProgress.objects.filter(report=report).order_by("project_id", "-reporting_date", "-pk")
    latest = {}
    for row in progress:
        latest.setdefault(row.project_id, row.risk_level or "unknown")
    breakdown = {}
    for level in latest.values():
        breakdown[level] = breakdown.get(level, 0) + 1
    return {
        "project_completion_rate": ratio(completed.count(), count),
        "projects_on_time_rate": ratio(on_time, comparable.count()),
        "delayed_project_count": count_metric(delayed, bool(count or section_confirmed(report, "ivdp_projects"))),
        "budget_utilisation_rate": ratio(spent, approved),
        "physical_progress_average": average(physical, physical_rows),
        "financial_progress_average": average(financial, financial_rows),
        "overdue_milestone_count": count_metric(milestones.count(), bool(count or section_confirmed(report, "ivdp_projects"))),
        "projects_by_risk_level": calculated(sum(breakdown.values()), sum(breakdown.values()), None, breakdown=breakdown) if breakdown else no_data(),
    }


def _resilience_results(report):
    preparedness = VillageDisasterPreparedness.objects.filter(village=report.village).first()
    controls = ("disaster_plan_available", "disaster_committee_active", "emergency_contacts_available", "warning_system_available", "emergency_supplies_available", "vulnerable_people_register_available")
    preparedness_result = no_data()
    if preparedness and all(getattr(preparedness, name) is not None for name in controls):
        yes = sum(bool(getattr(preparedness, name)) for name in controls) + bool(preparedness.evacuation_drill_date)
        preparedness_result = ratio(yes, 7)
    centres = EvacuationCentre.objects.filter(village=report.village, is_active=True)
    capacity, capacity_rows = sum_or_none(centres, "capacity")
    population, _ = sum_or_none(verified_population(report), "count")
    climate = ClimateImpactObservation.objects.filter(report=report)
    disasters = DisasterIncident.objects.filter(report=report)
    households, household_rows = sum_or_none(climate, "households_affected")
    people, people_rows = sum_or_none(climate, "population_affected")
    climate_loss, climate_loss_rows = sum_or_none(climate, "estimated_damage_value")
    disaster_loss, disaster_loss_rows = sum_or_none(disasters, "estimated_loss")
    currencies = set(climate.exclude(estimated_damage_value__isnull=True).values_list("currency_code", flat=True)) | set(disasters.exclude(estimated_loss__isnull=True).values_list("currency_code", flat=True))
    loss = (climate_loss or ZERO) + (disaster_loss or ZERO)
    actions = ClimateResponseAction.objects.filter(impact_observation__report=report, due_date__lt=report.reporting_period.end_date).exclude(status__iexact="completed")
    observed = bool(climate.exists() or disasters.exists() or section_confirmed(report, "climate_disaster"))
    return {
        "disaster_preparedness_score": preparedness_result,
        "evacuation_capacity": count_metric(capacity or ZERO, bool(capacity_rows or section_confirmed(report, "climate_disaster"))),
        "evacuation_capacity_ratio": ratio(capacity, population),
        "households_affected_by_disasters": count_metric(households or ZERO, bool(household_rows or section_confirmed(report, "climate_disaster"))),
        "population_affected_by_disasters": count_metric(people or ZERO, bool(people_rows or section_confirmed(report, "climate_disaster"))),
        "climate_incident_count": count_metric(climate.count() + disasters.count(), observed),
        "estimated_disaster_loss": count_metric(loss, bool(climate_loss_rows or disaster_loss_rows)) if len(currencies) <= 1 else no_data("Loss values use multiple currencies and were not summed."),
        "overdue_climate_response_actions": count_metric(actions.count(), observed),
    }


def _culture_results(report):
    titles = TraditionalTitle.objects.filter(traditional_unit__village=report.village)
    title_count = titles.count()
    knowledge = CulturalKnowledgeRecord.objects.filter(village=report.village)
    known_youth = knowledge.exclude(youth_participation__isnull=True)
    under_stages = ("community_discussion", "village_meeting_completed", "documentation_in_progress", "submitted", "under_review")
    return {
        "traditional_title_vacancy_rate": ratio(titles.filter(Q(status__iexact="vacant") | Q(confirmation_stage="vacant")).distinct().count(), title_count),
        "traditional_title_confirmation_rate": ratio(titles.filter(confirmation_stage="confirmed").count(), title_count),
        "titles_under_confirmation_count": count_metric(titles.filter(confirmation_stage__in=under_stages).count(), bool(title_count or section_confirmed(report, "traditional_culture"))),
        "cultural_practices_at_risk": count_metric(knowledge.filter(risk_level__in=("at_risk", "critically_at_risk")).count(), bool(knowledge.exists() or section_confirmed(report, "traditional_culture"))),
        "critically_at_risk_cultural_practices": count_metric(knowledge.filter(risk_level="critically_at_risk").count(), bool(knowledge.exists() or section_confirmed(report, "traditional_culture"))),
        "youth_cultural_participation_rate": ratio(known_youth.filter(youth_participation=True).count(), known_youth.count()),
    }


def calculate_report_results(report, *, health_filters=None):
    results = {
        spec.code: unavailable(spec.unavailable_reason)
        for spec in CATALOGUE
        if not spec.available
    }
    for group in (
        _population_results(report),
        _governance_results(report),
        _water_results(report),
        _sanitation_results(report),
        _energy_results(report),
        _health_results(report, health_filters),
        _disability_results(report),
        _agriculture_results(report),
        _economy_results(report),
        _project_results(report),
        _resilience_results(report),
        _culture_results(report),
    ):
        results.update(group)
    missing_implementation = set(CATALOGUE_BY_CODE) - set(results)
    if missing_implementation:
        raise RuntimeError(f"Indicator calculators are missing: {', '.join(sorted(missing_implementation))}")
    return results


def calculate_health_preview(report, **filters):
    return _health_results(report, filters)
