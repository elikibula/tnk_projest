# Fictional demonstration data

## Analytics and Photo Reports showcase (2100)

**Installed locally on 26 August 2026.** Verified: 12 additional reports, 60 image
attachments, 1,638 indicator values for 2100; 16 demo reports / 18 reports overall.
Both Roko accounts passed dashboard, gallery and protected-image preview checks.
All 18 existing accounts, 15 assignments, six previous reports and all locations
matched the backup. The four demo-seed tests and 40 analytics/report regression
tests passed (44 total); Django and Ruff checks passed.

Backup: `output/location_audit/tnk-before-demo-showcase-20260826094405.sqlite3`.
Verification: `output/location_audit/demo-showcase-result-20260826094405.json`.
Existing media was not overwritten; the backup covers the database, while the
new protected photo files are additive.

Local shortcuts after signing in:
[Q2 analytics](http://127.0.0.1:8000/analytics/?period=6) and
[2100 Photo Reports](http://127.0.0.1:8000/reports/photos/?year=2100).
Period ID 6 is specific to this local database; other installations should select
2100 Q2 from the period menu.

The additional `seed_demo_showcase` command extends an **already installed** demo
without resetting passwords, roles, assignments, or existing reports:

```powershell
& '.\tnk_venv\Scripts\python.exe' backend/manage.py seed_demo_showcase --settings=config.settings.local
```

Back up the local SQLite database first using `scripts/backup_tnk_sqlite.py`.
The showcase refuses to run with `DEBUG=False` or missing demo accounts/villages.
It never seeds real imported villages or connects to production.

### Included sample data

- **12 new reports**, one per quarter of 2100 for each of Fictional Vunidemo,
  Fictional Navutest and Fictional Korotest. The original 2099 reports remain intact.
- All 42 configured entry types are represented, reusing existing fictional
  masters and adding report-specific population, housing, water, health,
  agriculture, finance, project, climate and other records.
- Population, crop yields, health cases, food shortages, and water outage durations
  vary by village and quarter, providing trends and comparisons.
- Eight approved reports, one submitted, one under Tikina review, one under
  provincial review, and one editable draft. These use the normal declaration,
  validation and workflow services. Official analytics include only official states.
- **60 protected photo attachments**: five per report across agriculture, water,
  housing, projects and climate. They reuse five AI-generated sample scenes,
  prominently labelled **DEMO - SYNTHETIC IMAGE**. They are illustrations of the
  gallery feature, not actual evidence or distinct observations of these villages.
- Q1/Q2/Q3/Q4 attachments demonstrate the Before/Progress/After/Observation filters.
  Reusing a sample does not represent actual before-and-after photography.
  Image dates are seeding timestamps; no fictional GPS or future capture date is used.

### Where to look

1. Sign in as **`demo_roko_tui`** or **`demo_roko_veivuke`** using the existing demo
   password. Select **Fictional Test Province** and a **2100** reporting period.
2. Open **Analytics**. Start with **2100 Q2**, when all three village reports are
   approved. Compare Q1 against Q2 to see comparable coverage across villages.
   Q3 and Q4 intentionally mix workflow states; their official totals cover fewer
   villages and should not be mistaken for like-for-like population change.
3. Open **Photo Reports**, filter **Year = 2100**, and open any submitted or approved
   report. Try its area and stage filters and click an image to enlarge it.
4. Sign in as **`demo_tnk_b1`** to edit the **2100 Q4** draft and try adding photos.
   Senior officers cannot inspect pre-submission photos unless existing policy
   permits it. All confidentiality and location rules remain in force.

System administrators can see all 1,101 current villages; national compliance
therefore includes many villages with no 2100 reports. Use the demo province or
its scoped Roko account for the intended three-village demonstration.

The command skips existing village/quarter reports entirely, even if a tester has
edited them; rerunning it does not duplicate reports or photos. SQL changes are
atomic, with cleanup of newly written photo files if the attempt fails. Shared
historical master records are not overwritten. No model migration is required.

### Image provenance

Project assets are `backend/data/demo_photos/{farm,water,housing,project,climate}.png`.
They were created with the built-in `image_gen` tool. Exact prompts, subject
descriptions and provenance are saved in `backend/data/demo_photos/provenance.json`.
Protected uploaded copies live under the configured media storage, not public static files.

## Original 2099 demo

The development-only `seed_demo_data` command populates TNK Insight so its forms, reports, dashboard, access controls and workflow can be explored without entering real personal information.

From the project root, run:

```powershell
python backend/manage.py migrate
python backend/manage.py seed_demo_data --show-credentials
python backend/manage.py runserver
```

Open `http://127.0.0.1:8000/` and sign in with one of the accounts below. Every account uses the password `Demo-TNK-2026!`.

| Purpose | Username |
|---|---|
| System Administrator and full overview | `demo_admin` |
| Provincial administration | `demo_provincial` |
| Provincial approval | `demo_roko_tui` |
| Tikina support/review | `demo_roko_veivuke` |
| Coastal Tikina review | `demo_mata_a` |
| Highlands Tikina review | `demo_mata_b` |
| Editable Vunidemo report | `demo_tnk_a1` |
| Submitted Navutest report | `demo_tnk_a2` |
| Korotest report under review | `demo_tnk_b1` |
| Village data assistance | `demo_assistant` |
| Health-limited access | `demo_nurse` |
| Project-limited access | `demo_project` |
| Aggregate analytics | `demo_analyst` |
| Read-only audit access | `demo_auditor` |

## What is included

- Fictional Test Province, two Tikina and three villages.
- 2099 Q1 approved historical report for Fictional Vunidemo.
- 2099 Q2 editable draft for Fictional Vunidemo, approximately 82% complete.
- 2099 Q2 submitted report for Fictional Navutest.
- 2099 Q2 report under Tikina review for Fictional Korotest.
- At least one visible record for every one of the 42 configured entry types across all 17 report sections.
- Forty-one fictional households, population and movement records, leadership, meetings, visits, training, housing, assets, water, sanitation, waste, energy, health, disability, agriculture, food security, business, finance, IVDP project delivery, climate/disaster and cultural records.
- Protected fictional PDF evidence, workflow history, audit events and 91 indicator values.

## Suggested walkthrough

1. Sign in as `demo_admin` to view the complete dashboard, administration and audit overview.
2. Sign in as `demo_tnk_a1`, select the 2099 Q2 Vunidemo draft, and open each section to see populated form tables and editable fields.
3. Compare the draft with the approved 2099 Q1 historical report.
4. Sign in as `demo_mata_b` to review the Korotest report and observe Tikina location isolation.
5. Sign in as `demo_analyst` to inspect aggregate dashboards without confidential row-level access.
6. Sign in as `demo_nurse` or `demo_project` to verify section-limited access.
7. Switch between English and iTaukei while viewing forms.

## Safety and repeatability

All names, addresses, organisations, records and evidence are synthetic. The command refuses to run when `DEBUG=False`. Running it again reports that the dataset is already installed and does not duplicate reports or evidence. The predictable passwords are for local development only.

Do not copy this database into production. Use a fresh production database and never enable `DEBUG` merely to run the demo seed.
