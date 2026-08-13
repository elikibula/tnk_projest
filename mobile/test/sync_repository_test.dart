import 'dart:convert';

import 'package:drift/drift.dart' hide isNotNull;
import 'package:drift/native.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:tnk_insight_mobile/core/auth/auth_models.dart';
import 'package:tnk_insight_mobile/core/database/app_database.dart';
import 'package:tnk_insight_mobile/core/database/sync_status.dart';
import 'package:tnk_insight_mobile/core/sync/sync_remote_data_source.dart';
import 'package:tnk_insight_mobile/core/sync/sync_repository.dart';

void main() {
  test('accepted upload becomes synced and stores cursor and log', () async {
    final database = AppDatabase(NativeDatabase.memory());
    addTearDown(database.close);
    final now = DateTime.utc(2026, 8, 11, 10);
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
            syncStatus: SyncStatus.pendingUpdate.value,
            createdAt: now,
            updatedAt: now,
          ),
        );
    await database
        .into(database.operationalRecords)
        .insert(
          OperationalRecordsCompanion.insert(
            localUuid: 'entry-local',
            ownerUserUuid: 'user-1',
            resourceType: 'population',
            reportLocalUuid: 'report-local',
            payloadJson: jsonEncode({
              'section_code': 'population_households',
              'values': {'count': 10},
            }),
            syncStatus: SyncStatus.pendingCreate.value,
            createdAt: now,
            updatedAt: now,
          ),
        );
    final remote = AcceptingSyncRemote(now);
    final repository = SyncRepository(remote, database, clock: () => now);

    final result = await repository.synchronize(_session());

    final entry = await database
        .select(database.operationalRecords)
        .getSingle();
    expect(result.uploaded, 1);
    expect(entry.syncStatus, SyncStatus.synced.value);
    expect(entry.serverUuid, 'entry-local');
    expect(entry.idempotencyKey, isNotNull);
    expect(
      await database
          .select(database.localSyncLogs)
          .getSingle()
          .then((log) => log.status),
      'completed',
    );
    expect(remote.uploaded.single['idempotency_key'], entry.idempotencyKey);
    expect(remote.downloadCursors, [null, 'cursor-page-1']);
  });

  test(
    'server validation failure remains retryable with stable idempotency',
    () async {
      final database = AppDatabase(NativeDatabase.memory());
      addTearDown(database.close);
      final now = DateTime.utc(2026, 8, 11, 10);
      await _seedRecord(database, now);
      final remote = RetrySyncRemote(now);
      final repository = SyncRepository(remote, database, clock: () => now);

      final first = await repository.synchronize(_session());
      final failed = await database
          .select(database.operationalRecords)
          .getSingle();
      expect(first.failed, 1);
      expect(failed.syncStatus, SyncStatus.failed.value);
      expect(failed.syncError, 'validation_error');
      final idempotency = failed.idempotencyKey;

      final second = await repository.synchronize(_session());
      final accepted = await database
          .select(database.operationalRecords)
          .getSingle();
      expect(second.uploaded, 1);
      expect(accepted.syncStatus, SyncStatus.synced.value);
      expect(accepted.idempotencyKey, idempotency);
      expect(remote.keys.toSet(), {idempotency});
    },
  );

  test('conflict produces a partial log and preserves both values', () async {
    final database = AppDatabase(NativeDatabase.memory());
    addTearDown(database.close);
    final now = DateTime.utc(2026, 8, 11, 10);
    await _seedRecord(database, now, serverUuid: 'entry-server');
    final repository = SyncRepository(
      ConflictSyncRemote(now),
      database,
      clock: () => now,
    );

    final result = await repository.synchronize(_session());

    expect(result.conflicts, 1);
    expect(
      (await database.select(database.localSyncLogs).getSingle()).status,
      'partial',
    );
    final conflict = await database
        .select(database.conflictRecords)
        .getSingle();
    expect(jsonDecode(conflict.localPayloadJson)['values']['count'], 10);
    expect(jsonDecode(conflict.serverPayloadJson)['values']['count'], 12);
    expect(
      (await database.select(database.operationalRecords).getSingle())
          .syncStatus,
      SyncStatus.conflict.value,
    );
  });
}

Future<void> _seedRecord(
  AppDatabase database,
  DateTime now, {
  String? serverUuid,
}) async {
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
      .into(database.operationalRecords)
      .insert(
        OperationalRecordsCompanion.insert(
          localUuid: 'entry-local',
          ownerUserUuid: 'user-1',
          serverUuid: Value(serverUuid),
          resourceType: 'population',
          reportLocalUuid: 'report-local',
          payloadJson: jsonEncode({
            'section_code': 'population_households',
            'values': {'count': 10},
          }),
          syncStatus: SyncStatus.pendingCreate.value,
          createdAt: now,
          updatedAt: now,
        ),
      );
}

AuthSession _session() => AuthSession(
  user: const AuthUser(
    uuid: 'user-1',
    username: 'user',
    fullName: 'User',
    preferredLanguage: 'en',
    roles: ['turaga_ni_koro'],
  ),
  tokens: const AuthTokens(
    accessToken: 'access',
    refreshToken: 'refresh',
    deviceUuid: 'device',
  ),
  establishedAt: DateTime.utc(2026, 8, 11),
  offlineValidUntil: DateTime.utc(2026, 8, 14),
);

class AcceptingSyncRemote implements SyncRemoteDataSource {
  AcceptingSyncRemote(this.now);
  final DateTime now;
  List<Map<String, dynamic>> uploaded = [];
  final List<String?> downloadCursors = [];

  @override
  Future<SyncBatchResponse> upload(
    String accessToken,
    List<Map<String, dynamic>> changes,
  ) async {
    uploaded = changes;
    return SyncBatchResponse(
      [
        {
          'status': 'accepted',
          'local_uuid': 'entry-local',
          'record': {
            'server_uuid': 'entry-local',
            'record_version': 1,
            'server_updated_at': now.toIso8601String(),
          },
        },
      ],
      const [],
      const [],
    );
  }

  @override
  Future<SyncChangesResponse> download(
    String accessToken,
    String? cursor,
  ) async {
    downloadCursors.add(cursor);
    return cursor == null
        ? const SyncChangesResponse('cursor-page-1', [], [], hasMore: true)
        : const SyncChangesResponse('cursor-final', [], []);
  }
}

class RetrySyncRemote implements SyncRemoteDataSource {
  RetrySyncRemote(this.now);
  final DateTime now;
  var attempts = 0;
  final keys = <String?>[];
  @override
  Future<SyncBatchResponse> upload(
    String accessToken,
    List<Map<String, dynamic>> changes,
  ) async {
    attempts++;
    keys.add(changes.single['idempotency_key'] as String?);
    if (attempts == 1) {
      return const SyncBatchResponse([], [], [
        {'local_uuid': 'entry-local', 'code': 'validation_error'},
      ]);
    }
    return SyncBatchResponse(
      [
        {
          'status': 'accepted',
          'local_uuid': 'entry-local',
          'record': {
            'server_uuid': 'entry-server',
            'record_version': 1,
            'server_updated_at': now.toIso8601String(),
          },
        },
      ],
      const [],
      const [],
    );
  }

  @override
  Future<SyncChangesResponse> download(
    String accessToken,
    String? cursor,
  ) async => const SyncChangesResponse('cursor', [], []);
}

class ConflictSyncRemote implements SyncRemoteDataSource {
  ConflictSyncRemote(this.now);
  final DateTime now;
  @override
  Future<SyncBatchResponse> upload(
    String accessToken,
    List<Map<String, dynamic>> changes,
  ) async => SyncBatchResponse(const [], [
    {
      'local_uuid': 'entry-local',
      'server': {
        'values': {'count': 12},
        'record_version': 2,
      },
    },
  ], const []);
  @override
  Future<SyncChangesResponse> download(
    String accessToken,
    String? cursor,
  ) async => const SyncChangesResponse('cursor', [], []);
}
