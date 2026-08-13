sealed class AppException implements Exception {
  const AppException(this.safeMessage);

  final String safeMessage;
}

final class ConfigurationException extends AppException {
  const ConfigurationException(super.safeMessage);
}
