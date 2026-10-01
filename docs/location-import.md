# Working Fiji location seed: reconciliation before import

**Local import status:** following administrator approval, the non-conflicting
seed was applied on 26 August 2026 after a verified SQLite backup. It added
13 provinces, 176 Tikina and 1,097 villages. See
[the audit follow-up](location-reconciliation-2026-08-26.md) for verification.
Production has not been changed. The commands below remain the operating guide
for future runs and other environments.

## Status and architecture

Use `backend/data/tnk_fiji_locations_master.csv` as the machine input. It is a
byte-for-byte copy of the supplied CSV, not an authoritative register. The Excel
reference is not needed for import and has not been used to override the CSV.

The existing models are `apps.locations.Province`, `Tikina` and `Village`.
Tikina has a protected foreign key to Province; Village has a protected foreign
key to Tikina. All three already have integer primary keys, unique UUIDs, codes,
English/Fijian names, `is_active`, timestamps and record versions. Codes are
unique globally for Province and within the parent for Tikina/Village. Names
are not database-unique. No Division model or slugs are present; division remains
reconciliation metadata. No models, fields, constraints or migrations were added.

User assignments reference exactly one location level. Reports protect their
Village foreign key. Analytics, workflow, reports and mobile serializers traverse
the existing foreign keys; no fixed location IDs are used by this import.
`seed_reference_data` seeds reference categories, not national locations;
`seed_demo_data` creates the explicitly fictional demonstration hierarchy.

## Matching and apply rules

- Dry run is the default. Only explicit `--apply` permits database inserts.
- Names are compared after trimming/collapsing spaces and case-folding. Identity
  includes the entire parent path. A case/space-only match reuses the existing
  object without changing its name, code, active state, primary key or UUID.
- Similar spellings and administrative suffixes such as `Lau Province` versus
  `Lau` are review suggestions only. No automatic alias, rename, move or merge.
  Similarity uses a conservative heuristic (ratio >= 0.82, names at least four
  characters); it is not a substitute for the official register.
- Repeated names under different parents remain distinct when both identities
  are represented. If an existing namesake's original path is absent from the
  seed, a proposed new parent is conservatively flagged as a possible relocation
  **or** a distinct namesake, and skipped pending administrator review.
- Every `REVIEW` village is skipped, even if it already has an exact DB match.
  Parents used only by REVIEW rows are not created. Parents shared with validated
  SOURCE_SEED rows may be created. Notes, status, division and URLs are retained
  in the reconciliation CSV, not new model fields.
- Duplicate CSV paths, invalid fields, incompatible division/province mapping,
  or helper-key reuse across identities fail the whole apply before any writes.
  DB duplicates, spelling/code conflicts and unresolved/inactive parents block
  the affected branch. Unaffected safe branches can still be added by `--apply`.
- Existing records absent from the seed are `EXISTING_ONLY`, never removed.
  Active-state differences are reported and never applied to existing objects.
- New provinces use the CSV province code only when it is unoccupied. New Tikina
  and Village codes are deterministic internal `ST`/`SV` plus 18 hexadecimal
  characters derived from the full normalised path; they are **not official
  government codes**. CSV helper keys are audited, not forced into code/UUID fields.
- Reconciliation loads the hierarchy in three queries. Inserts use cached parent
  objects and `get_or_create`, inside one transaction. Unexpected errors roll back
  all inserts. PostgreSQL locks the three location tables while reconciling and
  inserting; schedule apply in a maintenance window. SQLite concurrent writes
  may abort the transaction safely; rerun the audit before retrying.
- Reconciliation output is a pre-apply plan, not a log of committed inserts.
  Choose a **new output filename** for each audit: files are created exclusively,
  never overwritten. CSV cells that could be spreadsheet formulas are escaped.

## National control discrepancy

Input controls are 14 provinces / 189 distinct Tikina / 1,172 unique village rows.
The Parliament-hosted [Public Accounts Committee review, introduction p. 6](https://parliament.gov.fj/wp-content/uploads/2025/05/Review-Report-Provincal-Council-vol-4-to-6-Final-Copy.pdf)
states 14 provinces / 190 districts / 1,172 villages. This supports the warning;
it does not identify a missing district or verify every detailed seed row.
Do not invent a district, move villages, include Rotuma, or force totals to match.
Obtain current iTaukei Affairs confirmation before treating the seed as authoritative.

## Commands from the project root (PowerShell)

### 1. Audit the local SQLite database — no database writes

```powershell
New-Item -ItemType Directory -Path output/location_audit -Force | Out-Null
& '.\tnk_venv\Scripts\python.exe' backend/manage.py import_locations --settings=config.settings.local --file backend/data/tnk_fiji_locations_master.csv --dry-run --report-output output/location_audit/local-review-01.csv
& '.\tnk_venv\Scripts\python.exe' backend/manage.py check_locations --settings=config.settings.local
```

Omitting `--dry-run` is also read-only. Use `--province Lau` for a scoped review;
the file's national control counts and CSV validation still cover the whole file.
Use `--verbose` for per-record terminal details. Invalid input exits nonzero after
writing available reconciliation details. Integrity checks exit nonzero if issues
are found and never repair anything automatically.

### 2. Back up before any apply

The checked local settings use SQLite at `backend/db.sqlite3` (not the root-level
`db.sqlite3`). The helper reads the database path from the selected Django settings,
uses SQLite's online backup API (safe with a live database/WAL), verifies the copy,
and refuses to overwrite any existing file:

```powershell
$locationBackupStamp = Get-Date -Format 'yyyyMMdd-HHmmss'
& '.\tnk_venv\Scripts\python.exe' scripts/backup_tnk_sqlite.py --settings=config.settings.local --output "output/location_audit/tnk-before-locations-$locationBackupStamp.sqlite3"
```

Keep backups private: they contain the **entire database**, not just locations.
Do not commit them. A failed backup retains any incomplete destination for review;
it must not be used for restore. Test restoring a copy separately before production.

`config.settings.production` requires PostgreSQL via `DATABASE_URL`. Production
credentials and its live database have not been inspected. Configure a protected
PostgreSQL service entry `tnk_prod` for the **same host/database/user** as the
deployment settings (password in `.pgpass` or another approved secret mechanism),
then back up with PostgreSQL tools:

```powershell
$locationBackupStamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$locationBackupPath = "output/location_audit/tnk-production-$locationBackupStamp.dump"
if (Test-Path -LiteralPath $locationBackupPath) { throw 'Backup already exists' }
pg_dump --dbname='service=tnk_prod' --format=custom --file=$locationBackupPath
if ($LASTEXITCODE -ne 0) { throw 'PostgreSQL backup failed; do not apply' }
pg_restore --list $locationBackupPath
```

Use an approved secure destination on the production host if `output/location_audit`
does not exist there. Verify a restore into a separate database; never restore over
the live database as an import step.

### 3. Apply only after administrator review and a verified backup

The dry-run/apply logic is covered by automated tests, including an isolated full
seed import and repeat import. These commands are provided for the administrator;
the local apply was subsequently approved and executed as recorded above.
They have **not** been run against production.

For the checked local database, after approving the reconciliation:

```powershell
& '.\tnk_venv\Scripts\python.exe' backend/manage.py import_locations --settings=config.settings.local --file backend/data/tnk_fiji_locations_master.csv --apply --report-output output/location_audit/local-approved-plan-01.csv
& '.\tnk_venv\Scripts\python.exe' backend/manage.py check_locations --settings=config.settings.local
```

For production, first supply the deployment's normal environment variables, run
the production-specific dry run, and review **that** report (local findings do not
describe the production database):

```powershell
& '.\tnk_venv\Scripts\python.exe' backend/manage.py import_locations --settings=config.settings.production --file backend/data/tnk_fiji_locations_master.csv --dry-run --report-output output/location_audit/production-review-01.csv
# STOP: review discrepancies, obtain approval, and verify the PostgreSQL backup.
& '.\tnk_venv\Scripts\python.exe' backend/manage.py import_locations --settings=config.settings.production --file backend/data/tnk_fiji_locations_master.csv --apply --report-output output/location_audit/production-approved-plan-01.csv
& '.\tnk_venv\Scripts\python.exe' backend/manage.py check_locations --settings=config.settings.production
```

The `check_locations` output supplies actual per-province post-apply totals.
No migration is needed. Do not expect national totals while conflicts or REVIEW
rows remain skipped. Never resolve a discrepancy just to increase the count.

## Integration checks

Imported records are picked up by model-backed administration selectors and the
existing Province → Tikina / Tikina → Village options endpoint. That endpoint now
returns both the existing UUID and the database ID needed by Django form choices,
rejects malformed IDs, and excludes inactive parents/children. Assignment role
rules have not changed; no users are reassigned by the importer.

The mobile village-choice endpoint lists only active hierarchy branches. Bootstrap
retains inactive locations referenced by existing reports to preserve offline
history. Report endpoints and historical foreign keys are unchanged. Analytics
continues to aggregate through village/tikina/province relationships.

Tests cover parsing, zero-write dry runs, exact/case/similarity matching, parent
identity, duplicates, REVIEW handling, inactive parents, rollback, idempotency,
FK/assignment preservation, report-output safety, bounded reconciliation queries,
backup safety, selectors, mobile history, and examples across all four divisions.

Run the full backend regression suite from the project root:

```powershell
& '.\tnk_venv\Scripts\python.exe' -m pytest backend/tests -q -p no:cacheprovider --tb=short
```

Pytest selects `config.settings.test` and an isolated SQLite database; it does not
apply the seed to the configured local or production database.
