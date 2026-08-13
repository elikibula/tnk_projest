# Mobile conflict resolution

Official TNK data never uses blind last-write-wins. Each batch item compares the submitted expected version with the current server `record_version`. A mismatch is returned in the batch `conflicts` collection with the safe server representation, submitted version and whether the server value is mandatory.

Distinct operational records with distinct UUIDs can normally coexist. Reference data, permissions, workflow state and approved/locked reports force the server value. Draft field conflicts require explicit resolution. Returned reports must be refreshed before correction. The future Flutter conflict screen may offer keep-server, use-local or manual edit only where the API says the action is permitted.

Models inheriting `UUIDTimeStampedModel` and `TNKReport` are already version-ready. Supporting records such as `ReportingPeriod`, `ReportSectionStatus`, `DataQualityIssue`, role assignments and evidence links need either version fields or parent-version/change-feed semantics before participating in delta writes.
