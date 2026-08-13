# TNK Insight final readiness audit - Phase I

Audit date: 8 August 2026 (Pacific/Fiji)
Scope: Django application, 17-section reporting workflow, 42 entry forms, access control, historical records, indicators, exports, evidence, audit, PostgreSQL, deployment assets, backup/restore evidence, and automated tests.

## Executive verdict

**Go-live readiness: CONDITIONAL**

The application code and database workflow are ready for controlled staging and user acceptance testing. The complete fictional Phase I acceptance scenario passes, all 120 automated tests pass, application statement coverage is 88%, and a clean PostgreSQL 18 database accepts every migration and passes Django's production deployment check. A separate guarded PostgreSQL rehearsal completed report approval, generated 273 indicator values and three audited exports, and verified protected evidence by checksum.

Unsupervised production go-live is not yet authorised. Docker/Nginx/TLS and persistent container volumes could not be exercised because Docker is unavailable on this workstation. The responsible Fiji authorities must also approve privacy, retention, access, sharing, breach, and disposal rules before real sensitive information is entered.

## Phase I acceptance scenario

`backend/tests/test_final_acceptance.py` creates entirely fictional data:

- Test Province; Tikina A and B; Villages A1, A2, and B1.
- System Administrator, Provincial Administrator, Roko Tui, Roko Veivuke, Mata A, Mata B, TNK A1, TNK A2, Data Assistant, Village Nurse, Analyst, and Auditor users.
- A previous approved quarter and a current report, including master-data history.
- Governance committee and meeting, household, population movement, population snapshot, water source, sanitation, health condition, IVDP project, project progress, final declaration, and protected evidence.
- All 17 section statuses completed, while exercising the configured entry-data relationships used by the 42-form registry.

The test verifies the full operational sequence:

1. Create reporting periods and previous/current reports.
2. Display the previous approved quarter.
3. Enter master, governance, household, movement, population, water, sanitation, health, project, and project-progress data.
4. Upload restricted evidence through the real endpoint.
5. Complete all 17 sections and run data-quality validation.
6. Mark ready, submit, begin Tikina review, and return for correction.
7. Correct population data, redeclare, resubmit, review, forward, approve, and lock.
8. Reject editing of locked official data.
9. Calculate and display indicators.
10. Generate audited XLSX and PDF exports.
11. Allow authorised evidence access and reject unauthorised access.
12. Record report, evidence, and export audit events.
13. Reject TNK and Mata users attempting access outside their assigned village/Tikina.

The scenario passes as part of the 120-test suite. A production-settings pytest execution against PostgreSQL emitted its passing test marker and removed its temporary test database, but its command wrapper timed out during post-run shutdown; this is not counted as a clean test-run exit. The independent guarded PostgreSQL rehearsal below exited cleanly and is the authoritative PostgreSQL workflow result.

## Readiness ratings

| Area | Rating | Evidence and remaining condition |
|---|---|---|
| Workflow | **PASS** | Central transitions enforce role, location, quality, declaration, acknowledgement, comments, and separation of duties. Phase I covers return, correction, resubmission, approval, lock, and locked-edit rejection. |
| Historical preservation | **PASS** | Effective-dated master data, close-and-replace services, immutable official history, previous-quarter selection, and frozen report master snapshots are implemented and tested. |
| Confidentiality | **PASS WITH NOTES** | Deny-by-default role, section, clearance, location, linked-object, report-status, evidence, analytics, and export checks pass. Organisational policy and privileged database access remain operational responsibilities. |
| Indicators | **PASS WITH NOTES** | 91 approved definitions exist; 84 are executable. Seven are explicitly unavailable because the present schema lacks defensible denominators or duration/beneficiary inputs; no substitute values are fabricated. |
| Amendments | **PASS** | Approved/locked report corrections use immutable, reviewed overlays with lineage and indicator reaggregation. |
| Exports | **PASS** | Authorised CSV/XLSX/Unicode PDF exports are scoped, typed, formula-safe, paginated, and audited. Phase I verifies XLSX and PDF bytes and their audit rows. |
| Admin | **PASS** | Admin access is role- and location-scoped, sensitive fields are reduced, high-risk records are protected, and assignment changes are accountable. |
| Audit | **PASS WITH NOTES** | Application audit rows are append-only and location-scoped; report, evidence, export, authentication, and admin events are covered. Direct privileged SQL remains outside application-layer controls, and preserved legacy events may have no location scope. |
| PostgreSQL | **PASS** | PostgreSQL 18 accepted all migrations from zero, `check --deploy` passed, no operations remained, and the guarded workflow rehearsal exited successfully. |
| Docker/Nginx | **NEEDS WORK** | Compose YAML exists and parsed in Phase H, but Docker/Nginx executables are unavailable here. Image build, TLS proxy, health, static/media, volume restart, and container restore must pass on the staging host. |
| Backup/restore | **PASS WITH NOTES** | Phase H performed real PostgreSQL and protected-media backup, empty-target restore, checksum verification, and process-restart persistence. Production still needs scheduling, retention, off-site storage, encryption, key custody, and alerting. |
| Security | **PASS WITH NOTES** | Secure production settings, HSTS/cookies/redirects, CSP, permissions policy, request IDs, privacy-scrubbed optional monitoring, protected evidence, and access tests are present. Formal privacy/security approval and a dependency-vulnerability scan in the deployment pipeline remain required. |
| Testing | **PASS** | 120 passed, 0 failed, 0 skipped; 88% application statement coverage; Ruff, dependency consistency, Django check, migration drift, and migration plan all pass. The only local warning is inability to write pytest's optional cache directory. |
| Mobile readiness | **PASS WITH NOTES** | Responsive server-rendered forms and documented future API/mobile boundaries are suitable for current browser use. Offline synchronisation and a native/mobile API are future features and are not represented as delivered. |

## Verification record

| Check | Result |
|---|---|
| `python manage.py check` | PASS - no issues |
| `python manage.py check --deploy` with production settings/PostgreSQL | PASS - no issues |
| `python manage.py makemigrations --check --dry-run` | PASS - no changes detected |
| `python manage.py showmigrations` | PASS - every migration applied |
| `python manage.py migrate --plan` | PASS - no planned operations |
| Full pytest suite | PASS - 120 tests |
| Coverage | PASS - 88% of 4,471 application statements |
| Ruff | PASS |
| `pip check` | PASS - no broken requirements |
| PostgreSQL migration from empty database | PASS |
| Guarded PostgreSQL fictional workflow rehearsal | PASS - approved report, 273 indicator values, 3 export audits, evidence checksum verified |
| Docker runtime | NOT RUN - executable unavailable |
| Python dependency vulnerability audit | NOT RUN - `pip-audit` unavailable; `pip check` is not a vulnerability scanner |

## Remaining issues by severity

### BLOCKER - before real production data or public go-live

1. Run and document the complete Docker Compose/Nginx/TLS rehearsal on the actual staging host, including health checks, static assets, protected media, database/media volumes, restart persistence, and restore into empty volumes.
2. Obtain accountable authority approval for lawful purpose and notice/consent, role access, retention/archive/disposal, correction, public-release thresholds, breach response, and cross-agency sharing for personal, household, health, disability, and safety data.
3. Provision production-only secrets and restricted encrypted storage; schedule monitored, encrypted, off-site database/media backups and prove a restore under the production operating procedure.

### HIGH

1. Run an approved software-composition/vulnerability scan in CI or staging and resolve actionable findings. `pip-audit` was not installed on this workstation.
2. Complete a controlled staging UAT with the named operational roles and obtain workflow, translation, terminology, report, and export sign-off from business owners.

### MEDIUM

1. Decide whether to extend the schema for the seven unavailable indicators; preserve them as unavailable until valid inputs exist.
2. Complete governed reference-vocabulary mapping with representative production-like data and owner-approved bilingual terminology.
3. Establish performance/load baselines and monitoring alert thresholds on production-sized PostgreSQL and deployment infrastructure.
4. Review external map/chart asset dependencies and CSP allow-list choices for the final hosting environment.

### LOW

1. Correct the workstation permission that prevents pytest from writing its optional cache directory.
2. Review future offline/mobile API requirements after browser-based field UAT; they are not required for the current server-rendered release.

## Release decision

- **Controlled staging/UAT:** READY.
- **Production infrastructure rehearsal:** CONDITIONAL on Docker/Nginx/TLS/volume execution.
- **Entry of real sensitive data:** NOT AUTHORISED until privacy, records-management, security, and operational approvals are signed.
- **Overall Phase I verdict:** **CONDITIONAL**.

This verdict deliberately separates verified application readiness from approvals and infrastructure evidence that cannot be created on this workstation.
