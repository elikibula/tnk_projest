sealed class AuthFailure implements Exception {
  const AuthFailure(this.message);
  final String message;
}

final class InvalidCredentialsFailure extends AuthFailure {
  const InvalidCredentialsFailure()
    : super('The username or password is incorrect.');
}

final class AuthValidationFailure extends AuthFailure {
  const AuthValidationFailure(String detail)
    : super('Sign-in request was rejected: $detail');
}

final class SessionExpiredFailure extends AuthFailure {
  const SessionExpiredFailure()
    : super('Your session has expired. Please sign in again.');
}

final class DeviceRevokedFailure extends AuthFailure {
  const DeviceRevokedFailure()
    : super('This device is no longer authorised. Please contact support.');
}

final class UpgradeRequiredFailure extends AuthFailure {
  const UpgradeRequiredFailure()
    : super('This version is no longer supported. Please update the app.');
}

final class AuthNetworkFailure extends AuthFailure {
  const AuthNetworkFailure()
    : super('The TNK service could not be reached. Check your connection.');
}

final class UnexpectedAuthFailure extends AuthFailure {
  const UnexpectedAuthFailure()
    : super('Sign-in could not be completed. Please try again.');
}
