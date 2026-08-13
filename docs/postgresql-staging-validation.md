# PostgreSQL staging validation — R5

Date: 13 August 2026 (Pacific/Fiji)

Status: **PASS FOR ISOLATED LOCAL STAGING REHEARSAL**

This validates PostgreSQL behavior and the TNK workflow on this workstation.
It does not claim deployment to a separately administered staging host.

## Environment

- PostgreSQL server: 18.0
- Cluster: fresh, isolated workspace cluster
- Network exposure: loopback only on temporary port 55435
- Host authentication: SCRAM-SHA-256
- Data checksums: enabled
- Database: `tnk_insight_r5_staging`
- Application role: dedicated non-production role
- Django settings: production settings with HTTPS/HSTS controls enabled
- Data: fictional rehearsal data only
- Final database size: 16 MB
- Cluster state after validation: stopped cleanly

All generated administrator, application and Django secrets remained in the
validation process and were cleared afterward. A one-time ignored bootstrap
file required by Windows `initdb` was removed. No credentials are retained in
the repository or this report.

## Results

| Check | Result |
| --- | --- |
| Empty PostgreSQL 18 cluster initialization | PASS |
| SCRAM authentication and administrator password rotation | PASS |
| Dedicated staging database/application role | PASS |
| Migrations from zero | PASS — 54 migration records applied |
| Migration drift | PASS — no changes detected |
| Django system check | PASS |
| Django deployment check | PASS WITH NOTES — six OpenAPI schema warnings |
| Fictional end-to-end workflow | PASS |
| Protected evidence download/checksum | PASS |
| Indicator calculation | PASS — 273 rows |
| Audited CSV/XLSX/PDF exports | PASS — 3 audit rows |
| Full Django/API/permission suite on PostgreSQL | PASS — 147 passed in 288.98 seconds |
| Ruff | PASS |

The final rehearsal database contained one approved fictional TNK report,
four workflow users, eleven seeded role definitions, 273 indicator values and
three export-audit records.

## Defects found and fixed

1. The staging rehearsal called the development-only `seed_demo_data` command
   while running with production settings. The demo command correctly refused
   the unsafe operation. The rehearsal now loads only approved reference data
   and creates its own fictional isolated workflow records.
2. The suite previously lacked an explicit PostgreSQL test settings module.
   Added `config.settings.postgresql_test`, requiring a complete PostgreSQL
   `DATABASE_URL` and using production-like connection health behavior.
3. Streaming evidence responses close request connections. The confidentiality
   tests used `TestCase`, whose outer transaction cannot tolerate that real
   request lifecycle on PostgreSQL. Converted that class to
   `TransactionTestCase`, allowing a clean reconnect without changing
   application permission or download behavior.
4. The backend-independent staging guard test assumed SQLite. It now explicitly
   mocks a non-PostgreSQL vendor and passes under both SQLite and PostgreSQL.

Regression checks were added for the safe reference-only rehearsal path.

## Outstanding notes

- Six existing `drf-spectacular` schema warnings remain: two unresolved
  serializer method fields and four APIViews without explicit response
  serializers. Runtime/API/permission tests pass, but the generated OpenAPI
  document should be corrected before RC documentation is frozen.
- Docker, Gunicorn, Nginx, TLS, persistent container volumes and an externally
  administered staging host remain Phase R6 gates and are not claimed here.
- Backup/restore for this R5 database was not repeated; that is Phase R9. An
  earlier Phase H rehearsal is documented separately and does not substitute
  for the later RC-linked restore gate.
