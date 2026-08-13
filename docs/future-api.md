# Future API boundary

Planned versioned resources include authentication, assigned locations, periods, reports, sections, snapshots, movements, evidence upload sessions, validation and workflow actions. Commands call existing services rather than duplicating rules in serializers. Mutations require idempotency keys and expected record versions; locked records reject writes. Pagination, field-level confidentiality, audit correlation IDs and scoped attachment URLs are mandatory.
