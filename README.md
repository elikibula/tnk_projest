# TNK Insight

Turaga ni Koro Village Information, Monitoring and Decision Support Platform.

This standalone Django 5.2 and Flutter system provides secured identity/location scope, quarterly reporting, domain master/event/snapshot records, validation and approval workflow, protected evidence, indicators, dashboards, audited exports, offline-first mobile capture, synchronization, and deployment/backup operations.

The repository contains source code only. Python virtual environments, the Flutter SDK, build outputs, APKs, local databases, uploaded media, backup archives, signing material, and environment secrets are intentionally excluded.

## Local setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r backend/requirements/development.txt
Copy-Item .env.example .env
python backend/manage.py migrate
python backend/manage.py seed_reference_data
python backend/manage.py createsuperuser
python backend/manage.py runserver
```

To explore a complete fictional showcase instead of starting with empty screens:

```powershell
python backend/manage.py seed_demo_data --show-credentials
```

This development-only command creates three fictional villages, 14 role accounts, four reports in different workflow states, data for all 42 entry types, historical comparison, indicators and protected evidence. It is repeatable and will not duplicate the showcase. See [demo data](docs/demo-data.md) for the accounts and suggested walkthrough.

For a lightweight test run, the test settings use SQLite:

```powershell
pytest
```

## Mobile setup

Install Flutter separately, then from `mobile/` run `flutter pub get`. Development, staging, and production entry points are kept separate. Supply the API URL with the appropriate environment-specific Dart define; do not commit local IP addresses, passwords, tokens, or Android signing material.

The Django API must be reachable over HTTPS for staging and production mobile builds. Local physical-device testing may use a development LAN URL while Django is bound to the matching interface.

For the PostgreSQL stack:

```powershell
docker compose up --build
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

## First-use checklist

1. In `/admin/`, create the Province, Tikina and Village records.
2. Create a user, assign the **Turaga ni Koro** role, then add a location assignment. Choose one scope level and its matching location.
3. Create or open a quarterly reporting period.
4. Sign in as the village user, open **Reports**, create the draft and complete its section cards.
5. Upload supporting evidence, validate, acknowledge the declaration and submit.
6. Tikina and provincial users review, return or approve according to their assigned locations.

The language selector applies to navigation, report workflow, section screens, form labels, choices and help text. Draft iTaukei wording is maintained in `backend/locale/fj/LC_MESSAGES/django.po`; after editing it, run:

```powershell
python scripts/compile_po.py backend/locale/fj/LC_MESSAGES/django.po backend/locale/fj/LC_MESSAGES/django.mo
```

Alternatively, use the shorter Django command:

```powershell
python backend/manage.py compile_itaukei
```

Restart the Django development server after compiling because running Django processes cache translation catalogues. Text inside data-entry forms may also come from `backend/apps/reporting/itaukei.py`; edit that file when a label or choice does not have a corresponding `msgid` in `django.po`.

Frontend utility CSS is built locally rather than loaded from Tailwind's browser CDN. After changing utility classes in templates, run:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts\build-css.ps1
```

See [the data-entry guide](docs/tnk-data-entry.md), [architecture](docs/architecture.md), [workflow](docs/report-workflow.md), [testing](docs/testing.md), and [deployment](docs/deployment.md).
