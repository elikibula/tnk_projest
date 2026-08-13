import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/api/api_client.dart';
import '../../../core/database/database_providers.dart';
import 'evidence_cipher.dart';
import 'evidence_remote_data_source.dart';
import 'evidence_repository.dart';

final evidenceRemoteProvider = Provider<EvidenceRemoteDataSource>(
  (ref) => DioEvidenceRemoteDataSource(ref.watch(dioProvider)),
);
final evidenceCipherProvider = Provider<EvidenceCipher>(
  (ref) => EvidenceCipher(),
);
final evidenceRepositoryProvider = FutureProvider<EvidenceRepository>(
  (ref) async => EvidenceRepository(
    await ref.watch(appDatabaseProvider.future),
    ref.watch(evidenceRemoteProvider),
    ref.watch(evidenceCipherProvider),
  ),
);
