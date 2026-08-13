# Phase 2 - Reporting core

Implemented `ReportingPeriod`, `TNKReport`, and all 17 `ReportSectionStatus` records; open-period report creation; unique village/period enforcement; automatic latest approved/locked prior-report linkage; location-scoped list/detail pages; independent section progress saving; optimistic version protection; computed completeness; audit events; and approved/locked deletion protection.

## Commands

```powershell
python backend/manage.py makemigrations reporting
python backend/manage.py migrate
python backend/manage.py check
python backend/manage.py test tests -v 2
```

The reporting-period year range is configurable through `TNK_REPORTING_MIN_YEAR` and `TNK_REPORTING_MAX_YEAR`. Workflow transitions, validation blocking, reviewer actions, authorised revisions, and locking remain Phase 7 responsibilities; section domain records begin in Phase 3.
