import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/api/api_client.dart';
import '../../../core/database/database_providers.dart';
import 'dashboard_remote_data_source.dart';
import 'dashboard_repository.dart';

final dashboardRemoteProvider = Provider<DashboardRemoteDataSource>(
  (ref) => DioDashboardRemoteDataSource(ref.watch(dioProvider)),
);
final dashboardRepositoryProvider = FutureProvider<DashboardRepository>(
  (ref) async => DashboardRepository(
    await ref.watch(appDatabaseProvider.future),
    ref.watch(dashboardRemoteProvider),
  ),
);
final connectivityProvider = StreamProvider<bool>((ref) async* {
  bool connected(List<ConnectivityResult> values) =>
      values.any((value) => value != ConnectivityResult.none);
  final connectivity = Connectivity();
  yield connected(await connectivity.checkConnectivity());
  yield* connectivity.onConnectivityChanged.map(connected);
});
