sealed class BootstrapFailure implements Exception {
  const BootstrapFailure(this.message);
  final String message;
}

final class BootstrapNetworkFailure extends BootstrapFailure {
  const BootstrapNetworkFailure()
    : super('Initial data could not be downloaded. Check your connection.');
}

final class BootstrapUnavailableOfflineFailure extends BootstrapFailure {
  const BootstrapUnavailableOfflineFailure()
    : super(
        'Connect to the TNK service to download this device’s initial data.',
      );
}

final class BootstrapUpgradeRequiredFailure extends BootstrapFailure {
  const BootstrapUpgradeRequiredFailure()
    : super('This version cannot safely load TNK data. Please update the app.');
}

final class BootstrapUnexpectedFailure extends BootstrapFailure {
  const BootstrapUnexpectedFailure()
    : super('TNK data could not be prepared. Please try again.');
}
