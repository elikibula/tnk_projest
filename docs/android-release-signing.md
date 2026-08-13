# Android release signing — R4

Date: 13 August 2026 (Pacific/Fiji)

Status: **CONFIGURATION PREPARED; SIGNED ARTIFACT BLOCKED BY KEY CUSTODY AND RELEASE ENDPOINT**

## Implemented controls

- Release signing values are read only from process environment variables.
- Release artifact tasks fail closed when any signing value is absent.
- Debug builds remain independent of release credentials.
- `.gitignore` excludes JKS, keystore and local signing-property files.
- No keystore, private key, password or signing property file was created or
  committed by this phase.

Required variables:

- `TNK_ANDROID_KEYSTORE_PATH`
- `TNK_ANDROID_KEYSTORE_PASSWORD`
- `TNK_ANDROID_KEY_ALIAS`
- `TNK_ANDROID_KEY_PASSWORD`

Secrets should be injected by the protected release pipeline or a dedicated
secret manager. Do not place them in Flutter source, Gradle source, Git,
documentation, screenshots or shared logs.

## Upload key creation

Create the upload key interactively in a protected location outside the
repository. The command intentionally prompts for secrets:

```powershell
keytool -genkeypair -v `
  -keystore '<protected-path>\tnk-insight-upload.jks' `
  -alias 'tnk-insight-upload' `
  -keyalg RSA -keysize 4096 -validity 10000
```

Back up the keystore and recovery information using the organization's
approved secrets and disaster-recovery process. Loss of an upload/signing key
can prevent future application updates.

## Release build commands

After protected variables and the approved HTTPS endpoint are supplied:

```powershell
flutter build apk --release --flavor production `
  --target=lib/main_production.dart `
  --dart-define=TNK_APP_ENV=production `
  --dart-define=TNK_PRODUCTION_API_URL=https://<approved-host>/api/v1/

flutter build appbundle --release --flavor production `
  --target=lib/main_production.dart `
  --dart-define=TNK_APP_ENV=production `
  --dart-define=TNK_PRODUCTION_API_URL=https://<approved-host>/api/v1/
```

Verify final APK signatures with `apksigner verify --verbose --print-certs`.
Record only public certificate fingerprints, artifact sizes and SHA-256
checksums.

## Outstanding release inputs

1. Approved custodian and protected location for the upload keystore.
2. Keystore/key secrets delivered through an approved secret channel.
3. Approved production or staging HTTPS API hostname.
4. RC version and build number after earlier external gates pass.

No signed APK/AAB result is claimed until those inputs exist and both artifacts
are actually built and verified.
