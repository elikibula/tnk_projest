import 'dart:convert';

import 'package:drift/drift.dart';

import '../auth/auth_models.dart';
import '../database/app_database.dart';
import 'bootstrap_failures.dart';
import 'bootstrap_models.dart';
import 'bootstrap_remote_data_source.dart';

class BootstrapRepository {
  BootstrapRepository(
    this._remote,
    this._database, {
    DateTime Function()? clock,
  }) : _clock = clock ?? DateTime.now;

  final BootstrapRemoteDataSource _remote;
  final AppDatabase _database;
  final DateTime Function() _clock;

  Future<BootstrapSnapshot> load(AuthSession session) async {
    final cached = await readCached(session.user.uuid);
    if (session.isOffline) {
      if (cached == null) throw const BootstrapUnavailableOfflineFailure();
      return cached.copyWith(isOffline: true);
    }
    try {
      final bundle = await _remote.download(session.tokens.accessToken);
      if (bundle.user['uuid'].toString() != session.user.uuid) {
        throw const BootstrapUnexpectedFailure();
      }
      await _replaceCache(session.user.uuid, bundle);
      return (await readCached(session.user.uuid))!;
    } on BootstrapNetworkFailure {
      if (cached != null) return cached.copyWith(isOffline: true);
      rethrow;
    }
  }

  Future<BootstrapSnapshot?> readCached(String ownerUserUuid) async {
    Future<int> referenceCount(String type) async =>
        (_database.selectOnly(_database.cachedReferenceItems)
              ..addColumns([_database.cachedReferenceItems.serverUuid.count()])
              ..where(
                _database.cachedReferenceItems.ownerUserUuid.equals(
                      ownerUserUuid,
                    ) &
                    _database.cachedReferenceItems.resourceType.equals(type),
              ))
            .map(
              (row) =>
                  row.read(_database.cachedReferenceItems.serverUuid.count())!,
            )
            .getSingle();
    Future<int> masterCount(String type) async =>
        (_database.selectOnly(_database.cachedMasterRecords)
              ..addColumns([_database.cachedMasterRecords.serverUuid.count()])
              ..where(
                _database.cachedMasterRecords.ownerUserUuid.equals(
                      ownerUserUuid,
                    ) &
                    _database.cachedMasterRecords.resourceType.equals(type),
              ))
            .map(
              (row) =>
                  row.read(_database.cachedMasterRecords.serverUuid.count())!,
            )
            .getSingle();

    final cachedAt =
        await (_database.select(_database.syncMetadataEntries)..where(
              (row) =>
                  row.ownerUserUuid.equals(ownerUserUuid) &
                  row.key.equals('last_bootstrap_at'),
            ))
            .getSingleOrNull();
    if (cachedAt?.value == null) return null;
    return BootstrapSnapshot(
      ownerUserUuid: ownerUserUuid,
      cachedAt: DateTime.parse(cachedAt!.value!).toUtc(),
      villageCount: await masterCount('village'),
      reportingPeriodCount: await referenceCount('reporting_period'),
      reportCount: await masterCount('report'),
      sectionCount: await referenceCount('section_definition'),
      isOffline: false,
    );
  }

  Future<void> _replaceCache(String owner, BootstrapBundle bundle) async {
    final cachedAt = _clock().toUtc();
    await _database.transaction(() async {
      await (_database.delete(
        _database.cachedReferenceItems,
      )..where((row) => row.ownerUserUuid.equals(owner))).go();
      await (_database.delete(
        _database.cachedMasterRecords,
      )..where((row) => row.ownerUserUuid.equals(owner))).go();

      for (final period in bundle.reportingPeriods) {
        await _database
            .into(_database.cachedReferenceItems)
            .insert(
              CachedReferenceItemsCompanion.insert(
                ownerUserUuid: owner,
                resourceType: 'reporting_period',
                serverUuid: period['uuid'].toString(),
                payloadJson: jsonEncode(period),
                serverUpdatedAt: Value(_date(period['updated_at'])),
                cachedAt: cachedAt,
              ),
            );
      }
      for (final section in bundle.sectionDefinitions) {
        await _database
            .into(_database.cachedReferenceItems)
            .insert(
              CachedReferenceItemsCompanion.insert(
                ownerUserUuid: owner,
                resourceType: 'section_definition',
                serverUuid: section['code'].toString(),
                payloadJson: jsonEncode(section),
                cachedAt: cachedAt,
              ),
            );
      }
      for (final village in bundle.villages) {
        await _insertMaster(
          owner,
          'village',
          village,
          cachedAt,
          bundle.serverTime,
        );
      }
      for (final report in bundle.reports) {
        await _insertMaster(
          owner,
          'report',
          report,
          cachedAt,
          bundle.serverTime,
        );
      }
      await _insertMaster(
        owner,
        'user',
        bundle.user,
        cachedAt,
        bundle.serverTime,
      );
      await _insertMaster(
        owner,
        'device',
        bundle.device,
        cachedAt,
        bundle.serverTime,
      );
      await _insertMaster(
        owner,
        'workflow_capabilities',
        {'uuid': owner, 'values': bundle.workflowCapabilities},
        cachedAt,
        bundle.serverTime,
      );

      final metadata = {
        'schema_version': bundle.schemaVersion.toString(),
        'server_time': bundle.serverTime.toIso8601String(),
        'sync_cursor': bundle.syncCursor,
        'last_bootstrap_at': cachedAt.toIso8601String(),
      };
      for (final entry in metadata.entries) {
        await _database
            .into(_database.syncMetadataEntries)
            .insertOnConflictUpdate(
              SyncMetadataEntriesCompanion.insert(
                ownerUserUuid: owner,
                key: entry.key,
                value: Value(entry.value),
                updatedAt: cachedAt,
              ),
            );
      }
    });
  }

  Future<void> _insertMaster(
    String owner,
    String type,
    Map<String, dynamic> value,
    DateTime cachedAt,
    DateTime fallbackUpdatedAt,
  ) => _database
      .into(_database.cachedMasterRecords)
      .insert(
        CachedMasterRecordsCompanion.insert(
          ownerUserUuid: owner,
          resourceType: type,
          serverUuid: value['uuid'].toString(),
          villageUuid: Value(value['village_uuid']?.toString()),
          payloadJson: jsonEncode(value),
          recordVersion: (value['record_version'] as int?) ?? 1,
          serverUpdatedAt: _date(value['updated_at']) ?? fallbackUpdatedAt,
          cachedAt: cachedAt,
        ),
      );

  DateTime? _date(Object? value) =>
      value == null ? null : DateTime.parse(value.toString()).toUtc();
}
