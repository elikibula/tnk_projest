# Indicator definitions

## Authoritative catalogue

Phase D defines 91 quarterly indicators in `apps/analytics/catalogue.py`. Each seeded `IndicatorDefinition` contains:

- stable code and version;
- English and iTaukei display fields;
- description, numerator, denominator, and formula;
- measurement unit and frequency;
- geographic level and disaggregation;
- data source and verification requirement;
- missing-value rule and effective date;
- implementation status and, when unavailable, a precise reason.

No approved iTaukei indicator terminology was supplied with the project. `name_fj` therefore uses the English label as an explicit fallback rather than inventing an official translation. The fallback must be replaced through the versioned catalogue after language-owner approval.

## Calculation rules

- Verified rows are used for analytical snapshots that expose `verification_status`.
- Existing documented population movements remain event totals; their verification flag contributes to quality interpretation rather than silently removing recorded events.
- NULL means no data. It is never converted to zero.
- Zero is emitted only when the relevant section is complete/verified or source rows explicitly confirm zero.
- A zero denominator produces `no_data`, not zero or an exception.
- Mixed measurement units and currencies are never summed.
- Population bands are 0-14 (child), 15-64 (working age), and 65+ (elderly). Only age groups wholly inside the required band are included; overlapping groups produce no inferred split.
- Youth calculations use age groups wholly inside ages 15-35. School inclusion uses groups wholly inside ages 5-18.
- Indicator values retain numerator, denominator, optional breakdown, calculation status/notes, source-report count, and data-quality rating.
- Village values are calculated when a report is approved. Tikina and provincial values recombine village numerators and denominators; ratios are not averaged.
- Existing official village values are not silently recalculated from later-changing source records. Approved report corrections will use the Phase E amendment mechanism.
- Dashboards do not rank villages. Every displayed value includes its quality rating.

## Implemented catalogue

| Group | Implemented codes |
|---|---|
| Population | `total_population`, `male_population`, `female_population`, `child_population_percentage`, `working_age_percentage`, `elderly_population_percentage`, `dependency_ratio`, `sex_ratio`, `births_this_period`, `deaths_this_period`, `net_migration`, `population_growth_rate`, `average_household_size` |
| Governance | `active_committee_rate`, `committee_meeting_rate`, `female_committee_representation`, `youth_committee_representation`, `decision_completion_rate`, `overdue_decision_count`, `committees_with_annual_plan_percentage` |
| Water | `average_water_outage_days`, `water_failure_count`, `percentage_water_sources_tested` |
| Sanitation | `toilet_coverage`, `functional_sanitation_rate`, `households_without_toilet`, `shared_toilet_rate`, `safely_managed_sanitation_rate`, `flood_vulnerable_sanitation_rate` |
| Energy | `electrification_rate`, `reliable_energy_coverage`, `solar_household_coverage`, `generator_dependency_rate`, `households_without_electricity`, `average_energy_availability_hours` |
| Health | `new_cases_per_1000`, `existing_cases_per_1000`, `referral_rate`, `recovery_rate`, `mortality_count`, `emergency_referral_rate`, `average_health_facility_travel_time`, `medicine_shortage_frequency` |
| Disability | `disability_prevalence`, `disability_support_coverage`, `school_inclusion_rate`, `employment_inclusion_rate`, `unmet_support_count` |
| Agriculture and food | `crop_production_total`, `crop_loss_rate`, `estimated_agricultural_sales`, `crop_diversity_count`, `food_shortage_household_rate`, `average_food_shortage_days` |
| Economy | `active_businesses_per_100_households`, `licensed_business_rate`, `full_time_employment_created`, `part_time_employment_created`, `women_owned_business_rate`, `youth_owned_business_rate`, `business_survival_rate`, `village_savings_growth` |
| IVDP projects | `project_completion_rate`, `projects_on_time_rate`, `delayed_project_count`, `budget_utilisation_rate`, `physical_progress_average`, `financial_progress_average`, `overdue_milestone_count`, `projects_by_risk_level` |
| Resilience | `disaster_preparedness_score`, `evacuation_capacity`, `evacuation_capacity_ratio`, `households_affected_by_disasters`, `population_affected_by_disasters`, `climate_incident_count`, `estimated_disaster_loss`, `overdue_climate_response_actions` |
| Traditional leadership and culture | `traditional_title_vacancy_rate`, `traditional_title_confirmation_rate`, `titles_under_confirmation_count`, `cultural_practices_at_risk`, `critically_at_risk_cultural_practices`, `youth_cultural_participation_rate` |

The health preview service supports filters for condition, gender, and age group. Geographic and reporting-period filters are applied by report selection and the village/Tikina/province aggregation services.

## Explicitly unavailable indicators

These seven requested definitions are present and versioned but return `unavailable`; no proxy formula is used.

| Code | Reason |
|---|---|
| `committee_attendance_rate` | Meetings store attendance but not the eligible/expected attendee denominator. |
| `reliable_water_coverage` | Source-level household service counts can overlap; there is no household-to-source relationship. |
| `safe_water_coverage` | Source-level household service counts can overlap; there is no household-to-source relationship. |
| `households_without_reliable_water` | Distinct households with reliable water cannot be derived from overlapping source totals. |
| `average_water_repair_time` | Maintenance records have no repair start/end timestamps or duration. |
| `waste_service_coverage` | Facility household counts can overlap; there is no household-to-facility relationship. |
| `beneficiaries_reached` | Projects store expected beneficiaries but not actual beneficiaries reached. |

Future schema changes for these indicators require data-owner approval, migration design, form changes, and known-value tests. Until then, reports and dashboards clearly show them as unavailable.

## Geographic aggregation and quality

Village values are the primary calculation grain. Tikina and provincial values are derived only from official village values for the same period. Counts are summed; rate/average numerators and denominators are summed and the formula is reapplied. `projects_by_risk_level` stores and sums a JSON breakdown.

The aggregate quality rating is the lowest contributing village rating. A missing or unavailable village does not become zero. `source_report_count` shows how many village reports contributed, so incomplete geographic coverage remains visible.

## Operational use

`python manage.py calculate_indicators` seeds/updates the catalogue and calculates official approved, locked, and archived report periods. Approval also calculates the newly approved village and refreshes its Tikina/province aggregate immediately. `IndicatorValue` rows are read-only and non-deletable in Django admin.
