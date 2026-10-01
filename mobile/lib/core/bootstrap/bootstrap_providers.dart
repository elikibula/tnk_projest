import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../auth/auth_failures.dart';
import '../auth/auth_providers.dart';
import '../database/database_providers.dart';
import 'bootstrap_models.dart';
import 'bootstrap_remote_data_source.dart';
import 'bootstrap_repository.dart';

final bootstrapRemoteDataSourceProvider = Provider<BootstrapRemoteDataSource>(
  (ref) => DioBootstrapRemoteDataSource(ref.watch(authenticatedDioProvider)),
);

final bootstrapRepositoryProvider = FutureProvider<BootstrapRepository>((
  ref,
) async {
  return BootstrapRepository(
    ref.watch(bootstrapRemoteDataSourceProvider),
    await ref.watch(appDatabaseProvider.future),
  );
});

class BootstrapController extends AsyncNotifier<BootstrapSnapshot?> {
  @override
  Future<BootstrapSnapshot?> build() async => null;

  Future<void> load() async {
    state = const AsyncLoading();
    try {
      final session = await ref
          .read(authControllerProvider.notifier)
          .ensureFreshSession();
      final repository = await ref.read(bootstrapRepositoryProvider.future);
      state = AsyncData(await repository.load(session));
    } on SessionExpiredFailure catch (error, stackTrace) {
      await ref.read(authControllerProvider.notifier).invalidateSession();
      state = AsyncError(error, stackTrace);
    } on DeviceRevokedFailure catch (error, stackTrace) {
      await ref.read(authControllerProvider.notifier).invalidateSession();
      state = AsyncError(error, stackTrace);
    } on Object catch (error, stackTrace) {
      state = AsyncError(error, stackTrace);
    }
  }
}

final bootstrapControllerProvider =
    AsyncNotifierProvider<BootstrapController, BootstrapSnapshot?>(
      BootstrapController.new,
    );
