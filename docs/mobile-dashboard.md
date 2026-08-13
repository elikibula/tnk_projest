# Mobile dashboard and village summary

Phase 10 adds `GET /api/v1/dashboard/`. The endpoint selects only reports visible through the existing role-and-location selector and returns the current report, location hierarchy, reporting period, unresolved issue count, and a deliberately small catalogue of village-level `IndicatorValue` records. Indicator values are calculated by Django and include approved amendment overrides; Flutter does not reproduce official formulas.

The mobile home screen combines that authoritative response with device-local operational information: pending record and attachment count, last successful synchronization, and connectivity state. The most recent successful response is encrypted in the existing local database and remains available offline.

The dashboard provides large actions for continuing or starting a report, reviewing issues, synchronizing, opening the previous report, viewing all authorised reports, and viewing the lightweight village summary. Report-section cards show the server status, completion, issue count, and last update.

The initial indicator subset covers population, average household size, water testing, sanitation, energy, health, projects and project risk, and committee actions. Missing or unavailable values are displayed as such; the client never substitutes zero.
