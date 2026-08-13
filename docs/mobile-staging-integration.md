# Mobile-to-staging integration — R7

Date: 13 August 2026 (Pacific/Fiji)

Status: **PREFLIGHT PASS; LIVE INTEGRATION BLOCKED BY MISSING STAGING ENDPOINT**

## Environment

- Physical device: Samsung SM-A346E (`RFCW7123NDB`) connected and authorized
- Docker Desktop 4.86.0 and WSL 2.7.11: installed; newly enabled Virtual Machine
  Platform awaits Windows restart
- Docker/Compose staging stack: not yet started or exposed through an approved TLS proxy
- Real `TNK_STAGING_API_URL`: not supplied
- Default staging URL: `https://staging.invalid/api/v1/` (deliberately unusable)
- Certificate-valid staging hostname: unavailable
- PostgreSQL R5 rehearsal: passed separately; it was not exposed as a staging API

No localhost, emulator-loopback, cleartext, self-signed-certificate bypass or
disabled TLS verification was used as a substitute for staging.

## Preflight results

| Check | Result |
| --- | --- |
| Staging Dart entrypoint exists | PASS |
| Staging Android flavor exists | PASS |
| Staging manifest inherits cleartext denial | PASS by configuration |
| API base URL centralized | PASS |
| Staging/production require HTTPS | PASS |
| Placeholder `.invalid` hosts rejected | PASS after fix |
| Localhost, loopback and emulator host rejected outside development | PASS after fix |
| Custom certificate-validation bypasses | none found |
| Dart formatting | PASS — 78 files, no remaining changes |
| Flutter analysis | PASS — no issues |
| Flutter runtime tests | PASS — 33 passed |

## Defect fixed

Staging and production used deliberately reserved `.invalid` defaults, but
URL validation previously accepted those hosts because they were structurally
valid HTTPS URLs. This allowed an unusable staging build to start and fail only
when a request was attempted. Non-development configuration now rejects:

- reserved `.invalid` hosts;
- `localhost`;
- IPv4/IPv6 loopback;
- Android emulator development host `10.0.2.2`.

Regression tests confirm the default staging and production configurations
fail closed until real HTTPS endpoints are supplied.

## Live checks not executed

The following require a real certificate-valid staging API and fictional
staging credentials:

- health endpoint over HTTPS;
- valid and invalid login;
- device registration;
- token refresh and revocation;
- bootstrap/reference/master-data download;
- report and analytics download;
- server audit/log confirmation;
- logout and app restart;
- staging APK installation on the physical device;
- offline-session and server-side role/location-change behavior.

## Required inputs to continue

1. A reachable staging hostname with a publicly or organizationally trusted
   TLS certificate.
2. The exact URL ending in `/api/v1/`.
3. A deployed Django/PostgreSQL staging environment with fictional users.
4. Network access from the Samsung test device to that hostname.

Build only after those exist:

```powershell
flutter build apk --debug --flavor staging `
  --target=lib/main_staging.dart `
  --dart-define=TNK_APP_ENV=staging `
  --dart-define=TNK_STAGING_API_URL=https://<approved-host>/api/v1/
```

Do not embed passwords or tokens in Dart defines. R7 remains blocked until the
live requests above are executed and verified against server/database audit
records.
