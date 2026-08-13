# Historical master data

## Decision

TNK Insight preserves old quarterly reports with immutable report-specific master snapshots. The snapshots are captured when a report moves to `ready_for_validation`; reopening the report removes the freeze and the next ready transition recaptures the corrected state. Once the report is non-editable, snapshot rows cannot be changed or deleted through model saves, queryset deletion, or Django admin.

This is combined with effective-dated close-and-replace services for records whose identity changes over time. Persistent entities such as a business or IVDP project keep one identity and record lifecycle changes through movement/progress or audited service operations. This avoids duplicating the same entity every quarter while still making old reports reproducible.

## Model rules

| Model | Historical rule | Reason |
|---|---|---|
| `OfficialAppointment` | Close old `effective_to`, clear `is_current`, create replacement | The office holder is time-dependent and must never be overwritten. A change reason is mandatory. |
| `VillageCommittee` | Dissolve old committee and create replacement | A reconstituted committee is a new historical body. |
| `CommitteeMember` | Close old `left_date`, clear `is_active`, create replacement | Membership and office-holder changes are effective-dated. |
| `TraditionalTitleAppointment` | Close old `effective_to`, clear `is_current`, create replacement | The title holder is time-dependent. |
| `Household` | Close old `effective_to`, clear `is_active`, create replacement | Household composition/state shown as master data must remain historically resolvable. |
| `VillageAsset` | Deactivate old asset, create replacement and `AssetMovement` | A physically replaced asset is a different lifecycle record. |
| `VillageWaterSource` | Deactivate old source, create replacement and audit event | Replacement must preserve the retired source. |
| `VillageEnergyAsset` | Deactivate old asset, create replacement and audit event | Replacement must preserve the retired asset. |
| `VillageBusiness` | Retain identity; use an audited change service plus `BusinessMovement` | Ownership/status are lifecycle changes to the same registered business. The report snapshot freezes the state seen by each quarter. |
| `IVDPProject` | Retain identity; use audited master updates plus progress/milestone/risk history | Renaming or planning corrections do not create a new project. Quarterly report snapshots preserve presentation. |
| `TraditionalTitle` | Retain the title identity; title-holder changes use appointment replacement | The title is a continuing institution, while its appointments are historical. State changes use the audited culture service and report snapshots. |

The same report snapshot mechanism also freezes other master rows displayed by the 42 entry workflows, including village profile, people, sanitation facilities, finance accounts, preparedness records, evacuation centres, traditional units, and cultural knowledge.

## Service and permission rules

- Historical changes must go through the domain service layer, which locks the current row in a transaction.
- The actor must hold a report-author, provincial-administrator, or system-administrator role and be assigned to the affected village.
- A replacement date must be later than the predecessor's start date. The predecessor ends on the day before the replacement starts.
- Replacement and lifecycle services validate the resulting model and write an audit event. Infrastructure and business changes also write their existing movement records.
- Existing historical master rows are read-only and non-deletable in Django admin. Creation remains available to appropriately authorised administrators.
- Direct SQL and `QuerySet.update()` can bypass Django services; production database access must therefore remain restricted to application and trusted DBA accounts.

## Report resolution

For reports captured after this change, master rows are read from `ReportMasterSnapshot` whenever the report is not editable. Current database rows are never substituted into that historical display.

Reports created before the snapshot migration do not have captured rows. They use effective-date best-effort filtering for supported models so existing official reports remain viewable without inventing a backfill state. This compatibility path cannot reconstruct an in-place edit that occurred before history was recorded; such reports should be treated as legacy evidence and corrected only through the approved amendment mechanism planned for Phase E.

Snapshots are application-level immutability, not a database trigger. They are deliberately deleted and recaptured only while a report is reopened to an editable state. Approved, locked, and archived reports remain immutable.

## Verification scenarios

Regression tests cover:

- Q1 shows Official A after Official B is appointed in Q3;
- Q1 retains its committee, business, and project labels after later changes;
- appointment, committee member, traditional appointment, and household replacements close their predecessors;
- invalid replacement dates roll back without partial changes;
- infrastructure replacements retain inactive predecessors and asset movement history;
- frozen snapshot mutation and deletion are rejected;
- reopening and returning to ready recaptures corrected master state;
- Django admin treats existing audited master rows as read-only and non-deletable.
