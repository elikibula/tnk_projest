# Mobile evidence, camera, and GPS

Phase 8 keeps evidence uploads separate from JSON record batches. An editable, authorised report accepts multipart uploads at `POST /api/v1/reports/{report_uuid}/evidence/`; `GET` returns metadata filtered by the existing location, role, and confidentiality policy.

Each queued item receives a client UUID used as its `Idempotency-Key` and server evidence UUID. The server validates the extension, file signature, configured size limit, GPS ranges, report scope, and editability before linking it to the existing `EvidenceDocument` domain model. Repeating the same file and key returns the original response; reusing the key with different content returns a conflict.

On the device, camera photos, gallery images, PDF, DOCX, and XLSX files can be queued offline. Images over 1 MiB may be resized to at most 2048 px at 85% quality; the screen tells the user and allows compression to be disabled. Queue files are AES-256-GCM encrypted with a distinct key held in platform secure storage. Decrypted bytes exist only in memory for upload. The encrypted file is deleted only after server confirmation.

GPS is optional. The app does not request location permission until the user taps **Capture GPS**, captures one position with accuracy and timestamp, and never starts continuous tracking. Denial does not block evidence capture.

Failed uploads remain independent of report record synchronization. They retry on later manual synchronization up to four attempts and expose a safe failure message without logging evidence content.
