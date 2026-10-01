# TNK location implementation and reconciliation — 26 August 2026

## Follow-up: approved local import completed

After the initial audit below, the administrator explicitly approved backing up
the local database and importing only non-conflicting locations. This import is
now complete in the configured local SQLite database, not production.

- Verified backup: `output/location_audit/tnk-before-approved-import-20260826092411.sqlite3`.
- Created: **13 provinces, 176 Tikina, 1,097 villages**.
- Current totals: **15 provinces, 179 Tikina, 1,101 villages**, including existing
  fictional demo locations. These are database totals, not national controls.
- Existing nine location records, 15 assignments and six reports were compared
  against the backup and are unchanged.
- Integrity check passed. Repeat reconciliation proposes zero further additions.
- The administration village-search view successfully rendered imported Nailaga.
- Lau remains unresolved; its 72 seed villages and the three REVIEW villages
  were not imported. No accounts were reassigned or access scopes expanded.
- Verification results: `output/location_audit/approved-import-result-20260826092411.json`.

Refresh **Administration → Locations → Villages** to see the imported records
within the signed-in administrator's allowed location scope. A Lau-only account
will still see the existing Lau records until that hierarchy is resolved.

The sections below record the original pre-import audit and its findings.

## Decision and database status

The safe importer and integrity checker are implemented. **No import has been
applied to the current local or production database.** The first run was a
read-only audit of the configured local SQLite database. Production has not been
connected to or inspected; its reconciliation must be run separately.

| Location level | Local before audit | Local after audit | Proposed additions | Actually created locally |
|---|---:|---:|---:|---:|
| Province | 2 | 2 | 13 | 0 |
| Tikina | 3 | 3 | 176 | 0 |
| Village | 4 | 4 | 1,097 | 0 |

The existing 15 user-location assignments and six reports were not modified.
`check_locations` found no current location-integrity issues. The proposed
additions are a plan, not an imported national register.

## Existing architecture and records

`apps.locations.Province`, `Tikina`, and `Village` already provide the needed
hierarchy. Tikina → Province and Village → Tikina use protected foreign keys.
Integer IDs, unique UUIDs, codes, English/Fijian names, active flags, timestamps,
and versions already exist. Province codes are globally unique; child codes are
unique within their parent. There is no Division model or slug field. No new
model, constraint, or migration is needed. Name duplicates are audited rather
than introducing a constraint against uninspected production data.

Actual current local hierarchy (all nine records active):

| Level | ID | Stored name | Parent |
|---|---:|---|---|
| Province | 1 | Lau Province | — |
| Province | 2 | Fictional Test Province | — |
| Tikina | 1 | Vulaga District | Lau Province |
| Tikina | 2 | Fictional Coastal Tikina | Fictional Test Province |
| Tikina | 3 | Fictional Highlands Tikina | Fictional Test Province |
| Village | 1 | Ogea Village | Vulaga District |
| Village | 2 | Fictional Vunidemo | Fictional Coastal Tikina |
| Village | 3 | Fictional Navutest | Fictional Coastal Tikina |
| Village | 4 | Fictional Korotest | Fictional Highlands Tikina |

Actual per-province local totals, unchanged after the audit:

| Stored province | Tikina | Villages |
|---|---:|---:|
| Lau Province | 1 | 1 |
| Fictional Test Province | 2 | 3 |
| **Total** | **3** | **4** |

## Canonical CSV and reconciliation findings

The supplied CSV was copied unchanged to
`backend/data/tnk_fiji_locations_master.csv`.
SHA-256: `e55004f7f69a1fee20a031592f9205925364e8c01892a4ee55e6c42a05db0df1`.
The Excel reference was not supplied or used to override the machine input.

| CSV province | Distinct Tikina | Unique village rows |
|---|---:|---:|
| Ba | 21 | 102 |
| Bua | 9 | 54 |
| Cakaudrove | 16 | 131 |
| Kadavu | 9 | 75 |
| Lau | 13 | 72 |
| Lomaiviti | 12 | 74 |
| Macuata | 12 | 112 |
| Nadroga-Navosa | 22 | 122 |
| Naitasiri | 16 | 91 |
| Namosi | 5 | 28 |
| Ra | 19 | 89 |
| Rewa | 9 | 52 |
| Serua | 4 | 24 |
| Tailevu | 22 | 146 |
| **14 provinces** | **189** | **1,172** |

These are **source totals**, not current database totals. There are 1,169
SOURCE_SEED rows and three REVIEW rows. No CSV duplicates or invalid rows were
found. Rotuma is excluded, as requested. Division mapping is validated but remains
audit metadata.

Local reconciliation classifications:

| Classification | Count |
|---|---:|
| Exact matches | 0 |
| Case/whitespace-only matches | 0 |
| Possible spelling/suffix variants | 1 |
| Parent-location conflicts | 0 |
| Duplicate CSV records | 0 |
| Duplicate database paths | 0 |
| Existing-only database records, retained | 9 |
| New provinces proposed | 13 |
| New Tikina proposed | 176 |
| New villages proposed | 1,097 |
| Requires manual review | 88 |
| CSV hierarchy nodes without exact database path | 1,375 |

Categories are not all additive: the 1,375 missing-path entries are supplemental
to the primary classification. The single spelling/suffix candidate is **Lau**
versus **Lau Province**. It is not automatically merged or duplicated. Its 13
Tikina and 72 villages are blocked until the parent identity is resolved.
Thus 88 manual-review descendants/rows plus the province candidate make 89 skipped
hierarchy nodes. Once Lau is resolved, its child names must also be reviewed;
`Vulaga District` and `Ogea Village` must not be silently renamed or replaced.

Three source REVIEW villages are skipped, even if an exact database match exists:

| Physical CSV line | Location | Required review |
|---|---|---|
| 51 | Ba / Vuda / Veiseisei | Verify spelling against the official register. |
| 223 | Cakaudrove / Vaturova / Korotasere | Source listed it twice; CSV already deduplicated it. |
| 731 | Nadroga-Navosa / Nadrau / Naga (Vanua Levu) | Verify name and location. |

The reconciliation CSV preserves the original notes, status, source URLs, helper
keys, division, line numbers, matched database IDs, actions, and explanations:
`output/location_audit/location_reconciliation_final.csv` (final repeat audit).
The first audit is also retained as `location_reconciliation_report.csv`.

**National discrepancy:** the Parliament reference gives 190 districts while this
working seed has 189. See the linked primary reference and explanation in
[the operating guide](location-import.md#national-control-discrepancy).
No missing district was invented and no villages were moved to force a total.
Current iTaukei Affairs confirmation remains necessary.

## Files created and modified for this request

Created:

- `backend/data/tnk_fiji_locations_master.csv`
- `backend/apps/locations/reconciliation.py`
- `backend/apps/locations/integrity.py`
- `backend/apps/locations/management/__init__.py`
- `backend/apps/locations/management/commands/__init__.py`
- `backend/apps/locations/management/commands/import_locations.py`
- `backend/apps/locations/management/commands/check_locations.py`
- `backend/tests/test_location_import.py`
- `scripts/backup_tnk_sqlite.py`
- `docs/location-import.md`
- `docs/location-reconciliation-2026-08-26.md`
- Generated local reconciliation CSV under `output/location_audit/` (ignored output).

Modified for this request:

- `backend/apps/administration/views.py`: validate parent IDs, return form IDs
  alongside existing UUIDs, and restrict location options to active branches.
- `backend/apps/mobile_api/views.py`: active village choices; retain inactive
  locations referenced by reports in mobile bootstrap for historical continuity.
- `backend/tests/test_mobile_api.py`: test inactive choices and retained history.

Other changes already in the workspace, including photo-evidence work, were not
reverted. **Location migrations created: zero.** Existing model-backed selectors,
serializers, relationship-based analytics and assignment rules are reused.

## Verification and limits

**Full backend regression suite: 214 passed in 517 seconds.** This includes
22 new location-import tests and one new mobile-history test, plus existing
reporting, workflow, analytics, administration, security and mobile coverage.

New tests cover default/explicit zero-write dry runs, malformed CSV, duplicate
paths and helper keys, parent identity, case/whitespace matches, spelling hints,
REVIEW rows, inactive parents, code conflicts, province scoping, rollback,
idempotency, existing report/assignment preservation, integrity checks, exclusive
report files, bounded reconciliation queries, safe SQLite backup, administration
options, mobile serialization and relationship-based analytics.

The full supplied seed was applied **only to an isolated test database**:
14 provinces / 189 Tikina / 1,169 villages, with all three REVIEW villages skipped.
A second apply created zero additional records. Tests checked representative
hierarchies in Western, Northern, Central and Eastern divisions, including
Lau / Lakeba / Tubou. The test database passed the integrity checker.

`manage.py check` passed and `makemigrations --check --dry-run` reported no changes.
The final local dry run compared complete location, assignment, and report records
before and after the command and verified they were unchanged. The integrity
checker passed again; Ruff passed for the new location code, tests and backup helper.
The PostgreSQL locking path has not been exercised against a production server.
No claim is made that the detailed seed is an authoritative current register.

## Exact audit, backup, and gated apply commands

The [operating guide](location-import.md#commands-from-the-project-root-powershell)
contains the exact PowerShell commands, in this order:

1. Local dry run and integrity check (the audit command is read-only by default).
2. Non-overwriting, verified SQLite backup of the database selected by settings.
3. PostgreSQL `pg_dump` backup and separate restore verification for production.
4. Separate production dry run, administrator review, then explicit `--apply` and
   post-apply integrity check under `config.settings.production`.

Production settings require PostgreSQL through `DATABASE_URL`; the actual local
settings use `backend/db.sqlite3`. Production credentials and database contents
were not accessed. Configure the documented PostgreSQL service to match the
deployment before using its backup command. Choose fresh report/backup filenames.
Do not apply until the administrator has reviewed the relevant database's report
and verified its backup.
