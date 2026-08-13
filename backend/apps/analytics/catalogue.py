from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class IndicatorSpec:
    code: str
    name_en: str
    formula: str
    unit: str
    numerator: str
    denominator: str
    source: str
    disaggregation: str = "village, Tikina, province, reporting period"
    missing: str = "Return no data when required source rows or a denominator are missing; never replace missing with zero."
    verification: str = "Use verified analytical rows where a verification field exists."
    available: bool = True
    unavailable_reason: str = ""


def item(code, name, formula, unit, numerator, denominator, source, **kwargs):
    return IndicatorSpec(code, name, formula, unit, numerator, denominator, source, **kwargs)


CATALOGUE_EFFECTIVE_FROM = date(2026, 1, 1)

CATALOGUE = (
    # Population
    item("total_population", "Total population", "Sum verified resident population counts.", "people", "Verified resident count", "Not applicable", "PopulationSnapshot"),
    item("male_population", "Male population", "Sum verified male resident population counts.", "people", "Verified male resident count", "Not applicable", "PopulationSnapshot", disaggregation="gender, age group, village, Tikina, province, reporting period"),
    item("female_population", "Female population", "Sum verified female resident population counts.", "people", "Verified female resident count", "Not applicable", "PopulationSnapshot", disaggregation="gender, age group, village, Tikina, province, reporting period"),
    item("child_population_percentage", "Child population percentage", "Verified residents aged 0-14 / total verified residents × 100.", "percent", "Verified residents in age groups wholly within ages 0-14", "Total verified residents", "PopulationSnapshot, AgeGroup"),
    item("working_age_percentage", "Working-age population percentage", "Verified residents aged 15-64 / total verified residents × 100.", "percent", "Verified residents in age groups wholly within ages 15-64", "Total verified residents", "PopulationSnapshot, AgeGroup"),
    item("elderly_population_percentage", "Elderly population percentage", "Verified residents aged 65+ / total verified residents × 100.", "percent", "Verified residents in age groups starting at age 65", "Total verified residents", "PopulationSnapshot, AgeGroup"),
    item("dependency_ratio", "Dependency ratio", "Children plus elderly / working-age residents × 100.", "dependants per 100 working-age people", "Verified residents aged 0-14 plus 65+", "Verified residents aged 15-64", "PopulationSnapshot, AgeGroup"),
    item("sex_ratio", "Sex ratio", "Verified male residents / verified female residents × 100.", "males per 100 females", "Verified male resident count", "Verified female resident count", "PopulationSnapshot"),
    item("births_this_period", "Births this period", "Sum verified birth movements.", "people", "Verified birth movement count", "Not applicable", "PopulationMovement"),
    item("deaths_this_period", "Deaths this period", "Sum verified death movements.", "people", "Verified death movement count", "Not applicable", "PopulationMovement"),
    item("net_migration", "Net migration", "Moved in plus returned minus moved out and temporarily left.", "people", "Verified incoming movement count minus verified outgoing movement count", "Not applicable", "PopulationMovement"),
    item("population_growth_rate", "Population growth rate", "Current verified population minus previous official-period population, divided by previous population × 100.", "percent", "Current verified population minus previous official-period population", "Previous official-period verified population", "PopulationSnapshot, TNKReport"),
    item("average_household_size", "Average household size", "Verified population / effective household count.", "people per household", "Total verified resident population", "Households effective during the reporting period", "PopulationSnapshot, Household"),
    # Governance
    item("active_committee_rate", "Active committee rate", "Committees active at period end / committees effective during period × 100.", "percent", "Committees active at period end", "Committees effective during period", "VillageCommittee"),
    item("committee_meeting_rate", "Committee meeting rate", "Active committees holding at least one meeting / active committees × 100.", "percent", "Active committees with a report-period meeting", "Active committees", "VillageCommittee, CommitteeMeeting"),
    item("female_committee_representation", "Female committee representation", "Active female members / active committee members × 100.", "percent", "Active members recorded as female", "Active committee members", "CommitteeMember"),
    item("youth_committee_representation", "Youth committee representation", "Active members aged 15-35 / active committee members × 100.", "percent", "Active members in age groups wholly within ages 15-35", "Active committee members", "CommitteeMember, AgeGroup"),
    item("committee_attendance_rate", "Committee attendance rate", "Meeting attendees / eligible expected attendees × 100.", "percent", "Meeting attendance", "Eligible expected attendees", "CommitteeMeeting", available=False, unavailable_reason="Meetings store attendance but not the eligible or expected attendee denominator."),
    item("decision_completion_rate", "Decision completion rate", "Completed meeting decisions / all meeting decisions × 100.", "percent", "Decisions completed by period end", "Decisions from report-period meetings", "MeetingDecision, CommitteeMeeting"),
    item("overdue_decision_count", "Overdue decision count", "Count incomplete decisions due before period end.", "decisions", "Incomplete decisions whose due date precedes period end", "Not applicable", "MeetingDecision, CommitteeMeeting"),
    item("committees_with_annual_plan_percentage", "Committees with annual plan", "Active committees with an annual plan / active committees × 100.", "percent", "Active committees with annual_plan_available=True", "Active committees", "VillageCommittee"),
    # Water
    item("reliable_water_coverage", "Reliable water coverage", "Households with reliable water / households × 100.", "percent", "Distinct households with reliable water", "Effective households", "VillageWaterSource, Household", available=False, unavailable_reason="Water-source service counts can overlap and there is no household-to-source relationship."),
    item("safe_water_coverage", "Safe water coverage", "Households with safe water / households × 100.", "percent", "Distinct households served by a safe source", "Effective households", "VillageWaterSource, Household", available=False, unavailable_reason="Water-source service counts can overlap and there is no household-to-source relationship."),
    item("households_without_reliable_water", "Households without reliable water", "Households minus distinct households with reliable water.", "households", "Effective households without a reliable source", "Not applicable", "VillageWaterSource, Household", available=False, unavailable_reason="Distinct covered households cannot be derived from overlapping water-source service counts."),
    item("average_water_outage_days", "Average water outage days", "Total recorded interruption hours / 24 / interruptions with duration.", "days", "Total interruption duration in days", "Interruptions with recorded duration", "WaterInterruption"),
    item("water_failure_count", "Water failure count", "Count report-period water interruptions.", "interruptions", "Water interruption count", "Not applicable", "WaterInterruption"),
    item("average_water_repair_time", "Average water repair time", "Total repair duration / completed repairs.", "hours", "Repair duration", "Completed repairs", "WaterMaintenanceActivity", available=False, unavailable_reason="Water maintenance records do not store repair start/end times or duration."),
    item("percentage_water_sources_tested", "Water sources tested", "Active sources tested in period / active sources × 100.", "percent", "Distinct active water sources tested during period", "Active water sources", "VillageWaterSource, WaterQualityTest"),
    # Sanitation
    item("toilet_coverage", "Toilet coverage", "Households represented by sanitation facilities / households × 100.", "percent", "Functional plus non-functional sanitation count", "Effective households", "SanitationSnapshot, Household"),
    item("functional_sanitation_rate", "Functional sanitation rate", "Functional sanitation count / total sanitation count × 100.", "percent", "Functional sanitation count", "Functional plus non-functional sanitation count", "SanitationSnapshot"),
    item("households_without_toilet", "Households without toilet", "Households minus sanitation count, floored at zero.", "households", "Effective households not represented by sanitation counts", "Not applicable", "SanitationSnapshot, Household"),
    item("shared_toilet_rate", "Shared toilet rate", "Shared sanitation count / total sanitation count × 100.", "percent", "Shared sanitation count", "Functional plus non-functional sanitation count", "SanitationSnapshot"),
    item("safely_managed_sanitation_rate", "Safely managed sanitation rate", "Safely managed count / total sanitation count × 100.", "percent", "Safely managed sanitation count", "Functional plus non-functional sanitation count", "SanitationSnapshot"),
    item("flood_vulnerable_sanitation_rate", "Flood-vulnerable sanitation rate", "Flood-vulnerable count / total sanitation count × 100.", "percent", "Flood-vulnerable sanitation count", "Functional plus non-functional sanitation count", "SanitationSnapshot"),
    item("waste_service_coverage", "Waste service coverage", "Distinct households served by waste service / households × 100.", "percent", "Distinct households receiving waste service", "Effective households", "WasteFacility, Household", available=False, unavailable_reason="Facility household counts can overlap and no household-to-facility relationship exists."),
    # Energy
    item("electrification_rate", "Electrification rate", "Households connected to a primary electricity source / households × 100.", "percent", "Connected households on primary electricity records", "Effective households", "EnergySnapshot, Household"),
    item("reliable_energy_coverage", "Reliable energy coverage", "Households with working primary supply / connected households × 100.", "percent", "Households with working primary supply", "Households connected to primary supply", "EnergySnapshot"),
    item("solar_household_coverage", "Solar household coverage", "Households connected to primary solar supply / households × 100.", "percent", "Households connected to primary solar records", "Effective households", "EnergySnapshot, Household"),
    item("generator_dependency_rate", "Generator dependency rate", "Households connected to primary generator supply / connected primary households × 100.", "percent", "Households connected to primary generator records", "Households connected to primary electricity records", "EnergySnapshot"),
    item("households_without_electricity", "Households without electricity", "Households minus primary connected households, floored at zero.", "households", "Effective households without a primary electricity connection", "Not applicable", "EnergySnapshot, Household"),
    item("average_energy_availability_hours", "Average energy availability", "Connected-household weighted average daily availability.", "hours per day", "Sum availability hours × connected households", "Connected households with availability data", "EnergySnapshot"),
    # Health
    item("new_cases_per_1000", "New cases per 1,000", "Verified new cases / verified population × 1,000.", "cases per 1,000 people", "Verified new health cases", "Verified resident population", "HealthConditionSnapshot, PopulationSnapshot", disaggregation="health condition, gender, age group, village, Tikina, province, reporting period"),
    item("existing_cases_per_1000", "Existing cases per 1,000", "Verified existing cases / verified population × 1,000.", "cases per 1,000 people", "Verified existing health cases", "Verified resident population", "HealthConditionSnapshot, PopulationSnapshot", disaggregation="health condition, gender, age group, village, Tikina, province, reporting period"),
    item("referral_rate", "Referral rate", "Referred cases / new plus existing cases × 100.", "percent", "Verified referred cases", "Verified new plus existing cases", "HealthConditionSnapshot", disaggregation="health condition, gender, age group, village, Tikina, province, reporting period"),
    item("recovery_rate", "Recovery rate", "Recovered cases / new plus existing cases × 100.", "percent", "Verified recovered cases", "Verified new plus existing cases", "HealthConditionSnapshot", disaggregation="health condition, gender, age group, village, Tikina, province, reporting period"),
    item("mortality_count", "Mortality count", "Sum verified health-condition deaths.", "deaths", "Verified deaths", "Not applicable", "HealthConditionSnapshot", disaggregation="health condition, gender, age group, village, Tikina, province, reporting period"),
    item("emergency_referral_rate", "Emergency referral rate", "Emergency referrals / new plus existing cases × 100.", "percent", "Emergency referrals in health-access snapshot", "Verified new plus existing cases", "VillageHealthAccessSnapshot, HealthConditionSnapshot"),
    item("average_health_facility_travel_time", "Average health-facility travel time", "Average reported travel time to nearest health facility.", "minutes", "Sum reported travel minutes", "Health-access records with travel time", "VillageHealthAccessSnapshot"),
    item("medicine_shortage_frequency", "Medicine shortage frequency", "Medicine shortage days / reporting-period days × 100.", "percent of period days", "Reported medicine-shortage days", "Days in reporting period", "VillageHealthAccessSnapshot"),
    # Disability
    item("disability_prevalence", "Disability prevalence", "Verified disability count / verified population × 100.", "percent", "Verified disability count", "Verified resident population", "DisabilitySnapshot, PopulationSnapshot", disaggregation="disability type, gender, age group, village, Tikina, province, reporting period"),
    item("disability_support_coverage", "Disability support coverage", "Receiving support / disability count × 100.", "percent", "Verified people receiving support", "Verified disability count", "DisabilitySnapshot"),
    item("school_inclusion_rate", "School inclusion rate", "School-attending school-age people with disability / school-age disability count × 100.", "percent", "Verified attending-school count for age groups wholly within ages 5-18", "Verified disability count for those age groups", "DisabilitySnapshot, AgeGroup"),
    item("employment_inclusion_rate", "Employment inclusion rate", "Employed working-age people with disability / working-age disability count × 100.", "percent", "Verified employed count for age groups wholly within ages 15-64", "Verified disability count for those age groups", "DisabilitySnapshot, AgeGroup"),
    item("unmet_support_count", "Unmet disability support count", "Disability count minus receiving-support count.", "people", "Verified disability count without recorded support", "Not applicable", "DisabilitySnapshot"),
    # Agriculture and food
    item("crop_production_total", "Crop production total", "Sum verified harvested quantity when all rows use one unit.", "reported quantity unit", "Verified harvested quantity", "Not applicable", "CropProductionSnapshot, CropType"),
    item("crop_loss_rate", "Crop loss rate", "Quantity lost / harvested quantity × 100 when units are compatible.", "percent", "Verified quantity lost", "Verified harvested quantity", "CropProductionSnapshot"),
    item("estimated_agricultural_sales", "Estimated agricultural sales", "Sum verified estimated sales when all rows use one currency.", "reported currency", "Verified estimated sales value", "Not applicable", "CropProductionSnapshot"),
    item("crop_diversity_count", "Crop diversity count", "Distinct crop types with verified report rows.", "crop types", "Distinct verified crop types", "Not applicable", "CropProductionSnapshot, CropType"),
    item("food_shortage_household_rate", "Food-shortage household rate", "Households reporting shortage / households × 100.", "percent", "Reported households with food shortage", "Effective households", "FoodSecuritySnapshot, Household"),
    item("average_food_shortage_days", "Average food-shortage days", "Reported average food-shortage days.", "days", "Reported average food-shortage days", "Not applicable", "FoodSecuritySnapshot"),
    # Economy
    item("active_businesses_per_100_households", "Active businesses per 100 households", "Active businesses / households × 100.", "businesses per 100 households", "Active businesses at period end", "Effective households", "VillageBusiness, Household"),
    item("licensed_business_rate", "Licensed business rate", "Active businesses with current/licensed/valid status / active businesses × 100.", "percent", "Active licensed businesses", "Active businesses", "VillageBusiness"),
    item("full_time_employment_created", "Full-time employment", "Sum full-time employees in active businesses.", "jobs", "Full-time employees in active businesses", "Not applicable", "VillageBusiness"),
    item("part_time_employment_created", "Part-time employment", "Sum part-time employees in active businesses.", "jobs", "Part-time employees in active businesses", "Not applicable", "VillageBusiness"),
    item("women_owned_business_rate", "Women-owned business rate", "Active women-owned businesses / active businesses × 100.", "percent", "Active businesses with owner gender female", "Active businesses", "VillageBusiness"),
    item("youth_owned_business_rate", "Youth-owned business rate", "Active youth-owned businesses / active businesses × 100.", "percent", "Active businesses whose owner age group is wholly within ages 15-35", "Active businesses", "VillageBusiness, AgeGroup"),
    item("business_survival_rate", "Business survival rate", "Businesses existing at period start and still open at period end / businesses existing at period start × 100.", "percent", "Pre-period businesses not closed before period end", "Businesses started on or before period start", "VillageBusiness"),
    item("village_savings_growth", "Village savings growth", "Verified closing balances minus opening balances / opening balances × 100.", "percent", "Verified closing balance minus verified opening balance", "Verified opening balance", "VillageFinancialSnapshot"),
    # IVDP projects
    item("project_completion_rate", "Project completion rate", "Completed active projects / active projects × 100.", "percent", "Active projects recorded completed", "Active projects", "IVDPProject"),
    item("projects_on_time_rate", "Projects on-time rate", "Completed projects finishing by planned end / completed projects with planned and actual end dates × 100.", "percent", "Completed projects on or before planned end", "Completed projects with comparable dates", "IVDPProject"),
    item("delayed_project_count", "Delayed project count", "Incomplete active projects whose planned end precedes period end.", "projects", "Delayed active projects", "Not applicable", "IVDPProject"),
    item("budget_utilisation_rate", "Budget utilisation rate", "Actual expenditure / approved budget × 100.", "percent", "Actual project expenditure", "Approved project budget", "IVDPProject"),
    item("physical_progress_average", "Average physical progress", "Average physical progress of active projects.", "percent", "Sum physical progress", "Active projects", "IVDPProject"),
    item("financial_progress_average", "Average financial progress", "Average financial progress of active projects.", "percent", "Sum financial progress", "Active projects", "IVDPProject"),
    item("overdue_milestone_count", "Overdue milestone count", "Incomplete milestones planned before period end.", "milestones", "Overdue incomplete milestones", "Not applicable", "ProjectMilestone, IVDPProject"),
    item("projects_by_risk_level", "Projects by risk level", "Count latest report-period project progress records by risk level.", "projects", "Projects grouped by latest risk level", "Not applicable", "IVDPProjectProgress", disaggregation="risk level, village, Tikina, province, reporting period"),
    item("beneficiaries_reached", "Beneficiaries reached", "Sum actual beneficiaries reached.", "people", "Actual beneficiaries reached", "Not applicable", "IVDPProject", available=False, unavailable_reason="The project model stores expected beneficiaries only; no actual reached field exists."),
    # Resilience
    item("disaster_preparedness_score", "Disaster preparedness score", "Available preparedness controls / seven controls × 100; no value until all controls are answered.", "percent", "True preparedness controls", "Seven required preparedness controls", "VillageDisasterPreparedness"),
    item("evacuation_capacity", "Evacuation capacity", "Sum capacity of active evacuation centres.", "people", "Active evacuation-centre capacity", "Not applicable", "EvacuationCentre"),
    item("evacuation_capacity_ratio", "Evacuation capacity ratio", "Evacuation capacity / verified population × 100.", "percent", "Active evacuation-centre capacity", "Verified resident population", "EvacuationCentre, PopulationSnapshot"),
    item("households_affected_by_disasters", "Households affected by disasters", "Sum households affected in climate observations.", "households", "Reported affected households", "Not applicable", "ClimateImpactObservation"),
    item("population_affected_by_disasters", "Population affected by disasters", "Sum population affected in climate observations.", "people", "Reported affected population", "Not applicable", "ClimateImpactObservation"),
    item("climate_incident_count", "Climate incident count", "Count climate-impact observations plus disaster incidents.", "incidents", "Climate observations and disaster incidents", "Not applicable", "ClimateImpactObservation, DisasterIncident"),
    item("estimated_disaster_loss", "Estimated disaster loss", "Sum climate damage and disaster loss when all values use one currency.", "reported currency", "Reported estimated damage and loss", "Not applicable", "ClimateImpactObservation, DisasterIncident"),
    item("overdue_climate_response_actions", "Overdue climate-response actions", "Incomplete response actions due before period end.", "actions", "Overdue incomplete response actions", "Not applicable", "ClimateResponseAction"),
    # Traditional leadership and culture
    item("traditional_title_vacancy_rate", "Traditional title vacancy rate", "Vacant titles / all titles × 100.", "percent", "Titles recorded vacant", "Traditional titles", "TraditionalTitle"),
    item("traditional_title_confirmation_rate", "Traditional title confirmation rate", "Confirmed titles / all titles × 100.", "percent", "Titles at confirmed stage", "Traditional titles", "TraditionalTitle"),
    item("titles_under_confirmation_count", "Titles under confirmation", "Count titles in a non-vacant, non-confirmed confirmation stage.", "titles", "Titles under an intermediate confirmation stage", "Not applicable", "TraditionalTitle"),
    item("cultural_practices_at_risk", "Cultural practices at risk", "Count cultural knowledge records marked at risk or critically at risk.", "practices", "At-risk cultural knowledge records", "Not applicable", "CulturalKnowledgeRecord"),
    item("critically_at_risk_cultural_practices", "Critically at-risk cultural practices", "Count cultural knowledge records marked critically at risk.", "practices", "Critically at-risk cultural knowledge records", "Not applicable", "CulturalKnowledgeRecord"),
    item("youth_cultural_participation_rate", "Youth cultural participation rate", "Records reporting youth participation / cultural knowledge records × 100.", "percent", "Cultural knowledge records with youth_participation=True", "Cultural knowledge records with a known participation response", "CulturalKnowledgeRecord"),
)

CATALOGUE_BY_CODE = {spec.code: spec for spec in CATALOGUE}
