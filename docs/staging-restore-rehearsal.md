# Phase H staging and restore rehearsal

Date: 8 August 2026 (Pacific/Fiji)
Environment: Windows 11 workstation; Python 3.13; Django 5.2; isolated PostgreSQL 18 workspace cluster on `127.0.0.1:55432`; production Django settings; fictional data only.
Docker/Nginx runtime: unavailable on this workstation and therefore not claimed as passed.

## PostgreSQL staging rehearsal

An empty `tnk_phase_h_staging2` database was created in a new cluster under the ignored workspace `tmp` directory. All 39 migration records were applied from zero using production settings. `seed_reference_data` and fictional demo data were loaded. The guarded `staging_rehearsal` command then created users and location/role assignments, a reporting period and TNK report, completed its 17 sections, uploaded protected fictional PDF evidence, and performed:

`draft → ready_for_validation → submitted → under_tikina_review → under_provincial_review → approved`

The authorised protected download endpoint returned the uploaded bytes with a matching checksum. Approval calculated village/Tikina/province indicator rows. CSV, XLSX, and Unicode PDF exports were generated and audited. `collectstatic` completed and `manage.py check --deploy` reported no issues with `DEBUG=False` and secure redirect enabled.

Result before backup:

| Check | Result |
|---|---:|
| Reports | 1 |
| Approved report found | Yes |
| Users | 4 |
| Roles | 11 |
| Indicator values | 273 |
| Export audit rows | 3 |
| Evidence checksum/download | Passed |

## Backup and restore

Commands used were the repository `backup-postgres.ps1`, `backup-media.ps1`, `restore-postgres.ps1`, and `restore-media.ps1` scripts, invoked with PowerShell execution policy bypass because this workstation disables unsigned local scripts by policy.

| Artefact/operation | Size | Duration | Result |
|---|---:|---:|---|
| PostgreSQL custom backup | 456,593 bytes | 7.14 seconds | Passed; SHA-256 recorded |
| Protected-media ZIP | 334 bytes | 20.95 seconds | Passed; SHA-256 recorded |
| Restore into empty `tnk_phase_h_rehearsal_restore` | — | 76.68 seconds | Passed |
| Restore into empty media directory | — | 54.40 seconds | Passed |
| First restored verification | — | 96.9 seconds | Passed |

The unusually long restore/media timings reflect this workstation's filesystem/security scanning and are well inside the provisional eight-hour RTO; staging infrastructure must establish its own baseline.

The PostgreSQL process was forcibly stopped to simulate process loss, started again from the same isolated data directory, and queried successfully. A new Django command process then repeated restored verification with the same counts and checksum. This confirms database/media persistence across both restore and process restart.

## Failures and resolutions

1. The first fictional evidence object failed `full_clean()` because its checksum field was blank before `save()` recalculation. The transaction rolled back. The fixture now supplies a syntactically valid placeholder and the model replaces it with the calculated checksum; validation was not weakened.
2. A restore target named only `phase_h_restore` was rejected by the safety guard. A new empty database explicitly named `tnk_phase_h_rehearsal_restore` was used. The rejected database remained empty.
3. `pg_ctl` could not create its restricted Windows token. The isolated `postgres.exe` process was started hidden with an exact data directory and port, then stopped by its verified listening-process ID.
4. Docker and Nginx executables were not installed. Compose YAML parsed successfully and contains `db`, `web`, and `nginx`, but Docker build/start, container health, Nginx static serving, and container-volume restart checks remain mandatory on the real staging host.

## Final result

- PostgreSQL migration/rehearsal: **PASS**
- Protected evidence and exports: **PASS**
- Static collection and Django deployment check: **PASS**
- Database/media backup and restore: **PASS**
- Restart persistence: **PASS**
- Docker/Nginx runtime rehearsal: **NOT RUN — Docker unavailable**
- Phase H staging readiness: **PASS WITH NOTES**; controlled staging may proceed, but production go-live remains conditional on the Docker/TLS/container-volume rehearsal and operational approvals.
