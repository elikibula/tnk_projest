import 'package:flutter_test/flutter_test.dart';
import 'package:tnk_insight_mobile/core/config/app_environment.dart';

void main() {
  test('environment configuration is centralized and safe by default', () {
    expect(AppEnvironment.development.apiBaseUrl, endsWith('/api/v1/'));
    expect(AppEnvironment.staging.apiBaseUrl, endsWith('/api/v1/'));
    expect(AppEnvironment.production.apiBaseUrl, endsWith('/api/v1/'));
    expect(AppEnvironment.production.enableDiagnosticLogging, isFalse);
    expect(AppEnvironment.production.enableCrashReporting, isFalse);
    expect(AppEnvironment.production.enableFutureAiFeatures, isFalse);
    expect(
      AppEnvironmentDetails.fromName('production'),
      AppEnvironment.production,
    );
    expect(
      () => AppEnvironmentDetails.fromName(''),
      throwsA(isA<StateError>()),
    );
    expect(() => AppEnvironment.staging.apiBaseUri, throwsA(isA<StateError>()));
    expect(
      () => AppEnvironment.production.apiBaseUri,
      throwsA(isA<StateError>()),
    );
  });
}
