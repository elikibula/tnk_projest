# TNK Insight Mobile

Offline-first Flutter client for TNK Insight. The implemented scope includes
device-bound authentication, encrypted local storage, bootstrap and section
reporting, durable synchronization and conflicts, protected evidence,
authoritative validation/workflow, dashboard indicators, bilingual UI support,
accessibility foundations, and release-oriented security controls.

Version `1.0.1+2` adds a role-aware profile, scoped Province/Tikina/Village
directory, backend-calculated analytics with reporting-period comparison and
drill-down, cascading report location selection, report filters and workflow
history, and one-time access-token refresh for authenticated API calls.

The mobile reporting experience now carries the website's data-type presentation
through to Flutter: red Master/Base, green Operational/Event, purple Snapshot,
and gold Evidence/Workflow/Derived labels and card accents. Senior officers with
the same website roles receive Photo Reports with scoped report filters, area and
progress-stage filters, protected previews, capture time, confidentiality, GPS,
record context and full-screen zoom. Supported synced records can capture staged
photo evidence directly from their mobile card. Location browsing retrieves every
authorised paginated Province, Tikina and Village and links villages to their
report history and analytics. Analytics includes period comparison, official
indicators, hierarchy drill-down, insights, trends and missing-report follow-up.

The mobile client uses these additional read-only endpoints:

- `GET /api/v1/locations/` for the assigned hierarchy
- `GET /api/v1/analytics/` for scoped, server-calculated analytics
- `GET /api/v1/photo-reports/` for authorised village report selection
- `GET /api/v1/photo-reports/<report UUID>/` for the filtered photo gallery
- `GET /api/v1/photo-reports/images/<document UUID>/` for private image bytes

User and location administration remains in the Django web application. The
mobile app does not invent mutation endpoints or notification behavior that the
backend does not provide.

## Entrypoints

- `lib/main_development.dart`
- `lib/main_staging.dart`
- `lib/main_production.dart`

API URLs are centralized and supplied with Dart defines:

```powershell
flutter run --flavor development --target=lib/main_development.dart --dart-define=TNK_APP_ENV=development --dart-define=TNK_DEVELOPMENT_API_URL=http://10.0.2.2:8000/api/v1/
```

The generic `lib/main.dart` entrypoint fails closed unless `TNK_APP_ENV` is explicitly supplied. Staging and production configuration rejects non-HTTPS URLs and URLs outside the versioned `/api/v1/` boundary.

Staging and production default to deliberately invalid HTTPS hosts and reject
reserved `.invalid` or local-development hosts at runtime. A real URL must be
supplied through `TNK_STAGING_API_URL` or `TNK_PRODUCTION_API_URL`; no
production secret is stored in the application.

The previously authenticated offline-session window defaults to 72 hours and can be configured at build time with `--dart-define=TNK_OFFLINE_SESSION_HOURS=72`. First-time login always requires the API. Passwords are never persisted; device-bound tokens and the random installation identifier use platform secure storage.

The local database uses SQLite3 Multiple Ciphers with a random 256-bit key held in platform secure storage. Database records carry an owning user UUID to prevent one signed-in user from reading another user's cached data. Do not place JWTs, passwords, or the database key in Drift.

Android product flavours provide distinct development, staging, and production
application identities. Production signing is intentionally absent from source
control and must be injected by the protected release pipeline. Staging and
production prevent ordinary screenshots/recent-task previews, deny cleartext,
and exclude application state from backup and device transfer. Development
retains local HTTP and screen capture for testing.

The iOS project currently uses the three Dart entrypoints; native Xcode
scheme/configuration separation, signing, backup/file-protection behavior and
physical-device validation must be completed on macOS before release.

## Feature boundaries

The project uses a feature-first layout. New phases add implementation beneath `lib/features/`; shared API, authentication, database, security, sync, errors, localization, and utilities belong beneath `lib/core/`. Large catch-all service or model files should not be introduced.
