# Android debug build validation — R3

Date: 12 August 2026 (Pacific/Fiji)

Status: **APK BUILD PASS; R3B INSTALL/LAUNCH PARTIAL PASS**

## Build result

- Command: `flutter build apk --debug --flavor development --target=lib/main_development.dart --dart-define=TNK_APP_ENV=development`
- Flutter: 3.44.3 stable
- Gradle: 9.1.0
- Successful build duration: 461.5 seconds, including first-time CMake installation
- APK: `mobile/build/app/outputs/flutter-apk/app-development-debug.apk`
- Size: 169,722,444 bytes
- SHA-256: `4CC9EEFDE9697B7495E8DB0EA774A68ABF58E0B855CBE6E4A6648B99FEBE925E`
- Git commit: unavailable; this repository still has no commits

## Artifact verification

- Application ID: `fj.gov.tnk.tnk_insight_mobile.development`
- Version: `1.0.0-development` (`versionCode` 1)
- Minimum SDK: 24
- Target/compile SDK: 36
- Label: `TNK Insight Dev`
- Native ABIs: arm64-v8a, armeabi-v7a, x86_64
- APK signature verification: PASS using APK Signature Scheme v2
- Signer: standard Android debug certificate (not a release credential)
- Backup and full backup: disabled
- Android 12+ data-extraction rules: present
- Cleartext traffic: enabled in the debug overlay for local development only
- Main/staging/production manifest default: cleartext traffic disabled

## Defects fixed during native compilation

1. Enabled AGP 9 `resValues` generation for flavor-specific app labels.
2. Enabled AGP 9 `BuildConfig` generation for the existing
   `BuildConfig.FLAVOR` security branch in `MainActivity`; `FLAG_SECURE` was
   preserved.
3. Added the required debug-only manifest-merger declaration for local
   cleartext access. Staging and production were not weakened.
4. Reduced Gradle JVM limits and capped workers at two to fit the host's RAM.
5. A subsequently installed artifact had been compiled from the generic
   fail-closed entrypoint and threw a missing `TNK_APP_ENV` exception at
   startup. Performed a clean rebuild with the full `--target` option and an
   explicit `TNK_APP_ENV=development` defense-in-depth define. Verified the
   rebuilt cache references `main_development.dart`, then reinstalled it.

No database migration is involved. No signing key or secret was created.

## Remaining R3B gate

On 13 August 2026, the corrected APK was installed on a Samsung SM-A346E
running Android 16. Package/version verification, cold launch, absence of the
previous Dart exception, and accessibility-hierarchy rendering of the login
screen passed. Manual keyboard, navigation, rotation, lifecycle, local-draft
persistence and physical `FLAG_SECURE` checks remain NOT EXECUTED. See
`docs/android-physical-device-test.md`.

## Known warning

`flutter_image_compress_common` still applies the Kotlin Gradle Plugin. It
builds with the current Flutter release, but Flutter warns that a future
release will require migration to Built-in Kotlin. Track this as dependency
maintenance; it is not a failure of the current APK.
