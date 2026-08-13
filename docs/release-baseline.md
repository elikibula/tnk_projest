# Release baseline — R1

Date: 12 August 2026 (Pacific/Fiji)

## Source state

- Repository branch: `master`
- Git commit: **unavailable — the repository has no commits yet**
- Working tree: all project files are untracked from Git's perspective
- Release implication: no build can currently be correlated to an immutable
  source revision. An reviewed initial commit is required before RC work.

## Toolchain baseline

| Component | Observed result |
| --- | --- |
| Operating system | Windows 11 Home 64-bit, 25H2 |
| Python | 3.13.3 |
| Django | 5.2 |
| Local PostgreSQL client | 18.0 |
| Container PostgreSQL target | PostgreSQL 17 Alpine |
| Flutter | 3.44.3 stable, revision `e1fd963c6f` |
| Flutter engine | `a4ce257c68` |
| Dart | 3.12.2 |
| Android Gradle Plugin | 9.0.1 |
| Gradle wrapper | 9.1.0 |
| Kotlin plugin | 2.3.20 |
| Java/JDK | Eclipse Temurin 17.0.19+10 configured for Flutter |
| Android SDK | PASS — installed at the per-user SDK path |
| Docker | **not installed or not discoverable** |
| Android device | none connected; R3B not executed |
| Flutter/Dart on PATH | no; workspace SDK works by absolute path |

The local PostgreSQL client and container target differ. This is not yet a
failure, but R5 must select and record one staging server version and validate
against it explicitly.

## Commands and results

| Check | Result |
| --- | --- |
| `python manage.py check` | PASS |
| `python manage.py check --deploy` using development settings | WARN: expected insecure-development settings plus OpenAPI warnings |
| `python manage.py check --deploy` using production settings and temporary non-secret baseline values | PASS WITH NOTES: six OpenAPI schema warnings |
| `makemigrations --check --dry-run` | PASS — no changes |
| `showmigrations` | PASS — all listed migrations applied to the local database |
| `migrate --plan` | PASS — no planned operations |
| `pytest -q` | PASS — 146 passed |
| `coverage run -m pytest -q` | PASS — 146 passed |
| `coverage report` | PASS — 93% total statement coverage (7,425 statements, 537 missed) |
| `ruff check .` from `backend` | PASS |
| `flutter --version` | PASS |
| `flutter doctor -v` | FAIL for Android toolchain; Windows desktop toolchain also unavailable |
| `dart analyze lib test` | PASS — no issues |
| `flutter test` | PASS — 33 passed |
| `dart format --output=none --set-exit-if-changed .` | PASS — 78 files unchanged |
| development-flavour debug APK build | PASS — artifact verified; see `android-debug-build.md` |

## Warnings and blockers

1. **BLOCKER for RC traceability:** Git has no initial commit.
2. **BLOCKER for R3B:** no authorized physical Android device is connected.
3. Docker is unavailable; R6 remains NOT EXECUTED.
4. The production deployment check reports six drf-spectacular schema warnings:
   unresolved method-field schemas and four APIViews without explicit response
   serializers. Runtime tests pass, but API documentation should be corrected
   before RC documentation is frozen.
5. Pytest cannot write its optional cache directory on this Windows workspace;
   test execution itself succeeds.
6. Visual Studio is absent. This blocks Windows desktop builds but is not an
   Android RC requirement.

No PostgreSQL staging, Docker/TLS, signing, device, backup/restore or UAT result
is claimed by this baseline.
