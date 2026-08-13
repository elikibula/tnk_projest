# Phase 13: mobile release readiness

Status: **ready for controlled staging; production remains conditional on the
external gates below.**

## Implemented release controls

- Development, staging and production Dart entrypoints and Android product
  flavours use separate identities and centralized API configuration.
- Staging and production reject cleartext or malformed API URLs. Placeholder
  hosts intentionally fail closed until the release pipeline supplies a URL.
- Application version and build number are registered at login. Django returns
  minimum/latest versions and blocks login/bootstrap when an unsafe version or
  sync schema is detected.
- Diagnostic logging is disabled in production. Crash reporting and future AI
  entrypoints are disabled-by-default compile-time feature flags; no reporting
  DSN, API key or production secret is embedded in the APK.
- Android backup, cloud extraction and device transfer are disabled. Staging
  and production use screenshot/recent-task protection and deny cleartext.
- Production signing material is deliberately absent from source control.

## Required staging gates

1. Supply the certificate-valid staging API URL and build the staging flavour.
2. Run the complete realistic workflow against the actual PostgreSQL staging
   backend, including a second-village denial and conflict resolution.
3. Exercise offline restart, evidence capture, permission revocation, token
   expiry, returned correction and resubmission on representative Android and
   iOS devices under limited connectivity.
4. Verify Android screenshot, recent-task, backup and device-transfer controls.
5. On macOS, create/validate distinct signed iOS schemes and verify Keychain,
   file protection and backup behavior on a physical device.
6. Configure a privacy-reviewed crash-reporting provider if the compile-time
   flag is enabled. Confirm payload scrubbing before enabling production.
7. Complete accessibility checks with TalkBack/VoiceOver, 200% text, keyboard,
   contrast measurement and the supported phone/tablet sizes.
8. Perform the existing Django Docker/Nginx/TLS, backup/restore, monitoring and
   volume rehearsal on the staging host.
9. Obtain accountable privacy, records-management, security and product-owner
   approval. Record rollback owner, support contacts and minimum version.

## Build examples

```powershell
flutter build apk --flavor staging -t lib/main_staging.dart `
  --dart-define=TNK_STAGING_API_URL=https://staging.example.gov.fj/api/v1/

flutter build appbundle --release --flavor production `
  -t lib/main_production.dart `
  --dart-define=TNK_PRODUCTION_API_URL=https://example.gov.fj/api/v1/
```

Do not enable crash reporting or future AI flags merely to create a build.
Future AI capabilities must remain server-side, permission-scoped and unable to
silently modify official records.
