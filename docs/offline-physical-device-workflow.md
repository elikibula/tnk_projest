# Offline physical-device workflow — R8

Date: 13 August 2026 (Pacific/Fiji)

Status: **BLOCKED AT PREREQUISITE — NO AUTHENTICATED STAGING SESSION**

## Device state

- Device: Samsung SM-A346E, connected and authorized through ADB
- Installed application: development debug package, version 1.0.0-development
- Visible state: online sign-in screen
- Local application database: not present
- Bootstrapped village/reporting data: not established
- Real staging API: unavailable
- Latest device recheck: Samsung serial `RFCW7123NDB` is connected and
  authorized; development package remains version `1.0.0-development`

Only non-sensitive file names and sizes were inspected. Secure-storage contents,
keys, tokens, passwords and application data were not read or exposed.

## Why the workflow cannot start

R8 requires a successful R7 session in this order:

1. Log in to the certificate-valid staging API.
2. Register the device and receive device-bound tokens.
3. Bootstrap the assigned fictional village and reference data.
4. Confirm the current reporting period and previous approved report.
5. Complete an initial synchronization.

The device currently displays “Sign in online to establish a secure session on
this device.” With no staging endpoint and no local database, disabling the
network would only prove that first-time login cannot occur offline. It would
not exercise the required offline reporting workflow.

## Supporting automated evidence

Flutter analysis was rerun during R8 preflight and reported no issues. The full
suite was also rerun and all 33 tests passed. Relevant tests cover:

- encrypted local database creation and wrong-key rejection;
- encrypted draft persistence across database restart;
- user-scoped cached data isolation;
- first bootstrap refusal while offline;
- cached bootstrap fallback after a prior online session;
- bounded offline authentication and expiry cleanup;
- offline report create/edit autosave without duplication;
- pending sync state and stable idempotency keys;
- validation failures remaining retryable;
- conflict preservation of both local and server values;
- encrypted evidence queue persistence, retry and deletion after upload.

These tests validate code behavior but do not replace airplane-mode,
process-kill, phone-restart, camera/GPS or reconnection testing on the physical
device.

## Physical checks not executed

- online bootstrap and initial sync;
- airplane-mode status indication;
- all 17 reporting sections and their entry types;
- evidence photo capture and protected pending file;
- GPS capture and permission behavior;
- process termination and application restart while offline;
- phone restart with an unsynced draft;
- local draft, evidence, queue and idempotency persistence after restart;
- reconnection upload and server/database comparison;
- partial batch failure;
- real server-side conflict creation and resolution;
- duplicate prevention and final synced status.

## Required continuation point

Complete R6 and R7 using an approved HTTPS staging deployment and fictional
user account. Reinstall a correctly configured staging APK, log in, bootstrap,
and sync while online. R8 can then begin by disabling all device network access
and following the controlled workflow checklist.

R9 backup/restore should not be treated as the next sequential pass while R8
is blocked, because later RC evidence must be tied to the same staging system
and release candidate.
