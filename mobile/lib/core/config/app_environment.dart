import 'package:flutter_riverpod/flutter_riverpod.dart';

enum AppEnvironment { development, staging, production }

extension AppEnvironmentDetails on AppEnvironment {
  static AppEnvironment fromName(String value) => switch (value) {
    'development' => AppEnvironment.development,
    'staging' => AppEnvironment.staging,
    'production' => AppEnvironment.production,
    _ => throw StateError(
      'TNK_APP_ENV must be development, staging, or production.',
    ),
  };

  String get label => switch (this) {
    AppEnvironment.development => 'Development',
    AppEnvironment.staging => 'Staging',
    AppEnvironment.production => 'Production',
  };

  String get apiBaseUrl => switch (this) {
    AppEnvironment.development => const String.fromEnvironment(
      'TNK_DEVELOPMENT_API_URL',
      defaultValue: 'http://10.0.2.2:8000/api/v1/',
    ),
    AppEnvironment.staging => const String.fromEnvironment(
      'TNK_STAGING_API_URL',
      defaultValue: 'https://staging.invalid/api/v1/',
    ),
    AppEnvironment.production => const String.fromEnvironment(
      'TNK_PRODUCTION_API_URL',
      defaultValue: 'https://production.invalid/api/v1/',
    ),
  };

  bool get enableDiagnosticLogging => this != AppEnvironment.production;

  bool get enableCrashReporting => switch (this) {
    AppEnvironment.development => false,
    AppEnvironment.staging ||
    AppEnvironment.production => const bool.fromEnvironment(
      'TNK_ENABLE_CRASH_REPORTING',
      defaultValue: false,
    ),
  };

  bool get enableFutureAiFeatures =>
      const bool.fromEnvironment('TNK_ENABLE_AI_FEATURES', defaultValue: false);

  Duration get offlineSessionDuration => Duration(
    hours: const int.fromEnvironment(
      'TNK_OFFLINE_SESSION_HOURS',
      defaultValue: 72,
    ),
  );

  Uri get apiBaseUri {
    final uri = Uri.tryParse(apiBaseUrl);
    if (uri == null || !uri.hasScheme || !uri.hasAuthority) {
      throw StateError('The configured TNK API URL is invalid.');
    }
    if (this != AppEnvironment.development && uri.scheme != 'https') {
      throw StateError('Staging and production TNK APIs require HTTPS.');
    }
    if (this != AppEnvironment.development &&
        (uri.host.endsWith('.invalid') ||
            uri.host == 'localhost' ||
            uri.host == '127.0.0.1' ||
            uri.host == '::1' ||
            uri.host == '10.0.2.2')) {
      throw StateError(
        'Staging and production require a real, non-local HTTPS API host.',
      );
    }
    if (!uri.path.endsWith('/api/v1/')) {
      throw StateError('The configured TNK API URL must end with /api/v1/.');
    }
    return uri;
  }
}

final appEnvironmentProvider = Provider<AppEnvironment>((ref) {
  throw StateError('AppEnvironment must be supplied by bootstrap().');
});
