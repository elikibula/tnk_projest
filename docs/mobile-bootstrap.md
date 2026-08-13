# Mobile bootstrap

After an authenticated session is established, Flutter refreshes an expiring access token and requests `GET /api/v1/sync/bootstrap/`. First bootstrap requires the API; the app never constructs an initial authoritative dataset locally.

The response is accepted only when:

- the envelope schema is version 1;
- the server does not require an application upgrade;
- the returned user UUID matches the authenticated local session;
- the payload has the required user, device, village, period, report, section, and workflow structures.

Accepted data replaces that user's existing reference and master-data cache in one Drift transaction. Villages, reports, user/device metadata and workflow capabilities are cached as server-owned master records. Reporting periods and section definitions are cached as reference records. Server time, schema version, sync cursor, and bootstrap completion time are stored as sync metadata.

If the API is unreachable, an existing cache belonging to the same user may be opened in offline mode. A first-time or different user receives a connectivity message instead. HTTP authentication/revocation failures are never converted into offline bootstrap success.

The bootstrap cache remains non-authoritative. Phase 5 does not implement delta changes, batch uploads, local report creation, or conflict resolution.
