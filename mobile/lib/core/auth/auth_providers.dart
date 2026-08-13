import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../api/api_client.dart';
import '../config/app_environment.dart';
import 'auth_failures.dart';
import 'auth_models.dart';
import 'auth_remote_data_source.dart';
import 'auth_repository.dart';
import 'installation_identity.dart';
import 'secure_session_store.dart';

final secureSessionStoreProvider = Provider<SecureSessionStore>(
  (ref) => PlatformSecureSessionStore(),
);
final installationIdentityProvider = Provider<InstallationIdentity>(
  (ref) => InstallationIdentity(ref.watch(secureSessionStoreProvider)),
);
final authRemoteDataSourceProvider = Provider<AuthRemoteDataSource>(
  (ref) => DioAuthRemoteDataSource(ref.watch(dioProvider)),
);
final authRepositoryProvider = Provider<AuthRepository>((ref) {
  final environment = ref.watch(appEnvironmentProvider);
  return AuthRepository(
    ref.watch(authRemoteDataSourceProvider),
    ref.watch(secureSessionStoreProvider),
    ref.watch(installationIdentityProvider),
    environment.offlineSessionDuration,
  );
});

class AuthController extends AsyncNotifier<AuthSession?> {
  @override
  Future<AuthSession?> build() => ref.watch(authRepositoryProvider).restore();

  Future<void> login(String username, String password) async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(
      () => ref.read(authRepositoryProvider).login(username, password),
    );
  }

  Future<void> logout() async {
    final session = state.value;
    if (session == null) return;
    state = const AsyncLoading();
    await ref.read(authRepositoryProvider).logout(session);
    state = const AsyncData(null);
  }

  Future<AuthSession> ensureFreshSession() async {
    final session = state.value;
    if (session == null) throw const SessionExpiredFailure();
    try {
      final refreshed = await ref
          .read(authRepositoryProvider)
          .ensureFreshSession(session);
      state = AsyncData(refreshed);
      return refreshed;
    } on Object catch (error, stackTrace) {
      state = AsyncError(error, stackTrace);
      rethrow;
    }
  }

  Future<void> invalidateSession() async {
    await ref.read(authRepositoryProvider).clearLocalSession();
    state = const AsyncData(null);
  }

  Future<void> retryRestore() async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(ref.read(authRepositoryProvider).restore);
  }
}

final authControllerProvider =
    AsyncNotifierProvider<AuthController, AuthSession?>(AuthController.new);
