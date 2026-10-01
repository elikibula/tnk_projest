import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/auth/auth_providers.dart';
import 'exploration_repository.dart';
import 'photo_reports_repository.dart';

final explorationRepositoryProvider = Provider<ExplorationRepository>(
  (ref) => ExplorationRepository(ref.watch(authenticatedDioProvider)),
);

final photoReportsRepositoryProvider = Provider<PhotoReportsRepository>(
  (ref) => PhotoReportsRepository(ref.watch(authenticatedDioProvider)),
);
