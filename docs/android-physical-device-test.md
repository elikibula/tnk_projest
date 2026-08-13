# Android physical-device validation — R3B

Date: 13 August 2026 (Pacific/Fiji)

Status: **PARTIAL PASS — CORRECTED INSTALL, LAUNCH AND LOGIN RENDER VERIFIED**

## Device and build

- Manufacturer/model: Samsung SM-A346E
- Android: 16 (API 36)
- Physical display: 1080 × 2340, density 450 dpi
- Device serial: omitted from release documentation
- Package: `fj.gov.tnk.tnk_insight_mobile.development`
- Version: `1.0.0-development` (`versionCode` 1)
- Minimum/target SDK: 24 / 36
- APK: development debug build
- Installation method: `adb install -r`

## Executed checks

| Check | Result |
| --- | --- |
| Device visible and authorized through ADB | PASS |
| Streamed APK installation | PASS — Android package manager returned `Success` |
| Installed package and version | PASS |
| Launcher activity resolution | PASS |
| Explicit cold launch | PASS — Activity Manager returned `Status: ok` |
| App process remains alive after launch | PASS |
| Immediate fatal exception or ANR | PASS — none found in a clean launch log |
| Login interface rendered | PASS — accessibility hierarchy contains the app title, secure-session guidance and Sign in control |
| Background and resume | PASS — same process remained alive and returned to foreground |
| Device sleep and wake | PASS — same process remained alive and returned to foreground |
| Orientation-change process survival | PASS — no process restart, fatal exception or ANR |
| Visual rotation layout | NOT EXECUTED — requires manual observation |
| Keyboard and Android back behavior | NOT EXECUTED — Samsung notification shade retained input focus during ADB automation |

## Defect found and corrected

The first installed artifact started the generic `lib/main.dart` entrypoint
without `TNK_APP_ENV`. The device log showed an unhandled fail-closed
configuration exception, leaving no usable UI. A clean APK was rebuilt with:

```text
--target=lib/main_development.dart --dart-define=TNK_APP_ENV=development
```

The rebuilt metadata references `main_development.dart`. Reinstallation,
explicit launch and a clean device-log check passed, and the TNK login screen
is now the focused window.

## Still requiring manual observation

The following checks are **NOT YET EXECUTED** and must not be inferred from a
successful launch:

- login screen layout and text readability;
- keyboard behavior and Android back navigation;
- visual rotation layout;
- local draft persistence after app/process/device restart;
- screenshot/recent-task protection in staging or production builds.

No sensitive screenshots or device identifiers are retained in this report.
