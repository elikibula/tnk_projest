from datetime import date, datetime, timezone
from decimal import Decimal

from django.test import TestCase

from apps.accounts.models import Role, User, UserLocationAssignment, UserRoleAssignment
from apps.analytics.catalogue import CATALOGUE
from apps.analytics.models import IndicatorDefinition, IndicatorValue
from apps.analytics.services import aggregate_indicators, calculate_village_indicators, preview_health_indicators, seed_indicator_definitions
from apps.culture.models import CulturalKnowledgeRecord, TraditionalTitle, TraditionalUnit
from apps.economy.models import CropProductionSnapshot, CropType, FoodSecuritySnapshot, VillageBusiness, VillageFinancialAccount, VillageFinancialSnapshot
from apps.governance.models import CommitteeMeeting, CommitteeMember, MeetingDecision, PersonReference, VillageCommittee
from apps.infrastructure.models import EnergySnapshot, SanitationSnapshot, VillageWaterSource, WaterInterruption, WaterQualityTest
from apps.locations.models import Province, Tikina, Village
from apps.population.models import AgeGroup, Household, PopulationMovement, PopulationSnapshot
from apps.projects.models import IVDPProject, IVDPProjectProgress, ProjectMilestone
from apps.reporting.models import ReportSectionStatus, ReportingPeriod, TNKReport
from apps.reporting.services import create_report
from apps.resilience.models import ClimateImpactObservation, ClimateResponseAction, DisasterIncident, EvacuationCentre, VillageDisasterPreparedness
from apps.wellbeing.models import DisabilitySnapshot, HealthCondition, HealthConditionSnapshot, VillageHealthAccessSnapshot


class IndicatorCatalogueTests(TestCase):
    def setUp(self):
        self.province = Province.objects.create(code="IND", name_en="Indicator Province")
        self.tikina = Tikina.objects.create(province=self.province, code="IT", name_en="Indicator Tikina")
        self.village = Village.objects.create(tikina=self.tikina, code="IV1", name_en="Indicator Village One")
        self.other_village = Village.objects.create(tikina=self.tikina, code="IV2", name_en="Indicator Village Two")
        self.q1 = ReportingPeriod.objects.create(year=2026, quarter=1, start_date=date(2026, 1, 1), end_date=date(2026, 3, 31), submission_due_date=date(2026, 12, 31), is_open=True)
        self.q2 = ReportingPeriod.objects.create(year=2026, quarter=2, start_date=date(2026, 4, 1), end_date=date(2026, 6, 30), submission_due_date=date(2026, 12, 31), is_open=True)
        self.user = User.objects.create_user(username="indicator-author")
        role = Role.objects.create(code=Role.Codes.TURAGA_NI_KORO, name="Turaga ni Koro")
        UserRoleAssignment.objects.create(user=self.user, role=role)
        UserLocationAssignment.objects.create(user=self.user, province=self.province)
        self.report = create_report(village=self.village, reporting_period=self.q2, prepared_by=self.user)
        self.child = AgeGroup.objects.create(code="IND-CH", name_en="Children", minimum_age=0, maximum_age=14, sort_order=1)
        self.school = AgeGroup.objects.create(code="IND-SCH", name_en="School age", minimum_age=5, maximum_age=14, sort_order=1)
        self.working = AgeGroup.objects.create(code="IND-WA", name_en="Working age", minimum_age=15, maximum_age=64, sort_order=2)
        self.youth = AgeGroup.objects.create(code="IND-Y", name_en="Youth", minimum_age=15, maximum_age=35, sort_order=2)
        self.elderly = AgeGroup.objects.create(code="IND-EL", name_en="Elderly", minimum_age=65, sort_order=3)

    def analytical(self, measurement_date=date(2026, 5, 1)):
        return {
            "measurement_date": measurement_date,
            "data_source": "village_register",
            "collection_method": "register",
            "verification_status": "verified",
        }

    def values(self, report=None):
        return {value.indicator.code: value for value in calculate_village_indicators(report or self.report)}

    def assert_value(self, values, code, expected):
        self.assertEqual(values[code].calculation_status, "calculated", code)
        self.assertEqual(values[code].value, Decimal(str(expected)).quantize(Decimal("0.0001")), code)

    def seed_population_and_households(self):
        PopulationSnapshot.objects.create(report=self.report, village=self.village, age_group=self.child, gender="male", resident_status="permanent_resident", count=20, **self.analytical())
        PopulationSnapshot.objects.create(report=self.report, village=self.village, age_group=self.working, gender="female", resident_status="permanent_resident", count=50, **self.analytical())
        PopulationSnapshot.objects.create(report=self.report, village=self.village, age_group=self.elderly, gender="male", resident_status="permanent_resident", count=10, **self.analytical())
        for number in range(4):
            Household.objects.create(household_code=f"IND-H{number}", village=self.village, household_head_name=f"Head {number}", household_size=20, effective_from=date(2026, 1, 1), verification_status="verified")

    def test_catalogue_has_all_91_versioned_definitions_and_explicit_gaps(self):
        definitions = seed_indicator_definitions()
        self.assertEqual(len(CATALOGUE), 91)
        self.assertEqual(len(definitions), 91)
        self.assertEqual(len({definition.code for definition in definitions}), 91)
        for definition in definitions:
            with self.subTest(code=definition.code):
                self.assertTrue(definition.name_en)
                self.assertEqual(definition.name_fj, "")
                self.assertTrue(definition.formula_description)
                self.assertTrue(definition.numerator_definition)
                self.assertTrue(definition.denominator_definition)
                self.assertTrue(definition.data_source)
                self.assertTrue(definition.disaggregation)
                self.assertTrue(definition.missing_value_rule)
                self.assertTrue(definition.verification_requirement)
                self.assertEqual(definition.version, 1)
        unavailable = IndicatorDefinition.objects.filter(implementation_status="unavailable")
        self.assertEqual(unavailable.count(), 7)
        self.assertFalse(unavailable.filter(unavailable_reason="").exists())

    def test_reseeding_preserves_an_approved_itaukei_indicator_name(self):
        definition = seed_indicator_definitions()[0]
        definition.name_fj = "Yaca vakadonui"
        definition.save(update_fields=("name_fj",))

        seed_indicator_definitions()

        definition.refresh_from_db()
        self.assertEqual(definition.name_fj, "Yaca vakadonui")

    def test_population_known_values_previous_period_and_zero_denominator(self):
        previous = create_report(village=self.village, reporting_period=self.q1, prepared_by=self.user)
        PopulationSnapshot.objects.create(report=previous, village=self.village, age_group=self.working, gender="female", resident_status="permanent_resident", count=40, **{**self.analytical(date(2026, 2, 1))})
        TNKReport.objects.filter(pk=previous.pk).update(status=TNKReport.Status.APPROVED)
        self.report.previous_report = previous
        self.report.save(update_fields=("previous_report", "updated_at"))
        self.seed_population_and_households()
        for movement_type, count in (("birth", 2), ("death", 1), ("moved_in", 3), ("moved_out", 1)):
            PopulationMovement.objects.create(village=self.village, reporting_period=self.q2, movement_type=movement_type, movement_date=date(2026, 5, 2), count=count, data_source="village_register")
        values = self.values()
        expected = {
            "total_population": 80,
            "male_population": 30,
            "female_population": 50,
            "child_population_percentage": 25,
            "working_age_percentage": 62.5,
            "elderly_population_percentage": 12.5,
            "dependency_ratio": 60,
            "sex_ratio": 60,
            "births_this_period": 2,
            "deaths_this_period": 1,
            "net_migration": 2,
            "population_growth_rate": 100,
            "average_household_size": 20,
        }
        for code, number in expected.items():
            with self.subTest(code=code):
                self.assert_value(values, code, number)

        PopulationSnapshot.objects.filter(report=self.report, gender="female").update(count=0)
        values = self.values()
        self.assertEqual(values["sex_ratio"].calculation_status, "no_data")
        self.assertIsNone(values["sex_ratio"].value)

    def test_known_values_across_all_indicator_groups(self):
        self.seed_population_and_households()

        person = PersonReference.objects.create(full_name="Committee Member", home_village=self.village)
        committee = VillageCommittee.objects.create(village=self.village, committee_type="development", name="Development", formed_date=date(2025, 1, 1), annual_plan_available=True)
        CommitteeMember.objects.create(committee=committee, person=person, position="Member", gender="female", age_group=self.working, joined_date=date(2025, 1, 1))
        meeting = CommitteeMeeting.objects.create(committee=committee, report=self.report, meeting_date=date(2026, 5, 1), total_attendance=1)
        MeetingDecision.objects.create(meeting=meeting, decision="Complete action", status="completed", completion_percentage=100, completion_date=date(2026, 5, 2))

        source1 = VillageWaterSource.objects.create(village=self.village, source_type="spring", source_name="Spring", operational_status="working", availability_status="reliable", water_quality_status="safe", condition="good", primary_or_backup="primary")
        VillageWaterSource.objects.create(village=self.village, source_type="tank", source_name="Tank", operational_status="working", availability_status="reliable", water_quality_status="safe", condition="good", primary_or_backup="backup")
        WaterInterruption.objects.create(water_source=source1, report=self.report, start_date=datetime(2026, 5, 1, tzinfo=timezone.utc), restored_date=datetime(2026, 5, 3, tzinfo=timezone.utc), cause="Failure", duration_hours=48, resolution_status="resolved")
        WaterQualityTest.objects.create(water_source=source1, test_date=date(2026, 5, 5), tested_by="Lab", test_type="basic", result="safe", safe_for_drinking=True)

        SanitationSnapshot.objects.create(report=self.report, toilet_type="flush", functional_count=3, non_functional_count=1, shared_count=1, safely_managed_count=2, flood_vulnerable_count=1, **self.analytical())
        EnergySnapshot.objects.create(report=self.report, energy_source="solar", households_connected=3, households_with_working_supply=2, average_hours_available_per_day=20, primary_or_backup="primary", **self.analytical())

        condition = HealthCondition.objects.create(code="IND-HC", name_en="Condition", category="general")
        HealthConditionSnapshot.objects.create(report=self.report, health_condition=condition, age_group=self.working, gender="female", new_cases=8, existing_cases=12, referred_cases=5, recovered_cases=10, deaths=1, **self.analytical())
        VillageHealthAccessSnapshot.objects.create(report=self.report, emergency_referrals_count=2, travel_time_minutes=30, medicine_shortage_days=5, **self.analytical())
        DisabilitySnapshot.objects.create(report=self.report, disability_type_id=self._disability_type().pk, age_group=self.school, gender="all", count=2, receiving_support_count=1, attending_school_count=1, employed_count=0, **self.analytical())
        DisabilitySnapshot.objects.create(report=self.report, disability_type_id=self._disability_type().pk, age_group=self.working, gender="all", count=6, receiving_support_count=5, attending_school_count=0, employed_count=3, **self.analytical())

        crop = CropType.objects.create(code="IND-CROP", crop_group="root", name_en="Dalo", default_measurement_unit="kg")
        CropProductionSnapshot.objects.create(report=self.report, crop_type=crop, quantity_harvested=100, quantity_unit="kg", quantity_lost=10, estimated_sales_value=500, currency_code="FJD", **self.analytical())
        FoodSecuritySnapshot.objects.create(report=self.report, households_with_food_shortage=2, average_food_shortage_days=3, **self.analytical())

        VillageBusiness.objects.create(village=self.village, business_name="Women shop", business_sector="retail", owner_type="individual", owner_gender="female", owner_age_group=self.youth, start_date=date(2025, 1, 1), licence_status="licensed", operating_status="active", full_time_employees=2, part_time_employees=1)
        VillageBusiness.objects.create(village=self.village, business_name="Other shop", business_sector="retail", owner_type="individual", owner_gender="male", start_date=date(2025, 1, 1), licence_status="pending", operating_status="active", full_time_employees=1, part_time_employees=2)
        VillageBusiness.objects.create(village=self.village, business_name="Closed shop", business_sector="retail", owner_type="individual", start_date=date(2025, 1, 1), closure_date=date(2026, 5, 1), operating_status="closed", is_active=False)
        account = VillageFinancialAccount.objects.create(village=self.village, account_type="savings", institution="Bank", account_purpose="Village", currency_code="FJD")
        VillageFinancialSnapshot.objects.create(account=account, report=self.report, opening_balance=100, deposits=20, withdrawals=0, closing_balance=120, verified_from_statement=True)

        project1 = IVDPProject.objects.create(project_code="IND-P1", village=self.village, project_name="Complete", project_category="water", problem_being_addressed="Access", priority="high", planned_end_date=date(2026, 5, 30), actual_end_date=date(2026, 5, 20), approved_budget=100, actual_expenditure=100, project_status="completed", physical_progress_percentage=100, financial_progress_percentage=100)
        project2 = IVDPProject.objects.create(project_code="IND-P2", village=self.village, project_name="Delayed", project_category="road", problem_being_addressed="Access", priority="high", planned_end_date=date(2026, 4, 30), approved_budget=200, actual_expenditure=50, project_status="active", physical_progress_percentage=50, financial_progress_percentage=40)
        ProjectMilestone.objects.create(project=project2, title="Late milestone", planned_date=date(2026, 4, 1), percentage_weight=50, status="open")
        IVDPProjectProgress.objects.create(project=project1, report=self.report, reporting_date=date(2026, 5, 20), work_completed="Done", progress_percentage=100, risk_level="low")
        IVDPProjectProgress.objects.create(project=project2, report=self.report, reporting_date=date(2026, 5, 20), work_completed="Half", progress_percentage=50, risk_level="high")

        VillageDisasterPreparedness.objects.create(village=self.village, disaster_plan_available=True, disaster_committee_active=True, emergency_contacts_available=True, evacuation_drill_date=date(2026, 5, 1), warning_system_available=True, emergency_supplies_available=True, vulnerable_people_register_available=True)
        EvacuationCentre.objects.create(village=self.village, name="Hall", capacity=40, accessibility_status="accessible", condition="good")
        climate = ClimateImpactObservation.objects.create(village=self.village, report=self.report, hazard_type="flood", observation_date=date(2026, 5, 1), severity="high", households_affected=2, population_affected=10, estimated_damage_value=100, currency_code="FJD", description="Flood")
        ClimateResponseAction.objects.create(impact_observation=climate, action="Repair", responsible_party="Village", due_date=date(2026, 5, 1), status="open")
        DisasterIncident.objects.create(village=self.village, report=self.report, incident_type="storm", incident_date=date(2026, 5, 2), estimated_loss=50, currency_code="FJD")

        unit = TraditionalUnit.objects.create(village=self.village, unit_type="yavusa", name="Yavusa")
        TraditionalTitle.objects.create(traditional_unit=unit, title_type="chief", title_name="Vacant", status="vacant", confirmation_stage="vacant")
        TraditionalTitle.objects.create(traditional_unit=unit, title_type="chief", title_name="Confirmed", status="filled", confirmation_stage="confirmed", confirmation_date=date(2026, 1, 1))
        CulturalKnowledgeRecord.objects.create(village=self.village, knowledge_category="dance", knowledge_name="Practice A", description="A", transmission_status="active", youth_participation=True, risk_level="at_risk")
        CulturalKnowledgeRecord.objects.create(village=self.village, knowledge_category="song", knowledge_name="Practice B", description="B", transmission_status="active", youth_participation=False, risk_level="critically_at_risk")

        values = self.values()
        expected = {
            "active_committee_rate": 100, "committee_meeting_rate": 100, "female_committee_representation": 100,
            "youth_committee_representation": 0,
            "decision_completion_rate": 100, "overdue_decision_count": 0, "committees_with_annual_plan_percentage": 100,
            "average_water_outage_days": 2, "water_failure_count": 1, "percentage_water_sources_tested": 50,
            "toilet_coverage": 100, "functional_sanitation_rate": 75, "households_without_toilet": 0,
            "shared_toilet_rate": 25, "safely_managed_sanitation_rate": 50, "flood_vulnerable_sanitation_rate": 25,
            "electrification_rate": 75, "solar_household_coverage": 75, "households_without_electricity": 1,
            "reliable_energy_coverage": Decimal("66.6667"), "generator_dependency_rate": 0,
            "average_energy_availability_hours": 20, "new_cases_per_1000": 100, "existing_cases_per_1000": 150,
            "referral_rate": 25, "recovery_rate": 50, "mortality_count": 1, "emergency_referral_rate": 10,
            "average_health_facility_travel_time": 30, "medicine_shortage_frequency": Decimal("5.4945"),
            "disability_prevalence": 10, "disability_support_coverage": 75,
            "school_inclusion_rate": 50, "employment_inclusion_rate": 50, "unmet_support_count": 2,
            "crop_production_total": 100, "crop_loss_rate": 10, "estimated_agricultural_sales": 500,
            "crop_diversity_count": 1, "food_shortage_household_rate": 50, "average_food_shortage_days": 3,
            "active_businesses_per_100_households": 50, "licensed_business_rate": 50,
            "full_time_employment_created": 3, "part_time_employment_created": 3, "women_owned_business_rate": 50,
            "youth_owned_business_rate": 50, "business_survival_rate": Decimal("66.6667"),
            "village_savings_growth": 20, "project_completion_rate": 50,
            "projects_on_time_rate": 100, "delayed_project_count": 1, "budget_utilisation_rate": 50,
            "physical_progress_average": 75, "financial_progress_average": 70, "overdue_milestone_count": 1,
            "projects_by_risk_level": 2,
            "disaster_preparedness_score": 100, "evacuation_capacity": 40, "evacuation_capacity_ratio": 50,
            "households_affected_by_disasters": 2, "population_affected_by_disasters": 10,
            "climate_incident_count": 2, "estimated_disaster_loss": 150, "overdue_climate_response_actions": 1,
            "traditional_title_vacancy_rate": 50, "traditional_title_confirmation_rate": 50,
            "titles_under_confirmation_count": 0, "cultural_practices_at_risk": 2,
            "critically_at_risk_cultural_practices": 1, "youth_cultural_participation_rate": 50,
        }
        for code, number in expected.items():
            self.assert_value(values, code, number)
        self.assertEqual(values["projects_by_risk_level"].breakdown, {"low": 1, "high": 1})
        self.assertEqual(values["beneficiaries_reached"].calculation_status, "unavailable")

    def _disability_type(self):
        from apps.wellbeing.models import DisabilityType

        value, _ = DisabilityType.objects.get_or_create(code="IND-D", defaults={"name_en": "Disability", "category": "general"})
        return value

    def test_confirmed_zero_mixed_units_health_filters_and_geographic_aggregation(self):
        self.report.section_statuses.filter(section_code="population_households").update(status=ReportSectionStatus.Status.COMPLETE)
        values = self.values()
        self.assert_value(values, "births_this_period", 0)
        self.assertEqual(values["total_population"].calculation_status, "no_data")

        PopulationSnapshot.objects.create(report=self.report, village=self.village, age_group=self.working, gender="female", resident_status="permanent_resident", count=50, **self.analytical())
        condition1 = HealthCondition.objects.create(code="IND-F1", name_en="One", category="general")
        condition2 = HealthCondition.objects.create(code="IND-F2", name_en="Two", category="general")
        HealthConditionSnapshot.objects.create(report=self.report, health_condition=condition1, age_group=self.working, gender="female", new_cases=5, **self.analytical())
        HealthConditionSnapshot.objects.create(report=self.report, health_condition=condition2, age_group=self.working, gender="female", new_cases=10, **self.analytical())
        preview = preview_health_indicators(self.report, health_condition=condition1, gender="female", age_group=self.working)
        self.assertEqual(preview["new_cases_per_1000"].value, Decimal("100"))

        crop1 = CropType.objects.create(code="IND-M1", crop_group="root", name_en="One", default_measurement_unit="kg")
        crop2 = CropType.objects.create(code="IND-M2", crop_group="root", name_en="Two", default_measurement_unit="tonne")
        CropProductionSnapshot.objects.create(report=self.report, crop_type=crop1, quantity_harvested=1, quantity_unit="kg", **self.analytical())
        CropProductionSnapshot.objects.create(report=self.report, crop_type=crop2, quantity_harvested=1, quantity_unit="tonne", **self.analytical())
        values = self.values()
        self.assertEqual(values["crop_production_total"].calculation_status, "no_data")

        other_report = create_report(village=self.other_village, reporting_period=self.q2, prepared_by=self.user)
        PopulationSnapshot.objects.create(report=other_report, village=self.other_village, age_group=self.working, gender="male", resident_status="permanent_resident", count=20, **self.analytical())
        self.report.data_quality_score = Decimal("90")
        self.report.save(update_fields=("data_quality_score", "updated_at"))
        other_report.data_quality_score = Decimal("65")
        other_report.save(update_fields=("data_quality_score", "updated_at"))
        calculate_village_indicators(self.report)
        calculate_village_indicators(other_report)
        tikina_values = {value.indicator.code: value for value in aggregate_indicators(self.q2, self.tikina)}
        province_values = {value.indicator.code: value for value in aggregate_indicators(self.q2, self.province)}
        self.assert_value(tikina_values, "total_population", 70)
        self.assert_value(province_values, "total_population", 70)
        self.assertEqual(tikina_values["total_population"].source_report_count, 2)
        self.assertEqual(tikina_values["total_population"].data_quality_rating, "medium")
        self.assertEqual(
            IndicatorValue.objects.filter(indicator__code="total_population", reporting_period=self.q2).count(),
            4,
        )

    def test_official_indicator_values_are_not_silently_recalculated(self):
        self.seed_population_and_households()
        self.assert_value(self.values(), "total_population", 80)
        TNKReport.objects.filter(pk=self.report.pk).update(status=TNKReport.Status.APPROVED)
        self.report.refresh_from_db()
        PopulationSnapshot.objects.filter(report=self.report).update(count=999)
        self.assert_value(self.values(), "total_population", 80)
