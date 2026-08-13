# R9 staging backup and restore rehearsal

Date: 13 August 2026 (Pacific/Fiji)

Status: **PARTIAL PASS — FINAL ARTIFACT RESTORE NOT APPROVED**

This is a local Docker rehearsal with fictional data. R7/R8 did not have an
approved certificate-valid staging endpoint, so this evidence is not tied to a
real staging release candidate and must not be represented as production
recovery approval.

## Source scenario

The guarded rehearsal source is PostgreSQL 17 in an isolated database named
`tnk_r9_source_rehearsal`. All 54 migrations were applied from zero. The source
contains:

| Record/check | Count/result |
| --- | ---: |
| Users | 4 |
| Roles | 11 |
| Provinces / Tikina / villages | 1 / 1 / 1 |
| Reporting periods | 2 |
| Reports | 2 |
| Approved reports | 1 |
| Locked reports | 1 |
| Immutable approval actions | 11 |
| Data-quality issues | 1 resolved warning |
| Protected evidence documents | 1 |
| Indicator values | 546 |
| Audit events | 26 |
| Export audits | 3 |

The protected fictional PDF checksum was verified by the guarded Django command
before backup. The four fictional users deliberately have unusable passwords;
mobile authentication against this recovery dataset is therefore not permitted
or claimed.

## Final backup artifacts

Directory: `output/r9/20260813T150500+1200/`

| Artifact | Bytes | SHA-256 | Duration |
| --- | ---: | --- | ---: |
| PostgreSQL custom archive | 494,515 | `5acce1d209382f12b6a90dd597d763f9d6f46b652db99aebd7b26629b370429d` | 26.00 s |
| Protected-media ZIP | 456 | `dd60bcbdc80506c12721317f7efcb525af4f5ddbbb99c983884f8209cf4cab04` | 12.03 s |

The media archive contains the 52-byte fictional PDF plus the 20-byte R6
persistence marker. Their individual SHA-256 values were recorded during the
rehearsal. A secret-free configuration inventory accompanies the artifacts.
No `.env`, credential, token, key, or signing file is included. These local
artifacts are not encrypted or off-site; approved infrastructure must encrypt
and transfer retained backups.

Database backup command (run inside the isolated PostgreSQL container):

```text
pg_dump --format=custom --no-owner --file=/tmp/tnk-r9-final.dump \
  -U tnk_insight tnk_r9_source_rehearsal
```

Media backup command:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass \
  -File scripts\backup-media.ps1 \
  -MediaRoot <isolated-media-copy> \
  -OutputFile <timestamped-media-zip>
```

## Completed clean restore proof

Before the final source was extended with a separate locked report, an earlier
timestamped archive was restored into a brand-new PostgreSQL container, database
volume, media volume, and empty media directory. No existing source was
overwritten.

| Check | Result |
| --- | --- |
| PostgreSQL custom restore | PASS, 31.52 s |
| Migrations | 54 |
| Users / roles | 4 / 11 |
| Approved report | present |
| Protected evidence checksum/download | PASS |
| Indicator values / export audits | 273 / 3 |
| Restored media files | 2 |
| Django migrations at startup | no pending migrations |
| Static collection | 158 files |
| Gunicorn | running with three workers |
| HTTP health | 200, `{"status": "ok"}` |
| Guarded restored verification | PASS, 32.17 s |

The standalone restored web container did not inherit the Compose healthcheck,
so an initial harness incorrectly waited for a nonexistent Docker health state.
Direct HTTP and guarded application verification passed; application behavior
was not changed.

## Final restore gate

The final artifacts include both the approved and locked reports and the
resolved quality issue. Creation of the second clean `tnk_r9_final_*` restore
environment was not approved at the execution prompt. No such environment was
created or modified. Consequently, the final archive's approved/locked/history/
quality-state restore is **NOT EXECUTED**, and R9 is not a full pass.

## Recovery objectives and response outline

The current documented targets are RPO 24 hours and RTO 8 hours, both subject to
infrastructure and project-owner approval. The observed local timings do not
establish production RTO.

- Server loss: isolate the failed host, provision from the approved immutable
  image/configuration, restore database and media into new infrastructure, rotate
  exposed host credentials, verify health and authorization, then switch traffic.
- Database loss: stop writes, preserve logs, select the latest verified encrypted
  backup within RPO, restore into a new database, verify migrations/counts/audit
  history, and obtain owner approval before cutover.
- Media loss: prevent further uploads, restore the matching media generation,
  reconcile database document rows and checksums, and test authorized downloads.
- Credential compromise: revoke/rotate the affected database, application,
  signing, administrator, and backup credentials; invalidate sessions/tokens;
  inspect immutable audit records; notify accountable security/privacy owners.
- Mobile device loss: revoke the registered device and refresh tokens, disable the
  account if needed, inspect sync/audit history, and rely on encrypted local data
  plus Android backup exclusion rather than remote extraction.
- Administrator compromise: disable the account, revoke sessions and privileged
  tokens, preserve evidence, review privileged actions/exports, rotate reachable
  secrets, restore altered data only through governed correction procedures, and
  follow the approved incident/breach process.

Production readiness still requires scheduled encrypted off-site backups,
retention expiry, monitoring/alerts, named recovery owners, key-custody testing,
and a fully approved restore of the final staging release candidate.
