# Mobile offline database

Phase 4 establishes schema and encryption. Phase 5 transactionally populates the user-scoped cache from the authorised bootstrap endpoint. It does not implement delta synchronization or duplicate Django validation rules.

The Drift database contains:

- cached reference items, including server version and update timestamps;
- cached master records, including village and confidentiality scope;
- draft reports with local/server UUIDs and record versions;
- operational section records stored as versioned JSON payloads;
- pending attachment metadata and local encrypted-file queue references;
- sync cursor/metadata entries;
- explicit local/server conflict records.

Synchronisable tables record local and server identity, timestamps, record version, sync state, deletion state, conflict state, and safe sync errors. Supported states are `local_only`, `pending_create`, `pending_update`, `pending_delete`, `uploading`, `synced`, `conflict`, and `failed`.

All records are scoped by the authenticated user's UUID. Local UUIDs remain stable before server creation. Server UUIDs and `record_version` values are preserved for later optimistic-concurrency handling. Reference data and workflow state remain server-authoritative.

SQLite3 Multiple Ciphers encrypts the database at rest with a random 256-bit key stored separately in platform secure storage. Foreign keys, secure deletion, and WAL journaling are enabled when the database opens. Tokens, passwords, and encryption keys are never stored in database tables.

Schema version 1 is created through Drift's migration strategy. Every future schema change must increment `schemaVersion`, provide an explicit forward migration, and include upgrade/restart tests before release.
