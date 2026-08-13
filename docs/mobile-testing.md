# Phase 12: mobile testing

The automated suite is split between authoritative Django/API integration
tests and isolated Flutter runtime tests. Test data uses multiple villages and
includes the required Test Province / Tikina A / Village A1 workflow.

## Coverage matrix

| Concern | Django/API | Flutter |
| --- | --- | --- |
| Login, refresh, logout, device revocation | Mobile API tests | Auth repository tests |
| Location and confidentiality permissions | Permission and confidentiality suites | User-scoped cache tests |
| Bootstrap and reference data | Mobile API tests | Bootstrap repository tests |
| Offline create/edit and restart persistence | Sync/report API tests | Reporting and encrypted database tests |
| Batch sync, cursor, idempotency and partial failure | Mobile sync API tests | Sync repository tests |
| Record-version conflict | Mobile sync API tests | Conflict preservation test |
| Evidence metadata, upload and permissions | Mobile API/document tests | Evidence encryption tests |
| Validation, submission and returned reports | Workflow/API tests | Validation repository tests |
| Bilingual preference and approved fallback | Mobile API/catalogue tests | Localization controller tests |
| Dashboard and analytics scope | Dashboard/API tests | Dashboard repository tests |

The full backend acceptance scenario additionally exercises server records,
workflow transitions, validation, review return/resubmission, location denial,
and audit history. Device-only camera and operating-system process termination
remain manual release checks because they require physical platform services.

## Commands

From `backend`:

```powershell
..\tnk_venv\Scripts\python.exe -m pytest -q
..\tnk_venv\Scripts\python.exe manage.py test
..\tnk_venv\Scripts\python.exe manage.py makemigrations --check --dry-run
```

From `mobile` with the repository Flutter SDK:

```powershell
flutter test
dart analyze lib test
```
