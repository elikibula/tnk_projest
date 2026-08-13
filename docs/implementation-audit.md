# TNK Insight implementation audit

Audit date: 7 August 2026
Scope: the repository in `tnk_project`, including Django code, tests, migrations, templates, static assets, requirements, Docker configuration, backup scripts, and project documentation.

## Post-audit remediation status

**Phase A — Finalise report workflow: PASS (7 August 2026).** The workflow finding below records the original audit state and is superseded by the authoritative matrix in `docs/report-workflow.md`. `ready_for_validation`, return-to-draft, rejection, submitted-return, and archival transitions are implemented centrally with state, role, location, quality, declaration, comment, acknowledgement, and separation-of-duties checks. Ordinary model saves and Django admin cannot change status. The legacy period archive command now uses the same accountable workflow service. Phase A verification: 74 tests passed, 0 failed, 0 skipped; 93% statement coverage; Django check, migration drift/plan, and Ruff checks passed; no migration was required.

**Phase B — Protect historical master data: PASS (7 August 2026).** The original historical-preservation findings below are superseded by `docs/historical-master-data.md`. Effective-dated appointments, memberships, committees, and households now use transactional close-and-replace services; infrastructure replacements retain inactive predecessors; business, project, and traditional-title lifecycle changes are audited. Report-specific master snapshots are captured at `ready_for_validation`, recaptured only after a legitimate reopen, and used for all non-editable historical report displays. Frozen snapshot creation, save, bulk update, and deletion are rejected through the normal ORM. Existing historical master records are read-only, non-deletable, and excluded from bulk deletion in Django admin. One additive reporting migration was created. Phase B verification: 81 tests passed, 0 failed, 0 skipped; 87% statement coverage across all application modules; focused historical/workflow tests, Django system check, migration drift/plan, clean test-database migration, and Ruff checks passed. The only pytest warning was an inability to create its optional local cache directory and did not affect execution.

**Phase C — Strengthen confidentiality and access control: PASS (7 August 2026).** The original confidentiality findings below are superseded by `docs/confidentiality-access-control.md`. A central deny-by-default policy combines active role, explicit section access, confidentiality clearance, location scope, linked-object scope, and report status. Village Nurses are limited to village profile/health/disability and cannot see community-safety rows; Project Officers are limited to village profile/IVDP projects; Analysts remain aggregate-only. Evidence downloads enforce document level, linked object, location, section role, and pre-/post-submission status. Analytics and every export entry point reapply role and location policy, and highly restricted raw export is denied. Sensitive admin models are limited to trusted roles, with health/disability/safety querysets location-scoped and generic evidence admin central-only pending Phase G. Phase C verification: 88 tests passed, 0 failed, 0 skipped; 87% statement coverage across all application modules; Django system check, migration drift/plan, Ruff checks, and focused role/location/UUID/export tests passed. No schema migration was required. Deployment check warnings reflect the intentionally active local-development settings and are deferred to the production configuration rehearsal in Phase H.

**Phase D — Approved analytics indicator catalogue: PASS WITH NOTES (7 August 2026).** The original three-indicator finding below is superseded by `docs/indicator-definitions.md`. The database now contains 91 versioned definitions with formula, numerator, denominator, unit, frequency, geography, source, disaggregation, missing-value, verification, effective-date, and implementation metadata. Eighty-four indicators are executable across population, governance, water, sanitation, energy, health, disability, agriculture/food, economy, IVDP projects, resilience, and culture. Seven definitions are explicitly unavailable because the current schema lacks a non-overlapping coverage denominator, repair duration, eligible attendance count, or actual beneficiaries reached; no proxy values were invented. Calculations preserve NULL versus confirmed zero, reject zero denominators, reject mixed units/currencies, support health disaggregation, store reproducibility metadata, calculate at approval, and aggregate village numerators/denominators to Tikina/province without ranking low-quality data. Existing official values are not silently recalculated. One additive analytics migration was applied and 91 definitions were seeded locally; there were no existing official local reports to calculate. Phase D verification: 93 tests passed, 0 failed, 0 skipped; 88% statement coverage across all application modules and 99% calculator coverage; Django system check, migration drift/plan, clean test-database migration, and Ruff checks passed. The iTaukei name field currently uses an explicit English fallback pending approved terminology.

**Phase E - Approved-report amendment: PASS (7 August 2026).** Approved, locked, and archived reports now use immutable amendment/change overlays with server-resolved original values, requester/reviewer separation, location/role controls, audit events, supersession lineage, authoritative presentation, and numerator/denominator-aware indicator reaggregation. Original reports and indicator rows remain unchanged. Phase E verification: 102 tests passed and 90% application statement coverage; focused security/immutability/browser/analytics tests, Django checks, migration drift, Ruff, and the applied reporting migration passed. See `docs/report-amendments.md`.

**Phase F - PDF and export quality: PASS (7 August 2026).** The hand-written single-page Helvetica PDF was replaced with ReportLab Platypus, runtime Unicode TrueType fonts, wrapped/repeating tables, A4 pagination, page counts, report metadata, approval/amendment history, authorised project summaries, and authorised evidence references. Analysts retain summary-only output. Excel now uses openpyxl with typed numeric/date/money cells, styles, filters, frozen headings, and explicit filter metadata; CSV uses a UTF-8 BOM. Both spreadsheet formats neutralise formula injection and omit sensitive fields. The renderer has clean background-worker boundaries without introducing an unjustified queue. Phase F verification: 107 tests passed, 0 failed, 0 skipped; 90% application statement coverage and 98% coverage of the export module; Django system check, migration drift, Ruff, focused export/security/typing tests, and legacy export compatibility tests passed. A representative three-page A4 PDF was rendered with Poppler and visually inspected with no clipping, overlap, wrapping, glyph, table, or footer defects. See `docs/export-quality.md`.

**Phase G - Django admin, audit accountability, and reference vocabulary: PASS (7 August 2026).** Django admin now denies ordinary staff regardless of global model permissions, gives System Administrators national access, gives Provincial Administrators location-scoped access without privileged account/role escalation, and gives Auditors location-scoped read-only audit access. Operational querysets, object URLs, and related selectors use the same scope. Sensitive list/search fields are excluded; high-risk workflow records are read-only. Admin assignment writes record the actor, before/after state, IP address, user agent, and derivable location without duplicating the fallback signal event. Audit events are append-only through normal ORM operations and now carry protected Province/Tikina/Village grain. Pre-existing events are preserved unscoped. The vocabulary review found insufficient representative production data for safe automatic remapping, so Phase G records a governed additive migration plan and makes no speculative official-data changes. Phase G verification: 115 tests passed, 0 failed, 0 skipped; 88% application statement coverage; focused admin/audit tests, Django system check, migration drift, applied migration, and Ruff checks passed. The only warning was pytest's inability to write its optional cache directory. See `docs/admin-audit-controls.md` and `docs/reference-vocabulary-migration-plan.md`.

**Phase H - Production/staging readiness: PASS WITH NOTES (8 August 2026).** Production no longer depends on the Tailwind browser CDN: a pinned, checksum-verified compiler builds local utility CSS in development and Docker. CSP and Permissions Policy headers, database-aware health checks, request correlation IDs, allow-listed JSON logging, privacy-scrubbed optional Sentry configuration, static cache headers, safer database/media backup and restore scripts, and a guarded PostgreSQL staging-rehearsal command are implemented. A real isolated PostgreSQL 18 rehearsal applied all migrations from zero, seeded fictional/reference data, completed submission/review/approval, calculated 273 indicator values, generated three audited export formats, exercised protected evidence download, collected static files, passed deployment checks, restored database and media into empty targets, and passed verification after a real PostgreSQL restart. Phase H verification: 119 tests passed, 0 failed, 0 skipped; 87% application statement coverage; Django check, production deployment check, migration drift, dependency consistency, Ruff, local asset build, PostgreSQL migration/workflow/backup/restore, and restart persistence passed. Docker Compose YAML parsed, but Docker/Nginx runtime execution was not possible because those executables are not installed. Production go-live remains conditional on the same Docker/TLS/volume rehearsal in the actual staging host. The only pytest warning was inability to write its optional cache directory. See `docs/deployment.md` and `docs/staging-restore-rehearsal.md`.

**Phase I - Final acceptance and readiness audit: CONDITIONAL (8 August 2026).** A realistic fictional fixture now covers the complete multi-role and multi-location lifecycle: previous quarter, representative master and section data, evidence, all 17 sections, validation, return/correction/resubmission, approval, lock, indicator calculation, dashboard, XLSX/PDF, audit, confidentiality, and cross-location isolation. The final suite passes 120 tests at 88% application statement coverage. Django checks, production deployment checks against PostgreSQL 18, migration drift/plan, Ruff, and dependency consistency pass. A fresh PostgreSQL migration and guarded end-to-end rehearsal exited successfully with 273 indicator values, three audited exports, and verified evidence. Overall go-live remains conditional because Docker/Nginx/TLS/volume execution is unavailable locally and legal/privacy/records-management/operational approvals are external prerequisites. See `docs/final-readiness-audit.md`.

## 1. Executive summary

TNK Insight is a coherent Django 5.2 application with a custom user model, location-scoped reporting, 17 report sections, 42 configured data-entry workflows, historical quarterly snapshots, validation, accountable approval and amendment actions, protected evidence, an approved indicator catalogue, dashboards, and audited exports. After Phases A-I, the local suite contains 120 passing tests and reaches 88% application statement coverage. Django system and production deployment checks, migration drift and plan, clean PostgreSQL migrations, dependency consistency, and Ruff checks pass.

The application is ready for controlled staging and user acceptance testing, but production go-live is **CONDITIONAL**. Remaining release gates are the actual Docker/Nginx/TLS/container-volume rehearsal, production backup/security operations, and accountable legal/privacy/records-management approval. The detailed current verdict in `docs/final-readiness-audit.md` supersedes the original findings below.

No production data was changed or deleted during this audit. Phase I adds an automated acceptance test and readiness documentation; it requires no schema migration.

## 2. Initial findings and disposition

| Severity | Initial finding | Disposition |
|---|---|---|
| HIGH | Archived official reports were excluded from previous-quarter comparison and could be deleted. | Fixed and tested. |
| HIGH | Each validation run deleted unresolved data-quality issues, destroying issue history. | Fixed with stable reuse and automatic resolution; tested. |
| HIGH | A read-only analyst with a location assignment could open detailed reports containing person and household rows. | Fixed: analysts retain aggregate analytics but detailed reports and evidence return 403; tested. |
| HIGH | Any scoped user, including an auditor, could invoke the mutating validation endpoint. | Fixed: only assigned authors may validate editable reports; tested. |
| HIGH | Evidence validation trusted filename extension and client MIME type. | Fixed with signature/container inspection for PDF, JPEG, PNG, DOCX, and XLSX; tested. |
| HIGH | Many subgroup totals and Decimal fields accepted internally impossible values through forms. | Targeted model validation added for the highest-risk household, governance, infrastructure, health, disability, economy, project, safety, and cultural rules; tested samples. |
| HIGH | Docker did not collect/share static files and did not persist protected media. | Fixed configuration; Docker execution could not be tested because Docker is unavailable on the audit host. |
| MEDIUM | Malformed dashboard/export filters could cause numeric conversion errors. | Fixed by a shared allow-listing filter function; tested. |
| MEDIUM | Excel exported numeric values as shared strings. | Fixed; years, quarters, percentages, scores, project budgets, and dates are typed cells with readable formatting; tested. |
| MEDIUM | Concurrent duplicate report creation could expose a raw database integrity error. | Fixed with a savepoint and human-readable validation error; the database unique constraint remains authoritative. |
| MEDIUM | Role/location assignment changes were not audited. | Fixed. Request-aware admin changes capture actor, before/after state, IP, user agent, and location; direct ORM writes retain an actor-null fallback event. |
| MEDIUM | Direct report-linked records remained editable/deletable through default Django admin after approval. | Fixed for normal admin use through central role, location, related-choice, object, and official-history protections. Direct SQL remains outside application controls. |
| LOW | The translation switch test expected an older user-edited iTaukei phrase. | Test updated to the compiled catalogue's current phrase; language switching passes. |

## 3. Current-system map

| Layer | Current implementation |
|---|---|
| Runtime | Python 3.13.3; Django 5.2 |
| Applications | 17 custom apps: accounts, analytics, audit, core, culture, data_quality, documents, economy, governance, infrastructure, locations, population, projects, reporting, resilience, wellbeing, workflow |
| Data model | 74 non-Django models; 62 have UUID public identifiers; 129 `PROTECT`, 12 `CASCADE`, and 1 `SET_NULL` relationships; 24 models link directly to a TNK report |
| Authentication | Custom `accounts.User`; Django sessions; throttled login; login/logout/failure audit signals |
| Authorisation | Role assignments plus province/Tikina/village assignments; server-side scoped selectors; service-level author/reviewer checks |
| Reporting | `ReportingPeriod`, unique village-period `TNKReport`, 17 `ReportSectionStatus` rows, 42 registered entry forms, automatic completion calculation |
| Workflow | Draft/submitted/Tikina review/provincial review/returned/approved/locked transitions; immutable `ApprovalAction`; declaration and acknowledgement controls |
| Data quality | Seven executable rules; weighted completeness/consistency/verification/timeliness/evidence score |
| Analytics | Aggregate scoped dashboard; total population, average household size, and net migration indicators |
| Evidence | UUID document, SHA-256 checksum, protected storage path, extension/size/content checks, location/role checked download |
| Exports | Scoped and audited CSV, XLSX, and summary PDF exports; formula-injection neutralisation |
| Deployment | PostgreSQL production settings, Gunicorn, Nginx, Docker Compose, persistent database/media/static volumes, CI workflow |

URLs are split between the Django admin, authentication, reporting, documents, analytics, and core dashboard. Forms use explicit registry field lists; report, village, period, creator, and updater ownership values are bound server-side.

## 4. Review status by major area

| Area | Status | Evidence and notes |
|---|---|---|
| Django foundation | PASS | Django 5.2 checks pass; custom user is configured from the initial accounts migration; secrets/hosts/CSRF origins are environment-based; secure production cookies, HTTPS redirect, HSTS, static/media roots, Fiji timezone, and locale paths are configured. Development-only fallback secret is not used by production deployment checks. |
| Migrations | PASS WITH NOTES | No model drift or pending migration; all migrations apply from zero on the temporary SQLite test database. A local clean PostgreSQL migration was not possible because no PostgreSQL service/client is available; CI is configured with PostgreSQL. |
| Database relationships | PASS WITH NOTES | `PROTECT` is used for most historical/official relationships and uniqueness is present at key grains. Some `CASCADE` children (quality issues, evidence links, meeting response details) are intentional dependent records. Several cross-field rules are application-level rather than DB checks, so `QuerySet.update()` can bypass them. |
| Reporting periods | PASS | Quarter 1-4 validators and DB check, configurable 2000-2100 year validation, chronological constraints, due-date constraint, uniqueness, and locked/open period checks are implemented and tested. |
| TNK report uniqueness | PASS | Database unique constraint on village + reporting period; duplicate service creation is tested and concurrency integrity errors are humanised. Phase E corrections use a separate immutable amendment overlay without weakening this grain. |
| Data classification | PASS WITH NOTES | Reference, master, movement, operational, and snapshot data are structurally separated. Project progress is periodic while project master data persists. See historical limitations below. |
| Historical preservation | NEEDS WORK | Quarterly snapshots and progress records are separate and official reports are deletion-protected. However, appointments, businesses, committees, assets, and projects are editable master records; the application does not consistently force append/close-and-replace operations. Indirect report children and direct ORM bulk updates are not database-trigger protected. |
| Previous-quarter comparison | PASS | Latest earlier approved, locked, or archived report is selected; drafts are ignored; Q1/Q4 chronology uses dates; missing history is safe. Regression tests cover these cases. |
| Population and households | PASS WITH NOTES | Positive integer counts, snapshot grain uniqueness, verified population aggregation, net migration, average household size, zero-denominator handling, and household breakdown validation are tested. Population change and dependency-ratio indicators are not implemented. Household PII is excluded from analytics/exports and analyst detail access. |
| Governance, visits, training | PASS WITH NOTES | Appointment chronology, inactive-committee meeting rejection, attendance breakdowns, decision completion, training chronology/subgroups/cost, percent bounds, and period-date checks exist. Overdue decision metrics and strict controlled status vocabularies remain absent. |
| Water, sanitation, waste, energy | PASS WITH NOTES | Non-negative/bounded values, interruption chronology and duration match, sanitation subgroup consistency, working-versus-connected households, and 0-24/0-31 energy bounds are enforced. Reliable/safe-water and repair-time indicators are not yet implemented. |
| Health and disability | PASS WITH NOTES | Records are aggregated and contain no patient names; positive fields and parent/subcount checks exist; analysts cannot open detailed records. Per-1,000, referral, recovery, inclusion, and trend indicators are deferred. Other operational roles within a location are not separated by health-specific field permissions. |
| Community safety | PASS WITH NOTES | No victim/suspect name field; offence type is reference data; reported/unreported explanation and date logic added; analytical exports remain summaries only. Severity and case status are free text and confidentiality is not field-level. |
| Agriculture and food | PASS WITH NOTES | Non-negative quantities, harvested allocation consistency, Decimal money, reporting-period shortage-day bounds, data source, and units are present. Controlled unit/reference vocabularies are incomplete. |
| Business and finance | PASS WITH NOTES | Closure chronology, employee consistency, Decimal money, FJD defaults, no bank account number, unique account/report grain, and exact balance reconciliation exist and are tested. Owner/revenue/licensing vocabularies remain free text; edit-in-place master history remains a risk. |
| IVDP projects | PASS WITH NOTES | Unique village project code, date logic, 0-100 percentages, completion-date requirement, non-negative budgets, beneficiary bounds, milestone ownership, and historical progress records exist. Schedule/budget/overdue metrics are not implemented. |
| Climate, disaster, traditional culture | PASS WITH NOTES | Non-negative count fields, Decimal damage/cost types, active flags, controlled traditional stages/risk, appointment chronology, and confirmed-date validation exist. Hazard/severity/status vocabularies and preparedness/title-vacancy indicators are incomplete. |
| Evidence security | PASS WITH NOTES | Size, extension, signature/container type, filename basename, checksum, UUID, protected URL, role/location access, and object-ID manipulation tests pass. Malware scanning, archive expansion limits, and storage encryption are deployment responsibilities. |
| Data-quality engine | PASS WITH NOTES | Stable rule codes, duplicate suppression, retained/resolved history, critical submission blocking, warning behaviour, and 30/25/20/15/10 scoring are implemented. Only seven rules exist and previous-value comparison is not yet implemented. |
| Workflow | PASS WITH NOTES | Report and amendment transitions are transactional, locked, scoped, role checked, self-approval protected, acknowledged, and audited. Phase E provides authorised post-approval corrections without reopening the report. Production acceptance still requires the exact role matrix and state machine to be signed by the data owner. |
| Permissions | PASS WITH NOTES | Cross-village detail and evidence tests, export scoping, POST ownership binding, analyst isolation, author/reviewer/approver restrictions, and non-author validation denial pass. A full province/Tikina/two-village matrix for every listed role is not present. Django admin permissions are model-global and must be granted only to trusted administrators. |
| Forms, CSRF, XSS, injection | PASS | Entry forms are built from explicit field tuples; report/location ownership is server-bound; all observed POST templates include CSRF; no raw SQL or `safe` rendering was found; template escaping is default; spreadsheet formula injection is neutralised; query filters are validated. |
| Dashboard and performance | PASS WITH NOTES | Location scoping and aggregate output are enforced; invalid/empty filters are safe; report selectors use `select_related`. Section pages intentionally query each configured group and can issue many queries; no formal query-count budget exists. |
| Exports | PASS WITH NOTES | Filters and permissions are re-applied; summary fields exclude PII; audit rows are created; CSV/XLSX Unicode is supported; numeric XLSX cells are tested. The minimal Helvetica PDF generator does not reliably support all Unicode/iTaukei characters and large exports are synchronous. |
| Templates, mobile UX, accessibility | PASS WITH NOTES | Responsive breakpoints, mobile navigation, sticky form actions, explicit labels, error summaries, focus styles, skip link, table/header usage where applicable, reduced-motion CSS, and text status labels are present. No automated WCAG 2.2 AA scan, keyboard lab test, or formal contrast report was run. Tailwind is loaded from a public CDN. |
| Internationalisation | PASS WITH NOTES | English/iTaukei switch and form localization pass; user-edited PO changes are reflected after compilation; reference models commonly have `name_en/name_fj`. Translation coverage is incomplete and new audit-era UI strings fall back to English; official terminology requires owner review. PDF Unicode remains deficient. |
| Audit logging | PASS WITH NOTES | Login/failure/logout, report/entry/section, workflow, upload/access, export, and assignment events exist. Request-aware assignment changes capture the administrator and request metadata; audit rows are location-grained and immutable through normal ORM operations. Direct non-request ORM writes retain actor-null fallback events, and direct SQL remains an operational control boundary. |
| Django admin | PASS | TNK roles, not `is_staff` alone, govern access. System Administrators are national; Provincial Administrators are location-scoped and cannot escalate accounts or roles; Auditors see only scoped audit rows. Querysets, object URLs, related selectors, sensitive displays, workflow immutability, filters, search, autocomplete, and date navigation are covered by common controls and tests. |
| Dependencies and secrets | PASS WITH NOTES | `.env`, SQLite databases, media, coverage, caches, and private output are ignored; production packages are constrained. DRF, django-filter, drf-spectacular, openpyxl, and Pillow are installed but not all are used by the current web implementation. `pip-audit` was unavailable locally, so the dependency vulnerability scan was not executed. |
| Backup and restore | PASS WITH NOTES | A real isolated PostgreSQL 18 custom backup and empty-target restore passed, as did protected-media ZIP backup/restore, checksum reconciliation, record checks, and persistence after restart. Encryption, off-site transfer, scheduling, retention expiry, and quarterly operational ownership remain infrastructure responsibilities. |
| Deployment | PASS WITH NOTES | Production settings and deployment checks pass; local Tailwind CSS, CSP, JSON logging, privacy-scrubbed Sentry, database-aware health checks, static caching, Gunicorn entrypoint, protected-media denial, and persistent volumes are configured. Docker Compose YAML parses, but Docker/Nginx runtime build/start checks remain unexecuted because Docker and Nginx are unavailable on this host. |
| Mobile readiness | PASS WITH NOTES | UUIDs, timestamps, record versions, service-layer validation, protected attachment IDs, and historical snapshots help future APIs. Browser sessions, incomplete API endpoints, mutable master data, limited conflict handling, and no offline sync protocol remain blockers for an offline mobile client. |

## 5. Tests and tools executed

| Command/check | Result |
|---|---|
| `python manage.py check` | PASS, 0 issues |
| Production `python manage.py check --deploy` with temporary secure environment values | PASS, 0 warnings |
| `python manage.py makemigrations --check --dry-run` | PASS, no changes |
| `python manage.py showmigrations` | PASS, all project migrations applied |
| `python manage.py migrate --plan` | PASS, no pending operations |
| Clean test settings migration from zero | PASS |
| Focused regression suite after fixes | PASS, 25/25 |
| Final `coverage run manage.py test tests` | PASS, 62/62, 0 failed, 0 skipped |
| Final `pytest` suite | PASS, 62/62 after excluding generated `tmp*` directories from collection |
| `coverage report -m` | PASS, 92% (2,613 statements; 203 missed, including tests/migrations) |
| `ruff check backend` using project Ruff config | PASS; emitted a non-code access warning for an inaccessible temporary directory |
| `docker compose config/build` | NOT RUN: Docker command unavailable |
| `pip-audit` | NOT RUN: command unavailable; CI installs and runs it |
| PostgreSQL restore rehearsal | NOT RUN: PostgreSQL service/client and isolated target unavailable |

The baseline suite contained 49 tests: 48 passed and one stale translation expectation failed. The final suite contains 62 passing tests. Coverage increased from 95% on the smaller baseline (2,220 statements) to 92% after adding code and tests (2,613 statements); the percentage remains above the 80% target.

## 6. Defects fixed

1. Included archived official reports in previous comparison and historical deletion protection.
2. Preserved data-quality issue history, reused stable open issues, and automatically resolved corrected issues.
3. Added practical content inspection and filename normalization for evidence uploads.
4. Restricted detailed records/evidence from analyst-only users while preserving aggregate analytics.
5. Restricted mutating manual validation to assigned authors and editable reports.
6. Validated malformed analytics/export query parameters without server errors.
7. Emitted real numeric XLSX cells.
8. Humanised duplicate creation races while retaining the database unique constraint.
9. Added assignment-change audit events.
10. Added official-report read-only/delete controls in report and domain admin screens.
11. Added high-risk cross-field, chronology, bounds, ownership, and non-negative validations across domain models.
12. Corrected the stale compiled-translation regression test.
13. Added an analyst-specific dashboard/navigation experience that does not link to forbidden details.
14. Corrected Docker static collection/sharing, health checks, required database password, and protected-media persistence.
15. Corrected backup documentation so database and media responsibilities are not conflated.

## 7. Data integrity and classification findings

| Class | Examples | Assessment |
|---|---|---|
| Reference | Age group, official role, crop type, health condition, disability/offence type | Correctly separate, though several free-text fields should become approved reference vocabularies later. |
| Master | Village, household, person, appointment, committee, water source, business, asset, project, traditional unit/title | Structurally correct, but several histories rely on user discipline rather than append-only services. |
| Movement | Population movement, asset/business movement | Correct and queryable. |
| Operational | Meetings, visits, training, interruptions, maintenance, incidents, milestones/risks | Correctly linked to a period/report where appropriate. |
| Snapshot | Population, housing, sanitation, energy, health, disability, crop, food, finance | Correct historical grain; official direct report-linked records receive admin protection. |

The dominant `PROTECT` strategy is suitable for government reporting history. Intentional `CASCADE` uses are confined mainly to dependent records, but deleting a draft parent can still delete those dependants. Production policy should prefer archive/deactivation for master data. Database triggers or a dedicated immutable revision layer would be required to make approved child immutability absolute against privileged SQL and `QuerySet.update()`.

## 8. Workflow transition matrix

| Action | From | To | Roles | Extra controls |
|---|---|---|---|---|
| Submit | draft, returned | submitted | Turaga ni Koro / Village Data Assistant | Declaration; validation; no critical issue |
| Start Tikina review | submitted | under Tikina review | Mata ni Tikina / Roko Veivuke | Location scope |
| Return | Tikina or provincial review | returned | Tikina/provincial reviewers | Required correction comment |
| Forward | Tikina review | provincial review | Mata ni Tikina / Roko Veivuke | Location scope |
| Approve | provincial review | approved | Roko Tui | Acknowledgement; no self-approval; validation |
| Lock | approved | locked | Roko Tui / system administrator | Acknowledgement; no self-lock |

Architecture gap: `ready_for_validation`, `rejected`, and `archived` are statuses but have no legal service transitions. The implementation therefore uses validation as a check while retaining `draft`, then submits directly. This must be approved as the real state machine or corrected in a later workflow migration with explicit transition and UI tests.

## 9. Implemented indicator definitions

| Code | Formula | Numerator / denominator | Sources and filters | Unit / missing handling |
|---|---|---|---|---|
| `total_population` | Sum of population counts | Verified count sum / none | `PopulationSnapshot`, current report, `verification_status=verified` | people; no rows returns 0 |
| `average_household_size` | Verified population / active households | verified population / count of `Household(is_active=True)` in village | Population snapshot + household master | people per household; zero households returns null |
| `net_migration` | moved in + returned - moved out - temporarily left | incoming movements / outgoing movements | `PopulationMovement`, same village and period | people; missing sides treated as 0 |

These formulas are deterministic and covered with known-value and zero-denominator tests. The broader approved catalogue is intentionally not claimed as implemented.

## 10. Security and permission findings

Location scoping is performed again in selectors and services, not only in templates. Object-ID manipulation tests show another village report/document is denied. Form registries do not expose report/village ownership fields, and related choices are narrowed to the report village. Exports query the scoped report selector again and contain only report-level summaries.

Remaining risks:

- Confidentiality labels are stored but do not yet drive a complete per-role/per-document access matrix. Non-analyst operational users in the same location may see restricted evidence if they have detailed-report access.
- Django admin model permissions are not automatically province/Tikina/village scoped. Staff status and domain permissions must be limited to trusted central administrators until scoped admin querysets are implemented.
- The system has no malware scanner or quarantined upload workflow.
- Tailwind is loaded as third-party JavaScript from a CDN; a production Content Security Policy and locally built CSS are recommended.
- Login throttling uses local cache and is not a substitute for proxy/network rate limiting in a multi-instance deployment.

## 11. Performance findings

The report selector preloads village, Tikina, period, preparer, and previous report. Analytics uses database aggregation and limits displayed reports. Entry lists are capped at 100. Obvious report-list N+1 access is avoided.

The section page executes a query per one of its entry groups and repeats those queries for previous-report comparisons. This is bounded (42 groups across 17 sections, not on one page) but has no measured query-count contract. Data-quality validation loops through households, water sources, energy snapshots, businesses, projects, and 17 sections; it is acceptable for village-scale data but should be profiled with production volumes. Exports are synchronous and materialise rows in memory.

## 12. Accessibility and UX findings

The reviewed templates include a skip link, visible focus, explicit form labels, required-text alternatives, error summaries/alerts, non-colour status text, responsive layouts, mobile navigation, and reduced-motion handling. User-entered values use Django's escaping. The analyst UI now points to aggregate analytics instead of forbidden detailed pages.

Remaining work is a browser-based keyboard and screen-reader pass, automated WCAG scanning, contrast measurement, chart text/tabular alternatives, and testing on the low-powered mobile devices and networks expected in villages.

## 13. Remaining technical debt and risks

| Priority | Item | Recommended action |
|---|---|---|
| HIGH | Workflow differs from the approved state diagram. | Obtain owner approval for the exact matrix, then implement ready/reject/archive transitions and migration-safe tests. |
| HIGH | No completed Docker/PostgreSQL deployment and restore rehearsal. | Build in staging, migrate an empty PostgreSQL DB, collect static, upload/download evidence, restart containers, restore DB/media, and record results. |
| HIGH | Confidentiality is not enforced as a full field/document role matrix. | Approve a privacy matrix and enforce it in a central policy service with tests for every role/location. |
| HIGH | Mutable master data can change how an old report's comparison page looks. | Add close-and-replace appointment/business/committee/project services or explicit effective-dated snapshots; prohibit in-place historical edits. |
| MEDIUM | Indicator catalogue is limited to three population indicators. | Approve formulas/data owners before implementing health, water, project, disaster, and cultural indicators. |
| MEDIUM | PDF export is a minimal single-page Helvetica document. | Replace with a Unicode-embedded, paginated PDF implementation and test iTaukei names. |
| MEDIUM | Admin domain screens are not location scoped and have sparse search/filter tooling. | Keep permissions central-only now; later add scoped querysets, search, filters, and autocomplete. |
| MEDIUM | Assignment audit events cannot name the acting administrator. | Move assignment writes through request-aware services/admin hooks and store actor/IP/user agent. |
| MEDIUM | Several categorical fields remain free text. | Convert only after controlled vocabularies and migration mappings are approved. |
| COMPLETE | No authorised approved-report revision mechanism. | Phase E added immutable amendment/change records, independent approval, field overlays, indicator overlays, supersession lineage, admin protection, and tests without weakening village-period uniqueness. |
| LOW | Requirements include currently unused API/Excel/image packages. | Retain only if near-term API/import work is approved; otherwise remove after dependency-owner review. |
| LOW | Source files are intentionally compact and not Black-formatted. | Gradually format per app after establishing a clean Git baseline; do not rewrite migrations. |

## 14. Deferred items

The audit did not add a mobile API, offline synchronisation, new controlled-reference models, or malware scanning infrastructure. Phase E subsequently added the approved-report amendment subsystem documented in `report-amendments.md`. The remaining deferred items require product, data-owner, privacy, and deployment decisions.

The supplied realistic end-to-end flow is substantially represented by the workflow/location/form/export tests, but there is not one fixture containing every named user and every step across two Tikinas and three villages. Before production acceptance, add that named acceptance scenario, including corrections after return, audit-event assertions, second-village isolation, and a real PostgreSQL backend.

## 15. Mobile-readiness assessment

Status: **PASS WITH NOTES**. UUIDs, timestamps, record versions, service functions, deterministic validation, protected document UUIDs, and snapshot history are good foundations. A mobile client should not be started until API authentication/authorization, sync cursors, idempotency keys, conflict resolution, attachment resumability, and immutable-master/revision behaviour are defined and tested independently of browser sessions.

## 16. Deployment-readiness assessment

Status: **NEEDS WORK**. The code settings and packaging are materially improved and pass Django's deployment check, but Docker was unavailable and PostgreSQL backup/restore was not rehearsed. Production approval requires a clean staging build, secrets management, TLS proxying, locally built static assets/CSP, persistent encrypted database and media storage, monitoring/alerting, off-site backups, restore evidence, load sizing, and a signed privacy/access matrix.

## 17. Final recommendation

Proceed with controlled user acceptance testing using non-production or approved test data. Do not open the service broadly or load sensitive live health, household, safety, or evidence data until the HIGH remaining items above are resolved or formally accepted by the system owner and privacy/security authority. Re-run the complete checks, tests, PostgreSQL migration, Docker build, and restore rehearsal in the exact production-like environment before go-live.
