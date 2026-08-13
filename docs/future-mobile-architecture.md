# Future mobile architecture (no mobile code in MVP)

```mermaid
flowchart LR
  F["Future Flutter client"] --> E["Encrypted Drift/SQLite"]
  E --> Q["Outbox + attachment queue"] --> A["Versioned REST API"] --> D["PostgreSQL"]
  A --> L["Sync log and idempotency store"]
  A -->|conflict| C["Server-approved conflict policy"] --> F
```

A later Flutter application should use encrypted local storage, secure token storage, batch synchronization, idempotency keys, partial-success results, retry with exponential backoff, durable sync logs and resumable attachment queues. Locked server records are read-only. Conflicts compare record versions and require explicit resolution for sensitive records. Mobile development remains deferred.
