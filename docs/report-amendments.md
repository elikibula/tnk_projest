# Approved-report amendments

Phase E uses an immutable amendment overlay. An approved, locked, or archived `TNKReport` is never reopened, cloned, or overwritten. Its source records, workflow history, master snapshots, and stored `IndicatorValue` rows remain the signed historical evidence.

## Workflow

1. An assigned Turaga ni Koro, Village Data Assistant, provincial administrator, or system administrator creates a draft amendment and explains why it is required.
2. Each `ReportAmendmentChange` identifies one section, entry type, official record, and field. The service retrieves the original value from the report's immutable master snapshot or report-scoped source record; the requester cannot supply the original value.
3. Submission requires at least one correction and freezes the amendment and its changes.
4. An assigned Roko Tui or system administrator may approve or reject it. The requester cannot approve their own amendment, approval requires acknowledgement, and rejection requires a reason.
5. Approved corrections are displayed beside their preserved original values. Later approved amendments take precedence for the same report field and retain an explicit supersession link.

Statuses are `draft`, `submitted`, `approved`, `rejected`, and `withdrawn`. All workflow actions are recorded in the central audit log.

## Analytics

An amendment may optionally identify one affected active indicator. The service reads the original calculated village result and stores an amended value plus its numerator and denominator. Rate and average overrides must include a positive denominator, and the amended value must match the formula at four-decimal precision.

The original village `IndicatorValue` is not modified. Dashboard presentation applies the latest approved overlay. Tikina and province aggregation combines authoritative village numerators and denominators, so corrected rates are recomputed instead of averaged. Approval immediately rebuilds the affected report's Tikina and province aggregates.

## Security and immutability boundary

- Every read and workflow operation rechecks role and location scope in the server-side service/view.
- Submitted amendment models and their changes reject normal ORM save/delete/update operations, including stale in-memory parent objects.
- Django admin exposes amendment records as read-only evidence. Creation and transitions use the scoped browser workflow.
- The application-level boundary cannot prevent a database owner from issuing raw SQL. Production database privileges and audit/backup controls must preserve that trust boundary.

## User path

Open an approved report and select **View amendment history**. Create a request, then use the entry key, record ID, and field name shown on the relevant report section. Reviewers open the same amendment page to compare original and corrected values before approving or rejecting it.
