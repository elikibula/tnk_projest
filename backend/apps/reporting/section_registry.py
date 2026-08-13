from dataclasses import dataclass
from django.db import models

from apps.culture.models import CulturalKnowledgeRecord, TraditionalTitle, TraditionalUnit
from apps.economy.models import CropProductionSnapshot, FoodSecuritySnapshot, VillageBusiness, VillageFinancialAccount, VillageFinancialSnapshot
from apps.governance.models import CommitteeMeeting, MeetingDecision, OfficialAppointment, PersonReference, TrainingActivity, VillageCommittee, VillageVisit
from apps.infrastructure.models import EnergySnapshot, HousingSnapshot, SanitationSnapshot, VillageAsset, VillageEnergyAsset, VillageWaterSource, WasteCollectionActivity, WasteFacility, WaterInterruption, WaterMaintenanceActivity, WaterQualityTest
from apps.locations.models import Village
from apps.population.models import Household, PopulationMovement, PopulationSnapshot
from apps.projects.models import IVDPProject, IVDPProjectProgress, ProjectMilestone, ProjectRisk
from apps.resilience.models import ClimateImpactObservation, DisasterIncident, EvacuationCentre, VillageDisasterPreparedness
from apps.wellbeing.models import CommunitySafetyIncident, DisabilitySnapshot, HealthConditionSnapshot, VillageHealthAccessSnapshot


@dataclass(frozen=True)
class EntryConfig:
    key: str
    label: str
    model: type[models.Model]
    fields: tuple[str, ...]
    allow_create: bool = True
    allow_delete: bool = True

    @property
    def display_label(self):
        from .itaukei import localize_text
        return localize_text(self.label)


def entry(key, label, model, fields, **kwargs):
    return EntryConfig(key, label, model, tuple(fields.split()), **kwargs)


SECTION_ENTRIES = {
    "village_profile": [entry("village", "Village profile", Village, "name_en name_fj island_name latitude longitude postal_address contact_phone contact_email", allow_create=False, allow_delete=False)],
    "leadership_governance": [
        entry("person", "Personal Information", PersonReference, "full_name gender date_of_birth phone email confidentiality_level is_active"),
        entry("appointment", "Official appointment", OfficialAppointment, "person role appointment_date effective_from effective_to confirmation_status appointment_reference is_current change_reason"),
        entry("committee", "Village committee", VillageCommittee, "committee_type name formed_date dissolved_date mandate chairperson secretary constitution_available annual_plan_available bank_account_available is_active"),
        entry("meeting", "Committee meeting", CommitteeMeeting, "committee meeting_date chaired_by total_attendance male_attendance female_attendance youth_attendance disability_attendance quorum_achieved minutes_available"),
        entry("decision", "Meeting decision", MeetingDecision, "meeting decision responsible_person priority due_date completion_date status completion_percentage reason_delayed"),
    ],
    "visits_training": [
        entry("visit", "Village visit", VillageVisit, "visit_type officer_name organisation visit_date purpose findings recommendations follow_up_required follow_up_due_date follow_up_status"),
        entry("training", "Training activity", TrainingActivity, "category title provider start_date end_date delivery_method target_group male_participants female_participants youth_participants participants_with_disability total_completed cost currency_code funding_source expected_outcome actual_outcome follow_up_required follow_up_date"),
    ],
    "population_households": [
        entry("population", "Population snapshot", PopulationSnapshot, "age_group gender resident_status count measurement_date measurement_unit data_source collection_method source_reference verification_status confidence_level notes"),
        entry("movement", "Population movement", PopulationMovement, "movement_type movement_date gender age_group count origin_or_destination reason data_source verified"),
        entry("household", "Household", Household, "household_code household_head_name household_size male_count female_count child_count elderly_count disability_count primary_livelihood housing_type water_source toilet_type energy_source vulnerability_status latitude longitude effective_from effective_to is_active verification_status"),
    ],
    "housing_assets": [
        entry("housing", "Housing snapshot", HousingSnapshot, "structure_type construction_material condition occupancy_status count measurement_date measurement_unit data_source collection_method source_reference verification_status confidence_level notes"),
        entry("asset", "Village asset", VillageAsset, "asset_code asset_type asset_name quantity acquisition_date acquisition_cost currency_code estimated_current_value funding_source custodian location_description latitude longitude condition operational_status last_maintenance_date next_maintenance_date is_active"),
    ],
    "water": [
        entry("source", "Water source", VillageWaterSource, "source_type source_name latitude longitude ownership operational_status capacity_litres households_served people_served availability_status average_days_unavailable_per_month water_quality_status last_water_test_date last_maintenance_date condition primary_or_backup is_active"),
        entry("interruption", "Water interruption", WaterInterruption, "water_source start_date restored_date cause households_affected people_affected duration_hours responsible_agency action_taken resolution_status"),
        entry("quality", "Water quality test", WaterQualityTest, "water_source test_date tested_by test_type result safe_for_drinking corrective_action"),
        entry("maintenance", "Water maintenance", WaterMaintenanceActivity, "water_source activity_date activity_type problem action_taken responsible_organisation cost completion_status"),
    ],
    "sanitation_waste": [
        entry("sanitation", "Sanitation snapshot", SanitationSnapshot, "toilet_type functional_count non_functional_count shared_count private_count safely_managed_count flood_vulnerable_count measurement_date measurement_unit data_source collection_method source_reference verification_status confidence_level notes"),
        entry("facility", "Waste facility", WasteFacility, "facility_type latitude longitude operational_status collection_frequency households_served responsible_group environmental_risk last_inspection_date is_active"),
        entry("collection", "Waste collection", WasteCollectionActivity, "facility collection_date waste_type estimated_volume measurement_unit collected_by disposal_method"),
    ],
    "energy": [
        entry("energy_snapshot", "Energy snapshot", EnergySnapshot, "energy_source households_connected households_with_working_supply average_hours_available_per_day average_days_unavailable_per_month primary_or_backup estimated_monthly_cost currency_code measurement_date measurement_unit data_source collection_method source_reference verification_status confidence_level notes"),
        entry("energy_asset", "Energy asset", VillageEnergyAsset, "asset_type capacity capacity_unit installation_date households_served ownership condition operational_status fuel_or_energy_type maintenance_provider is_active"),
    ],
    "health": [
        entry("condition", "Health condition snapshot", HealthConditionSnapshot, "health_condition age_group gender new_cases existing_cases referred_cases hospitalised_cases recovered_cases deaths measurement_date measurement_unit data_source collection_method source_reference verification_status confidence_level notes"),
        entry("access", "Health access snapshot", VillageHealthAccessSnapshot, "village_nurse_available nurse_visits_count health_team_visits_count nearest_health_facility travel_time_minutes transport_available medicine_shortage_days emergency_referrals_count measurement_date measurement_unit data_source collection_method source_reference verification_status confidence_level notes"),
        entry("safety", "Community safety incident", CommunitySafetyIncident, "offence_type incident_date number_of_incidents severity victim_age_group victim_gender reported_to_authority authority_reported_to report_date action_taken case_status reason_not_reported measurement_date measurement_unit data_source collection_method source_reference verification_status confidence_level notes"),
    ],
    "disability": [entry("disability", "Disability snapshot", DisabilitySnapshot, "disability_type age_group gender count receiving_support_count attending_school_count employed_count support_required measurement_date measurement_unit data_source collection_method source_reference verification_status confidence_level notes")],
    "agriculture_food": [
        entry("crop", "Crop production", CropProductionSnapshot, "crop_type number_of_farmers number_of_gardens area_planted area_unit quantity_harvested quantity_unit quantity_consumed quantity_sold estimated_sales_value currency_code quantity_lost loss_reason planting_season measurement_date measurement_unit data_source collection_method source_reference verification_status confidence_level notes"),
        entry("food", "Food security", FoodSecuritySnapshot, "households_with_food_shortage average_food_shortage_days main_cause external_assistance_received assistance_provider measurement_date measurement_unit data_source collection_method source_reference verification_status confidence_level notes"),
    ],
    "business_finance": [
        entry("business", "Village business", VillageBusiness, "business_name business_sector owner_type owner_person owner_name owner_gender owner_age_group start_date closure_date licence_status licence_expiry_date operating_status full_time_employees part_time_employees male_employees female_employees youth_employees revenue_band primary_market support_required is_active"),
        entry("account", "Village financial account", VillageFinancialAccount, "account_type institution account_purpose opening_date authorised_signatories_count currency_code is_active"),
        entry("finance", "Financial snapshot", VillageFinancialSnapshot, "account opening_balance deposits withdrawals interest_or_return closing_balance verified_from_statement"),
    ],
    "ivdp_projects": [
        entry("project", "IVDP project", IVDPProject, "project_code project_name project_category problem_being_addressed baseline_value target_value measurement_unit priority responsible_person responsible_organisation planned_start_date planned_end_date actual_start_date actual_end_date estimated_budget approved_budget actual_expenditure currency_code funding_source project_status physical_progress_percentage financial_progress_percentage expected_beneficiaries male_beneficiaries female_beneficiaries youth_beneficiaries is_active"),
        entry("milestone", "Project milestone", ProjectMilestone, "project title planned_date completed_date percentage_weight status"),
        entry("progress", "Project progress", IVDPProjectProgress, "project reporting_date work_completed milestone progress_percentage expenditure_to_date materials_received challenges corrective_action next_activity next_activity_due_date risk_level"),
        entry("risk", "Project risk", ProjectRisk, "project risk_type description likelihood impact mitigation owner status"),
    ],
    "climate_disaster": [
        entry("climate", "Climate impact", ClimateImpactObservation, "hazard_type observation_date latitude longitude severity frequency households_affected population_affected farmland_affected infrastructure_affected estimated_damage_value currency_code description"),
        entry("preparedness", "Disaster preparedness", VillageDisasterPreparedness, "disaster_plan_available plan_last_updated disaster_committee_active emergency_contacts_available evacuation_drill_date warning_system_available emergency_supplies_available vulnerable_people_register_available last_reviewed"),
        entry("centre", "Evacuation centre", EvacuationCentre, "name latitude longitude building_material capacity separate_male_female_restrooms accessibility_status water_available sanitation_available condition is_active"),
        entry("incident", "Disaster incident", DisasterIncident, "incident_type incident_date warning_received people_evacuated injuries deaths houses_damaged houses_destroyed estimated_loss currency_code response_time_minutes assistance_received assistance_provider"),
    ],
    "traditional_culture": [
        entry("unit", "Traditional unit", TraditionalUnit, "unit_type name is_active"),
        entry("title", "Traditional title", TraditionalTitle, "traditional_unit title_type title_name status vacancy_start_date confirmation_stage confirmation_date next_action responsible_party"),
        entry("knowledge", "Cultural knowledge", CulturalKnowledgeRecord, "knowledge_category knowledge_name description number_of_knowledge_holders youngest_knowledge_holder_age transmission_status preservation_activity activity_frequency youth_participation documentation_available risk_level"),
    ],
}


def get_entry_config(section_code, entry_key):
    return next((config for config in SECTION_ENTRIES.get(section_code, ()) if config.key == entry_key), None)
