import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/api/api_client.dart';
import '../../../core/database/database_providers.dart';
import 'validation_remote_data_source.dart';
import 'validation_repository.dart';

final validationRemoteProvider = Provider<ValidationRemoteDataSource>(
  (ref) => DioValidationRemoteDataSource(ref.watch(dioProvider)),
);
final validationRepositoryProvider = FutureProvider<ValidationRepository>(
  (ref) async => ValidationRepository(
    await ref.watch(appDatabaseProvider.future),
    ref.watch(validationRemoteProvider),
  ),
);
