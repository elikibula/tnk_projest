# Mobile reporting forms

Phase 6 renders TNK report entry screens from the authorised section definitions returned by Django. Flutter does not maintain a second hard-coded field registry.

The bootstrap contract retains the original field-name list and adds compatible metadata derived from each real Django model field:

- field name and label;
- input type;
- whether the value is required;
- maximum text length;
- server-defined choice values;
- entry create/delete capabilities.

Flutter uses this metadata for text, numeric, choice, boolean and date controls. Relationship identifiers remain server-owned references and are not treated as free-standing mobile master data. Later bootstrap/reference enhancements can supply authorised selector options without changing the stored payload format.

## Local editing

An authorised cached server report is materialised as a user-scoped local working record when opened. Only `draft` and `returned_to_village` reports are editable. The repository independently enforces this rule; hiding a control is not the only protection.

Each repeatable entry receives a stable local UUID and stores:

- section and entry type;
- field values;
- owning user and local report;
- server UUID and record version when known;
- timestamps and sync state.

Fields autosave after a short debounce and show “Saved on device”. Local-only entries can be removed before sync. Server-backed entries are tombstoned as `pending_delete`; they are never physically deleted from local history before the server accepts the operation.

Phase 6 does not create official server reports, synchronize edits, validate official business rules, upload evidence, or change workflow state. Those operations remain in their later phases and require Django confirmation.
