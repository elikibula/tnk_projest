import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/database/database_providers.dart';
import 'reporting_repository.dart';

final reportingRepositoryProvider = FutureProvider<ReportingRepository>((
  ref,
) async {
  return ReportingRepository(await ref.watch(appDatabaseProvider.future));
});
