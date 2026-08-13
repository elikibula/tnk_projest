# Mobile validation and workflow

Phase 9 keeps validation and workflow authoritative in Django. Mobile clients can read unresolved issues and request validation through `/api/v1/reports/{report_uuid}/validation/`; they do not reproduce Django's cross-record quality rules.

Submission is online-only and follows this order: synchronize records and evidence, reject submission while any attachment remains unsynced, refresh the server report, run server validation, display unresolved issues, save an acknowledged final declaration, call `mark_ready`, call `submit`, and cache the returned server status. The UI never displays a submitted result before the response contains `status=submitted`; network or service uncertainty displays **Submission not confirmed.**

Critical unresolved issues block readiness and submission through the existing workflow service. Warning and information issues remain visible but do not incorrectly turn an otherwise complete section into a blocking state. Error severity continues to affect data-quality scoring according to the existing service rules.

Returned reports include reviewer name, return timestamp, comment, affected sections marked as needing attention, and the current server-backed report values. They remain editable only in the existing `returned_to_village` state. Corrections are synchronized before the same authoritative readiness and submission transitions are called.

Endpoints:

- `GET|POST /api/v1/reports/{report_uuid}/validation/`
- `POST /api/v1/reports/{report_uuid}/declaration/`
- `POST /api/v1/reports/{report_uuid}/workflow/{action}/`

All endpoints use the existing role and location selectors. Cross-village resources return 404 and unavailable workflow actions return 403.
