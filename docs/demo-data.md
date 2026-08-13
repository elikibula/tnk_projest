# Fictional demonstration data

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
