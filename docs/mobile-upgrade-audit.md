# Mobile/backend audit (26 August 2026)

## Existing architecture retained

Flutter 3.44.3 / Dart 3.12.2 are recorded in the existing package configuration.
The app is feature-first with Riverpod 3, Dio 5, GoRouter, secure platform token
storage, device-bound JWT, Drift/SQLite3 Multiple Ciphers, encrypted evidence,
durable offline drafts and conflict-aware sync. English and iTaukei ARB files
already exist. Keep these; the cache is a client replica, never a second authority.

Django exposes `/api/v1/` device login/refresh/logout, `me/`, `dashboard/`,
`locations/villages/`, `reporting-periods/`, `reports/`, report detail/evidence/
validation/declaration/workflow, and `sync/bootstrap/changes/batch/`. The schema
is `/api/v1/schema/`. Workflow actions and form definitions originate in Django.
There is no notification API and no safe mobile user-management write API.
Complex administration stays on the existing website.

## Gaps found before changes

- No reactive 401 refresh/retry; preflight expiry checks alone miss server rejection.
- Profile parser discards location assignments. No backend capability map.
- Closed periods omitted from bootstrap despite historical reports referring to them.
- Report cards show UUIDs rather than period/location labels, and editability is inferred in Dart.
- Bootstrap errors leave the authenticated landing page spinning indefinitely.
- Dashboard recreates network futures on rebuild and permits cached fallback on authorization errors.
- No scoped analytics drilldown/period comparison API or mobile screen.
- No searchable hierarchy/read-only reference screen; report creation uses a flat village list.
- Submission lacks a separate deliberate confirmation dialog; report detail lacks workflow history.
- Existing encrypted local draft and section-entry architecture works and should remain.
- Android release signing is explicitly fail-closed. No signing environment variables are configured.
- Recorded Flutter SDK path under `tmp/flutter-sdk/flutter` is missing. SDK restore is required to verify Flutter/build work.

## Compatibility and safety

Keep existing endpoint paths and default list response shapes. Add fields and new
read-only scoped endpoints. New pagination is opt-in on legacy lists. Use UUIDs
and backend capabilities, preserve server enforcement, never widen location scopes.
No real report or location data needs to change for this upgrade. Release credentials
must be supplied by the owner; never substitute debug signing for production.
