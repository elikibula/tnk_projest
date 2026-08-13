# Django admin and assignment audit controls

Phase G date: 7 August 2026

## Access model

`is_staff` opens the Django admin shell but does not grant TNK data access. Active TNK role assignments remain authoritative.

| Role | Admin access |
|---|---|
| System Administrator | National access to scoped operational data and management of governed reference data and accounts. |
| Provincial Administrator | Read/change access only inside assigned Province, Tikina, or Village scope. Reference data is view-only. Cannot create users, grant System/Provincial Administrator roles, edit privileged accounts, or delete assignments. |
| Auditor | Read-only, location-scoped audit events. No general model administration. |
| Other role, even with Django model permissions | Denied by the TNK admin policy. |

Provincial administrators may manage existing non-privileged users in their scope and may deactivate assignments. New account creation remains national because creating a user and assigning a location are not one atomic admin operation. Province, Tikina, and Village creation is also national; provincial staff may work only with existing assigned locations.

Operational model querysets and related-object selectors are location-scoped. Direct object URLs are checked again, so a UUID or primary-key change does not bypass scope. Sensitive health, disability, safety, household, finance, and other detailed records are restricted to trusted System/Provincial Administrators. Evidence and generic document links remain central and read-only because their polymorphic location scope is too risky for generic admin editing.

Reports, workflow decisions, declarations, snapshots, amendments, quality issues, indicator values, exports, and audit records are read-only in admin where changing them would bypass their application services. Normal workflow and data entry remain in the TNK application.

## Assignment audit trail

Role and location assignment writes made through admin record:

- authenticated actor and timestamp;
- created, changed, or deleted action;
- previous and new values;
- request IP address and user agent;
- affected Province, Tikina, and Village where derivable.

Bulk deletion is removed. Request-aware admin writes suppress the anonymous signal duplicate. Direct ORM assignment changes still produce the earlier actor-null fallback event, so audit history is preserved even when no request exists.

Audit events are append-only through normal model and queryset operations: update and delete are rejected. Location foreign keys use `PROTECT`. Existing pre-Phase-G audit rows are retained with empty location scope because history cannot be reconstructed reliably; only national administrators can see those unscoped central events. This is application-layer protection, not a claim that a privileged database administrator or direct SQL cannot alter data.

## Admin usability

Registered models use concise identifiers, human-readable names, filters, safe search fields, relationship preloading, autocomplete selectors, and date navigation where the schema supports them. Sensitive narrative and personal fields are deliberately excluded from changelist columns and broad search. Lists are paginated at 50 rows to keep large government datasets usable.

## Verification boundary

Automated tests cover role denial despite global Django permissions, national and provincial visibility, related-field scoping, direct admin URLs, privileged-role grant prevention, sensitive list configuration, request metadata, audit location grain, and audit immutability. Production database roles, reverse-proxy IP handling, retention, and database-level tamper evidence remain deployment/governance responsibilities.
