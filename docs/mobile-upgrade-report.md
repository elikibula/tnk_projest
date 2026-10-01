# TNK Insight mobile upgrade report

Date: 2026-08-27

1. **Flutter architecture:** Existing feature-first Flutter/Riverpod/Dio/Drift application with environment entrypoints, encrypted offline storage, synchronization, protected evidence and bilingual UI was retained.
2. **Backend architecture:** Django REST Framework under `/api/v1/`; Django remains authoritative for users, roles, location scope, reporting periods, workflow and indicator calculations.
3. **Problems found:** No reactive 401 refresh, incomplete profile capability data, no mobile analytics or hierarchy exploration, UUID-heavy report lists, omitted closed periods, weak bootstrap error recovery and no configured production host/signing secrets.
4. **Files modified:** Mobile auth, bootstrap, sync, dashboard, reporting, validation, evidence providers and screens; mobile API serializers/views/URLs/tests; `mobile/pubspec.yaml`; `mobile/README.md`.
5. **Files created:** `backend/apps/mobile_api/exploration.py`, `mobile/lib/core/api/authenticated_client.dart`, the exploration repository/providers/screens, profile screen, audit and this report.
6. **Packages:** No runtime package was added or removed. Existing compatible constraints were retained.
7. **Endpoints:** Existing auth, me, dashboard, reporting periods, reports, evidence, validation, declaration, workflow and sync endpoints; new read-only `locations/` and `analytics/` endpoints.
8. **Authentication:** Existing device-bound JWT and secure storage retained; UI capabilities and assignments now come from `/me/`.
9. **Token refresh:** A same-origin authenticated Dio client performs single-flight refresh and retries a rejected request once. Refresh rejection or a second 401 expires the session; an ordinary retry network error does not.
10. **Locations:** Role-scoped, paginated Province/Tikina/Village directory plus cascading report selection. Inactive hierarchy cannot be selected for a new report.
11. **Reporting periods:** Open periods remain selectable; closed periods referenced by authorised history are returned, and clients may explicitly request all periods.
12. **Reports:** Added filters, pagination compatibility, names/labels/timestamps, server-derived editability and workflow history while preserving offline drafts and section forms.
13. **Workflow:** Existing backend transitions remain authoritative; mobile submission now asks for explicit confirmation and shows workflow history.
14. **Analytics:** Added period-aware, scoped overview, comparison, indicators, insights and Province/Tikina/Village drill-down using existing backend calculations.
15. **Administration:** Added safe read-only hierarchy/profile visibility. User, role and location mutations remain in the web admin because no approved mobile mutation API exists.
16. **Security:** Server querysets enforce assignment scope; national analytics requires national permission; authenticated calls fail closed and never send tokens cross-origin; release signing remains fail closed.
17. **Offline/network:** Existing encrypted user-scoped cache, 72-hour bounded offline session, queued evidence and conflict sync retained. Dashboard no longer masks 401/403 with stale cache.
18. **Flutter tests:** No duplicate test file was added; the existing 39 unit/widget tests were run across auth, encryption, bootstrap, reporting, evidence, sync, localization and workflow.
19. **Django API tests:** Contract/security coverage now includes hierarchy scoping, analytics scope/national denial, report filtering/display/editability, data-type metadata, Photo Reports role/scope enforcement, gallery metadata and private image delivery.
20. **Backend changes:** Additive response fields and two read-only endpoints; opt-in pagination preserves older clients that expect arrays.
21. **Flutter analyze:** Flutter 3.44.3 analysis passes with no issues after the safe automated cleanup and a final analyzer rerun.
22. **Flutter test:** 39 passed in the completed upgrade run. A later Windows rerun was blocked before test execution by the Flutter native-assets launcher mishandling the workspace path containing `Django Sites`; this was a tooling/path failure, not a test failure. Flutter analysis after the parity implementation passes with no issues.
23. **Django validation:** All 223 backend tests passed, including 38 mobile API tests and all 6 website Photo Reports tests; Ruff passed; `manage.py check` reported no issues.
24. **Release APK:** Not produced. Production build is correctly blocked by absent production URL and signing credentials. Development APK compilation also stopped at external Maven downloads because the local JDK trust store rejected repository certificates.
25. **APK path:** None; no successful APK was claimed.
26. **Remaining issues:** Supply the real HTTPS production API URL and protected Android signing variables, repair the JDK/Maven certificate trust, rerun analyzer, build signed production APK, and complete physical-device administrator and end-to-end validation. Notification and mobile user-management APIs remain intentionally absent.
