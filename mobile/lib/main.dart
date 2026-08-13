import 'bootstrap.dart';
import 'core/config/app_environment.dart';

void main() {
  const configuredEnvironment = String.fromEnvironment('TNK_APP_ENV');
  bootstrap(AppEnvironmentDetails.fromName(configuredEnvironment));
}
