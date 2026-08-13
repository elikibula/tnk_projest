# Confidentiality and access control

## Enforcement model

TNK Insight combines three independent checks for every detailed access decision:

1. the user has an active recognised role;
2. the requested village is inside an active Province, Tikina, or Village assignment;
3. the role is explicitly allowed for the section and confidentiality level.

The central policy is implemented in `apps/core/security/confidentiality.py`. Templates may hide links for usability, but views, downloads, and exports call the server-side policy. Unknown roles, missing links, missing locations, and unknown confidentiality labels are denied by default.

## Levels

| Level | Examples | Rule |
|---|---|---|
| Public | Future approved publications | No public portal exists yet; authentication is still required. |
| Internal | Village profile and ordinary report summaries | Recognised role plus location and section scope. |
| Restricted | Named people, households, finance | Explicit detailed section role plus location scope. Excluded from ordinary analytical exports. |
| Highly restricted | Health, disability, community safety and protected evidence | Explicit section/evidence role plus location scope. Raw bulk export is always denied. |

The legacy value `confidential` is treated as `restricted`. Unknown values are also treated as restricted rather than public.

## Section matrix

| Role | Detailed report sections | Analytics | Ordinary summary export |
|---|---|---:|---:|
| System Administrator | All 17 | Yes | Yes |
| Provincial Administrator | All 17 in assigned scope | Yes | Yes |
| Roko Tui | All 17 in assigned scope | Yes | Yes |
| Roko Veivuke | All 17 in assigned scope | Yes | Yes |
| Mata ni Tikina | All 17 in assigned scope | Yes | Yes |
| Turaga ni Koro | All 17 for assigned village | Yes | Yes |
| Village Data Assistant | All 17 for assigned village | Yes | Yes |
| Village Nurse | Village profile, health, disability | Yes | Yes, aggregate only |
| Project Officer | Village profile, IVDP projects | Yes | Yes, aggregate only |
| Read-only Analyst | None; aggregate analytics only | Yes | Yes, aggregate only |
| Auditor | All 17 in assigned scope, read-only through existing workflow rules | Yes | Yes |
| No recognised active role | None | No | No |

Community-safety records are excluded from Village Nurse access even though they share the current Health page. This prevents safety details from being disclosed through a neighbouring entry group.

## Sensitive categories

| Category | Detailed access |
|---|---|
| Village master data | Roles with the relevant section and location assignment |
| Households | Full report roles only; Village Nurse, Project Officer and Analyst are denied |
| Health | Full report roles and Village Nurse; location scope required |
| Disability | Full report roles and Village Nurse; location scope required |
| Community safety | Full report roles only; location scope required |
| Finance | Full report roles with business/finance section access |
| Evidence | Document level, linked object, linked location, section role, and report status are all evaluated |
| Audit logs | System Administrators have national read-only access; Provincial Administrators and Auditors have location-scoped read-only access |
| Analytics | Recognised roles receive village-level aggregate summaries in their location scope |
| Exports | The same policy gates exports; current CSV/XLSX/PDF exports contain report summaries only |

Health and disability records are aggregate counts; the models do not store patient names. Analysts receive only the existing aggregate dashboard and report-summary exports and cannot open report, household, health, disability, safety, evidence, or data-entry URLs.

## Evidence rules

Evidence is never served directly by Nginx or a media URL. The protected download view evaluates the document confidentiality level and every linked content object.

- A document without a valid linked object is denied.
- Cross-village UUID manipulation is denied even when the role would otherwise qualify.
- Draft, returned, and ready-for-validation report evidence is limited to report authors and trusted administrators. Reviewers and auditors gain report-evidence access only after submission.
- A Village Nurse may access highly restricted evidence linked directly to an authorised health/disability record, but not generic report evidence or community-safety evidence.
- A Project Officer may access evidence only when it is directly linked to an authorised project record and its level is within project-officer clearance.
- Read-only Analysts cannot download evidence at any level.
- Every successful download retains the existing access audit event with actor, IP address, and user agent.

The Django admin for evidence is restricted to System Administrators and is read-only because generic-link location editing is not sufficiently safe for delegation. Highly restricted health, disability, and safety admin records are limited to System/Provincial Administrators and their assigned village scope.

## Export rules

All current analytical exports are aggregate report summaries. They include village, Tikina, province, period, status, completeness, and quality score only. They do not query or serialize people, household heads, health conditions, disability details, community-safety details, finance details, or evidence metadata. Raw export of a highly restricted record is denied by central policy for every role.

Future exports and API serializers must call `can_export_record()` or the equivalent batch policy and must not infer permission from dashboard visibility.

## Known boundary

The controls apply through Django views, forms, downloads, exports, and normal admin use. Trusted database administrators and direct SQL can bypass application policy, so production database and protected-storage credentials must remain tightly restricted. There are currently no application API serializers or autocomplete endpoints exposing these datasets.
