# TNK Insight mobile API v1

Phase 8 adds authorised evidence metadata and multipart upload endpoints:

- `GET /api/v1/reports/{report_uuid}/evidence/`
- `POST /api/v1/reports/{report_uuid}/evidence/` (requires `Idempotency-Key`)

Phase 9 adds authoritative validation and workflow endpoints:

- `GET|POST /api/v1/reports/{report_uuid}/validation/`
- `POST /api/v1/reports/{report_uuid}/declaration/`
- `POST /api/v1/reports/{report_uuid}/workflow/{action}/`

Phase 10 adds `GET /api/v1/dashboard/`, optionally filtered by an authorised `report_uuid`, for the current report summary and server-calculated village indicators.

The mobile API is mounted at `/api/v1/`. Django models and services remain authoritative; the API does not expose unrestricted model viewsets.

## Phase 1 endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/auth/login/` | Authenticate online and register an app installation |
| POST | `/auth/refresh/` | Rotate a device-bound refresh token |
| POST | `/auth/logout/` | Blacklist the supplied refresh token |
| GET | `/me/` | Current user, active roles and location assignments |
| GET | `/locations/villages/` | Assigned villages only |
| GET | `/reporting-periods/` | Open, unlocked periods |
| GET/POST | `/reports/` | Scoped report list and service-backed creation |
| GET | `/reports/{uuid}/` | Scoped report status and section progress |
| GET | `/sync/bootstrap/` | Initial mobile bootstrap envelope |
| GET | `/sync/changes/?cursor=...` | Scoped authoritative delta with opaque next cursor |
| POST | `/sync/batch/` | Bounded partial-success report-entry upload |
| GET | `/schema/` | OpenAPI schema |
| GET | `/docs/` | Swagger UI |

Write endpoints accept public UUIDs but resolve ownership on the server. Cross-location detail returns 404 to avoid object enumeration; cross-location creation returns 403 from the domain service. Errors use stable `code` and safe `detail` fields.

The bootstrap response has `schema_version`, `server_time`, user/scope data, active-device and version-policy data, villages, open periods, accessible reports, server-defined section fields and workflow capabilities. Each entry type includes its original `fields` list plus model-derived `field_definitions` (`name`, `label`, `type`, `required`, `max_length`, and `choices`) and create/delete capabilities. `sync_cursor` is intentionally `null` until the delta protocol is implemented in its planned sync phase.

## Planned API map

Later phases add explicit section-entry commands, validation/workflow actions, indicators, evidence metadata/upload sessions, and `/sync/changes/` plus `/sync/batch/`. Each command will reuse the existing section, validation, workflow, indicator, document and confidentiality services and require an expected `record_version` and idempotency key where applicable.
