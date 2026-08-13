import 'dart:io';

import 'package:drift/drift.dart';
import 'package:drift/native.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:tnk_insight_mobile/core/auth/auth_models.dart';
import 'package:tnk_insight_mobile/core/database/app_database.dart';
import 'package:tnk_insight_mobile/core/database/sync_status.dart';
import 'package:tnk_insight_mobile/core/security/database_key_store.dart';
import 'package:tnk_insight_mobile/features/evidence/data/evidence_cipher.dart';
import 'package:tnk_insight_mobile/features/evidence/data/evidence_remote_data_source.dart';
import 'package:tnk_insight_mobile/features/evidence/data/evidence_repository.dart';

void main() {
  test('transient evidence failure retries with stable idempotency', () async {
    final database = AppDatabase(NativeDatabase.memory());
    addTearDown(database.close);
    final directory = await Directory.systemTemp.createTemp(
      'tnk-evidence-retry-',
    );
    addTearDown(() => directory.delete(recursive: true));
    final encrypted = File(
      '${directory.path}${Platform.pathSeparator}photo.enc',
    );
    final cipher = EvidenceCipher(storage: MemorySecureStore());
    await cipher.encryptToFile([1, 2, 3, 4], encrypted);
    final now = DateTime.utc(2026, 8, 12);
    await database
        .into(database.draftReports)
        .insert(
          DraftReportsCompanion.insert(
            localUuid: 'report-local',
            ownerUserUuid: 'user-1',
            serverUuid: const Value('report-server'),
            villageUuid: 'village-a1',
            reportingPeriodUuid: 'period-q2',
            payloadJson: '{"status":"draft"}',
            syncStatus: SyncStatus.synced.value,
            createdAt: now,
            updatedAt: now,
          ),
        );
    await database
        .into(database.pendingAttachments)
        .insert(
          PendingAttachmentsCompanion.insert(
            localUuid: 'evidence-local',
            ownerUserUuid: 'user-1',
            reportLocalUuid: 'report-local',
            localPath: encrypted.path,
            mediaType: 'image/jpeg',
            checksumSha256: 'checksum',
            byteSize: 4,
            syncStatus: SyncStatus.pendingCreate.value,
            createdAt: now,
            updatedAt: now,
            metadataJson: const Value('{"filename":"photo.jpg"}'),
            idempotencyKey: const Value('evidence-idempotency'),
          ),
        );
    final remote = RetryEvidenceRemote();
    final repository = EvidenceRepository(database, remote, cipher);

    expect(await repository.syncPending(_session()), 0);
    final failed = await database
        .select(database.pendingAttachments)
        .getSingle();
    expect(failed.syncStatus, SyncStatus.failed.value);
    expect(failed.retryCount, 1);
    expect(await encrypted.exists(), isTrue);

    expect(await repository.syncPending(_session()), 1);
    final synced = await database
        .select(database.pendingAttachments)
        .getSingle();
    expect(synced.syncStatus, SyncStatus.synced.value);
    expect(remote.idempotencyKeys, [
      'evidence-idempotency',
      'evidence-idempotency',
    ]);
    expect(await encrypted.exists(), isFalse);
  });
}

AuthSession _session() => AuthSession(
  user: const AuthUser(
    uuid: 'user-1',
    username: 'tnk-a1',
    fullName: 'Turaga ni Koro A1',
    preferredLanguage: 'en',
    roles: ['turaga_ni_koro'],
  ),
  tokens: const AuthTokens(
    accessToken: 'access',
    refreshToken: 'refresh',
    deviceUuid: 'device',
  ),
  establishedAt: DateTime.utc(2026, 8, 12),
  offlineValidUntil: DateTime.utc(2026, 8, 15),
);

class RetryEvidenceRemote implements EvidenceRemoteDataSource {
  var attempts = 0;
  final idempotencyKeys = <String>[];
  @override
  Future<Map<String, dynamic>> upload({
    required String token,
    required String reportUuid,
    required String idempotencyKey,
    required String filename,
    required String mediaType,
    required List<int> bytes,
    required Map<String, dynamic> metadata,
  }) async {
    attempts++;
    idempotencyKeys.add(idempotencyKey);
    if (attempts == 1) throw const EvidenceUploadFailure(permanent: false);
    return {'uuid': 'evidence-server'};
  }
}

class MemorySecureStore implements SecureValueStore {
  final values = <String, String>{};
  @override
  Future<String?> read(String key) async => values[key];
  @override
  Future<void> write(String key, String value) async => values[key] = value;
}
