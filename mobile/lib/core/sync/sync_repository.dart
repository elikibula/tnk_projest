import 'dart:convert';

import 'package:drift/drift.dart';
import 'package:uuid/uuid.dart';

import '../auth/auth_models.dart';
import '../database/app_database.dart';
import '../database/sync_status.dart';
import 'sync_models.dart';
import 'sync_remote_data_source.dart';

class SyncRepository {
  SyncRepository(
    this._remote,
    this._database, {
    Uuid? uuid,
    DateTime Function()? clock,
  }) : _uuid = uuid ?? const Uuid(),
       _clock = clock ?? DateTime.now;

  final SyncRemoteDataSource _remote;
  final AppDatabase _database;
  final Uuid _uuid;
  final DateTime Function() _clock;

  Future<SyncResult> synchronize(AuthSession session) async {
    final owner = session.user.uuid;
    final started = _clock().toUtc();
    final logUuid = _uuid.v4();
    await _database
        .into(_database.localSyncLogs)
        .insert(
          LocalSyncLogsCompanion.insert(
            uuid: logUuid,
            ownerUserUuid: owner,
            startedAt: started,
            status: 'running',
          ),
        );
    try {
      final outgoing = await _outgoing(owner);
      final batch = outgoing.isEmpty
          ? const SyncBatchResponse([], [], [])
          : await _remote.upload(session.tokens.accessToken, outgoing);
      await _applyBatch(owner, batch);
      var cursor = await _metadata(owner, 'sync_cursor');
      var downloaded = 0;
      var pageCount = 0;
      do {
        final incoming = await _remote.download(
          session.tokens.accessToken,
          cursor,
        );
        downloaded += await _applyChanges(owner, incoming);
        cursor = incoming.nextCursor;
        pageCount++;
        if (!incoming.hasMore) break;
        if (pageCount >= 100) throw const SyncUnexpectedFailure();
      } while (true);
      final result = SyncResult(
        uploaded: batch.accepted.length,
        downloaded: downloaded,
        conflicts: batch.conflicts.length,
        failed: batch.failed.length,
      );
      await _finishLog(logUuid, result, null);
      return result;
    } on Object catch (error) {
      await (_database.update(
        _database.localSyncLogs,
      )..where((row) => row.uuid.equals(logUuid))).write(
        LocalSyncLogsCompanion(
          completedAt: Value(_clock().toUtc()),
          status: const Value('failed'),
          safeError: Value(
            error is SyncNetworkFailure
                ? error.message
                : 'Synchronization failed.',
          ),
        ),
      );
      rethrow;
    }
  }

  Future<List<Map<String, dynamic>>> _outgoing(String owner) async {
    final rows =
        await (_database.select(_database.operationalRecords)
              ..where(
                (row) =>
                    row.ownerUserUuid.equals(owner) &
                    row.syncStatus.isIn([
                      SyncStatus.pendingCreate.value,
                      SyncStatus.pendingUpdate.value,
                      SyncStatus.pendingDelete.value,
                      SyncStatus.failed.value,
                    ]),
              )
              ..limit(100))
            .get();
    final output = <Map<String, dynamic>>[];
    for (final row in rows) {
      final report =
          await (_database.select(_database.draftReports)
                ..where((item) => item.localUuid.equals(row.reportLocalUuid)))
              .getSingle();
      if (report.serverUuid == null) continue;
      final idempotency = row.idempotencyKey ?? _uuid.v4();
      if (row.idempotencyKey == null) {
        await (_database.update(
          _database.operationalRecords,
        )..where((item) => item.localUuid.equals(row.localUuid))).write(
          OperationalRecordsCompanion(idempotencyKey: Value(idempotency)),
        );
      }
      await (_database.update(_database.operationalRecords)
            ..where((item) => item.localUuid.equals(row.localUuid)))
          .write(const OperationalRecordsCompanion(syncError: Value(null)));
      final payload = jsonDecode(row.payloadJson) as Map<String, dynamic>;
      output.add({
        'idempotency_key': idempotency,
        'operation': row.deletedLocally
            ? 'delete'
            : row.serverUuid == null
            ? 'create'
            : 'update',
        'resource_type': row.resourceType,
        'section_code': payload['section_code'],
        'report_uuid': report.serverUuid,
        'local_uuid': row.localUuid,
        'server_uuid': row.serverUuid,
        'expected_record_version': row.recordVersion,
        'values': payload['values'],
      });
    }
    return output;
  }

  Future<void> _applyBatch(String owner, SyncBatchResponse response) async {
    await _database.transaction(() async {
      for (final item in response.accepted) {
        final record = Map<String, dynamic>.from(item['record'] as Map);
        await (_database.update(_database.operationalRecords)..where(
              (row) => row.localUuid.equals(item['local_uuid'].toString()),
            ))
            .write(
              OperationalRecordsCompanion(
                serverUuid: Value(record['server_uuid'].toString()),
                recordVersion: Value(record['record_version'] as int),
                serverUpdatedAt: Value(
                  DateTime.parse(record['server_updated_at'] as String),
                ),
                syncStatus: Value(SyncStatus.synced.value),
                lastSyncedAt: Value(_clock().toUtc()),
                syncError: const Value(null),
              ),
            );
      }
      for (final item in response.conflicts) {
        final localUuid = item['local_uuid'].toString();
        final local = await (_database.select(
          _database.operationalRecords,
        )..where((row) => row.localUuid.equals(localUuid))).getSingle();
        await _database
            .into(_database.conflictRecords)
            .insert(
              ConflictRecordsCompanion.insert(
                uuid: _uuid.v4(),
                ownerUserUuid: owner,
                resourceType: local.resourceType,
                localUuid: localUuid,
                serverUuid: Value(local.serverUuid),
                localPayloadJson: local.payloadJson,
                serverPayloadJson: jsonEncode(item['server']),
                status: ConflictStatus.unresolved.value,
                serverValueRequired: Value(
                  item['server_value_required'] as bool? ?? false,
                ),
                detectedAt: _clock().toUtc(),
              ),
            );
        await (_database.update(
          _database.operationalRecords,
        )..where((row) => row.localUuid.equals(localUuid))).write(
          OperationalRecordsCompanion(
            syncStatus: Value(SyncStatus.conflict.value),
          ),
        );
      }
      for (final item in response.failed) {
        await (_database.update(_database.operationalRecords)..where(
              (row) => row.localUuid.equals(item['local_uuid'].toString()),
            ))
            .write(
              OperationalRecordsCompanion(
                syncStatus: Value(SyncStatus.failed.value),
                syncError: Value(item['code']?.toString() ?? 'server_rejected'),
              ),
            );
      }
    });
  }

  Future<int> _applyChanges(String owner, SyncChangesResponse response) async {
    var count = 0;
    await _database.transaction(() async {
      for (final change in response.changes) {
        final report =
            await (_database.select(_database.draftReports)..where(
                  (row) =>
                      row.ownerUserUuid.equals(owner) &
                      row.serverUuid.equals(change['report_uuid'].toString()),
                ))
                .getSingleOrNull();
        if (report == null) continue;
        final existing =
            await (_database.select(_database.operationalRecords)..where(
                  (row) =>
                      row.ownerUserUuid.equals(owner) &
                      row.resourceType.equals(
                        change['resource_type'].toString(),
                      ) &
                      row.serverUuid.equals(change['server_uuid'].toString()),
                ))
                .getSingleOrNull();
        if (existing != null &&
            existing.syncStatus != SyncStatus.synced.value) {
          continue;
        }
        final localUuid =
            existing?.localUuid ?? change['server_uuid'].toString();
        await _database
            .into(_database.operationalRecords)
            .insertOnConflictUpdate(
              OperationalRecordsCompanion.insert(
                localUuid: localUuid,
                ownerUserUuid: owner,
                serverUuid: Value(change['server_uuid'].toString()),
                resourceType: change['resource_type'].toString(),
                reportLocalUuid: report.localUuid,
                payloadJson: jsonEncode({
                  'section_code': change['section_code'],
                  'values': change['values'],
                }),
                recordVersion: Value(change['record_version'] as int),
                syncStatus: SyncStatus.synced.value,
                createdAt: existing?.createdAt ?? _clock().toUtc(),
                updatedAt: _clock().toUtc(),
                lastSyncedAt: Value(_clock().toUtc()),
                serverUpdatedAt: Value(
                  DateTime.parse(change['server_updated_at'] as String),
                ),
              ),
            );
        count++;
      }
      await _setMetadata(owner, 'sync_cursor', response.nextCursor);
    });
    return count;
  }

  Future<String?> _metadata(String owner, String key) async =>
      (_database.select(_database.syncMetadataEntries)..where(
            (row) => row.ownerUserUuid.equals(owner) & row.key.equals(key),
          ))
          .map((row) => row.value)
          .getSingleOrNull();

  Future<void> _setMetadata(String owner, String key, String value) => _database
      .into(_database.syncMetadataEntries)
      .insertOnConflictUpdate(
        SyncMetadataEntriesCompanion.insert(
          ownerUserUuid: owner,
          key: key,
          value: Value(value),
          updatedAt: _clock().toUtc(),
        ),
      );

  Future<void> _finishLog(String uuid, SyncResult result, String? error) =>
      (_database.update(
        _database.localSyncLogs,
      )..where((row) => row.uuid.equals(uuid))).write(
        LocalSyncLogsCompanion(
          completedAt: Value(_clock().toUtc()),
          uploadedCount: Value(result.uploaded),
          downloadedCount: Value(result.downloaded),
          conflictCount: Value(result.conflicts),
          failedCount: Value(result.failed),
          status: Value(
            result.conflicts == 0 && result.failed == 0
                ? 'completed'
                : 'partial',
          ),
          safeError: Value(error),
        ),
      );
}
