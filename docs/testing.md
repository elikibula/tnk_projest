# Testing

From `backend`, run:

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
python -m pytest -q
python -m coverage run --source=apps -m pytest -q
python -m coverage report --skip-empty
python -m ruff check .
python -m pip check
```

The Phase I baseline is 120 passing tests and 88% application statement coverage. Tests cover identity and location scope, report creation and all 17 section statuses, the 42-form registry, historical data, confidentiality, amendments, finance/projects, data quality, workflow, indicators, exports, protected documents, admin, deployment controls, and audit events. `tests/test_final_acceptance.py` supplies the fictional multi-role, multi-location end-to-end acceptance scenario.

Before production release, repeat migrations, `check --deploy`, the guarded staging rehearsal, backup/restore, and restart persistence against PostgreSQL. Run the Docker/Nginx/TLS/volume rehearsal on the actual staging host; lightweight local tests do not replace those checks. See `docs/final-readiness-audit.md`.
