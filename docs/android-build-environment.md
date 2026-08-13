# Android build environment — R2

Status on 12 August 2026: **PASS FOR ANDROID DEVELOPMENT**

## Verified post-install environment

- Android SDK: `C:\Users\5888\AppData\Local\Android\Sdk`
- Android SDK platform: API 37 installed; API 36 used by the app build
- Android Build Tools: 36.0.0
- Android Emulator: 37.1.11 installed (no emulator test claimed)
- Android NDK: 28.2.13676358
- CMake: 3.22.1
- Flutter/Dart: 3.44.3 / 3.12.2
- Gradle/AGP/Kotlin: 9.1.0 / 9.0.1 / 2.3.20
- Effective JDK: Eclipse Temurin 17.0.19+10
- Android licences: accepted
- `flutter doctor -v`: Android toolchain PASS

No physical Android device is connected, so R3B remains NOT EXECUTED. The
Visual Studio doctor warning affects Windows desktop development only.

The JDK trust store could not validate the Gradle TLS chain on this Windows
host. Builds succeeded without disabling TLS verification by setting
`GRADLE_OPTS` and `JAVA_TOOL_OPTIONS` to
`-Djavax.net.ssl.trustStoreType=Windows-ROOT`. The wrapper is configured with
the official HTTPS Gradle distribution URL; no machine-specific distribution
path is retained in project configuration.

The remaining content below records the original, now-resolved R2 blocker and
the installation procedure used.

Flutter doctor reports `Unable to locate Android SDK`. Inspection confirmed:

- `C:\Users\5888\AppData\Local\Android\Sdk` does not exist.
- Android Studio is not installed under `C:\Program Files\Android`.
- no `ANDROID_HOME` or `ANDROID_SDK_ROOT` is configured;
- `java`, `sdkmanager` and Android Studio's bundled JDK are unavailable;
- a standalone `C:\windows\adb.exe` exists, but this is not an Android SDK;
- no Android device appears in Flutter doctor;
- the debug development-flavour APK build fails before Gradle with
  `No Android SDK found`.

## Required installation

Use the current stable Android Studio installer from the official Android
developer site. During setup install:

1. Android Studio with its bundled JetBrains Runtime/JDK.
2. Android SDK Platform matching the project's Flutter/compile SDK requirement
   shown by `flutter doctor` after installation (do not guess or downgrade it).
3. Latest compatible Android SDK Build-Tools.
4. Android SDK Command-line Tools (latest).
5. Android SDK Platform-Tools.
6. Android Emulator and one system image only if emulator testing is desired;
   a physical device can satisfy R3B instead.

The expected default per-user SDK path is:

```text
C:\Users\5888\AppData\Local\Android\Sdk
```

Use the actual path displayed by Android Studio's SDK Manager if it differs.

## Configuration after installation

In a new PowerShell session, substitute the actual SDK path:

```powershell
$androidSdk = 'C:\Users\5888\AppData\Local\Android\Sdk'
Test-Path $androidSdk
& 'C:\Users\5888\Desktop\Django Sites\tnk_project\tmp\flutter-sdk\flutter\bin\flutter.bat' config --android-sdk $androidSdk
& 'C:\Users\5888\Desktop\Django Sites\tnk_project\tmp\flutter-sdk\flutter\bin\flutter.bat' doctor --android-licenses
& 'C:\Users\5888\Desktop\Django Sites\tnk_project\tmp\flutter-sdk\flutter\bin\flutter.bat' doctor -v
```

`Test-Path` must return `True` before configuring Flutter. Review and accept
licenses interactively; do not script blind acceptance. Android Studio's
bundled JDK is preferred. If Flutter cannot locate it, configure the actual JDK
directory with `flutter config --jdk-dir`, then rerun doctor.

Useful persistent environment variables, if organizational tooling requires
them, are `ANDROID_HOME` pointing to the SDK and a `PATH` entry for
`platform-tools`. `ANDROID_SDK_ROOT` is deprecated by current Android tooling;
avoid defining conflicting SDK locations.

## Project versions observed

- Flutter 3.44.3 / Dart 3.12.2
- Android Gradle Plugin 9.0.1
- Gradle 9.1.0
- Kotlin 2.3.20
- Android minimum SDK 24 (current Flutter 3.44 default, confirmed in the APK)
- Java source/target compatibility 17

Use Android Studio's bundled supported JDK; do not install an obsolete Java 8
runtime. Confirm the effective Java version in the successful post-install
`flutter doctor -v` output.

## Required verification sequence

After Android doctor passes:

```powershell
cd 'C:\Users\5888\Desktop\Django Sites\tnk_project\mobile'
flutter clean
flutter pub get
flutter analyze
flutter test
flutter build apk --debug --flavor development --target=lib/main_development.dart --dart-define=TNK_APP_ENV=development
```

Then verify the APK exists under `build\app\outputs\flutter-apk`, record its
size and checksum, and run `adb devices` with an authorized physical device.

## Current result

- SDK location: PASS
- SDK platform/build tools: PASS
- Java version: PASS (17.0.19+10)
- Android licences: PASS
- Android toolchain: PASS
- Development APK: PASS; see `docs/android-debug-build.md`
- Physical Android device: NOT CONNECTED

Production signing remains a separate R4 gate.
