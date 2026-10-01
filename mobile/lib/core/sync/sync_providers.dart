import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../auth/auth_failures.dart';
import '../auth/auth_providers.dart';
import '../database/database_providers.dart';
import 'sync_models.dart';
import 'sync_remote_data_source.dart';
import 'sync_repository.dart';
import '../../features/evidence/data/evidence_providers.dart';

final syncRemoteDataSourceProvider = Provider<SyncRemoteDataSource>(
  (ref) => DioSyncRemoteDataSource(ref.watch(authenticatedDioProvider)),
);
final syncRepositoryProvider = FutureProvider<SyncRepository>((ref) async {
  return SyncRepository(
    ref.watch(syncRemoteDataSourceProvider),
    await ref.watch(appDatabaseProvider.future),
  );
});

class SyncController extends AsyncNotifier<SyncResult?> {
  @override
  Future<SyncResult?> build() async => null;

  Future<void> synchronize() async {
    state = const AsyncLoading();
    try {
      final session = await ref
          .read(authControllerProvider.notifier)
          .ensureFreshSession();
      if (session.isOffline) throw const SyncNetworkFailure();
      final repository = await ref.read(syncRepositoryProvider.future);
      final evidenceRepository = await ref.read(
        evidenceRepositoryProvider.future,
      );
      final evidenceUploaded = await evidenceRepository.syncPending(session);
      final result = await repository.synchronize(session);
      state = AsyncData(
        SyncResult(
          uploaded: result.uploaded + evidenceUploaded,
          downloaded: result.downloaded,
          conflicts: result.conflicts,
          failed: result.failed,
        ),
      );
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

final syncControllerProvider =
    AsyncNotifierProvider<SyncController, SyncResult?>(SyncController.new);
