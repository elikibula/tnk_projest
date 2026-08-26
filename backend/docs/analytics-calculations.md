# TNK Insight decision analytics calculations

Decision analytics are read-only and permission-scoped. Official indicator values use reports with `approved`, `locked`, or `archived` status. Reporting compliance is intentionally broader: a report is received once it is submitted, in review, approved, locked, or archived.

## Reporting completion

- Source: `locations.Village`, `reporting.TNKReport`.
- Expected: active villages within the user's authorised geographic scope.
- Received: distinct expected villages with a report in a received workflow state for the selected period.
- Formula: received / expected × 100, with a protected zero-village denominator.
- Missing is distinct from a valid reported value of zero.

## Population and households

- Population source: calculated `total_population` indicator values from verified `PopulationSnapshot` rows.
- Household source: the authoritative denominator of `average_household_size`, representing households effective during the period.
- Aggregation: sum village-grain values only. Province and Tikina aggregate records are not mixed with village records, preventing double counting.

## Projects, health, water, disability, and climate

- Projects: denominator of `project_completion_rate` (all projects represented in the official report calculation).
- Health cases: numerator of `new_cases_per_1000`; only aggregate counts are shown.
- Water issues: `water_failure_count`.
- Disability: numerator of `disability_prevalence`; no person-level fields are exposed.
- Climate: `climate_incident_count`.

Each metric returns **No Data** when no calculated village indicator exists. A calculated value of zero remains zero.

## Percentage change

`percentage_change(previous, current)` returns no comparison when either value is missing or the previous value is zero and current is non-zero. It returns zero when both values are zero. This avoids misleading or infinite changes.

## Security

All location querysets originate from `villages_for_user()`. System Administrators and superusers receive national scope. Provincial and other existing authorised analytics roles remain confined to their assigned location scope. CSV summary exports reuse the same scoped aggregation and create a `DataExportAudit` record.
