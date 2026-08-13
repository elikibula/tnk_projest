import 'dart:convert';
import 'package:dio/dio.dart';
import 'package:drift/drift.dart';
import '../../../core/auth/auth_models.dart';
import '../../../core/database/app_database.dart';
import '../../reporting/domain/reporting_models.dart';
import '../domain/dashboard_models.dart';
import 'dashboard_remote_data_source.dart';

class DashboardRepository {
  DashboardRepository(this._database, this._remote);
  final AppDatabase _database;
  final DashboardRemoteDataSource _remote;
  Future<DashboardSnapshot> load(
    AuthSession session, {
    String? reportUuid,
  }) async {
    Map<String, dynamic> payload;
    var offline = session.isOffline;
    try {
      if (offline) throw const DashboardOffline();
      payload = await _remote.load(
        session.tokens.accessToken,
        reportUuid: reportUuid,
      );
      await _cache(session.user.uuid, payload, reportUuid);
    } on Object catch (error) {
      if (error is! DioException && error is! DashboardOffline) rethrow;
      final cached = await _cached(session.user.uuid, reportUuid);
      if (cached == null) rethrow;
      payload = cached;
      offline = true;
    }
    final local = await _localMetrics(session.user.uuid);
    return DashboardSnapshot.fromJson(
      payload,
      pendingSync: local.$1,
      lastSuccessfulSync: local.$2,
      isOffline: offline,
    );
  }

  Future<LocalReportSummary> startReport(
    AuthSession session,
    String villageUuid,
    String periodUuid,
  ) async => LocalReportSummary.fromJson(
    await _remote.start(session.tokens.accessToken, villageUuid, periodUuid),
  );
  Future<List<StartReportOption>> villages(
    String owner, {
    String languageCode = 'en',
  }) =>
      (_database.select(_database.cachedMasterRecords)..where(
            (row) =>
                row.ownerUserUuid.equals(owner) &
                row.resourceType.equals('village'),
          ))
          .get()
          .then(
            (rows) => rows.map((row) {
              final value = jsonDecode(row.payloadJson) as Map<String, dynamic>;
              final localized = value['name_$languageCode']?.toString() ?? '';
              return StartReportOption(
                row.serverUuid,
                localized.isNotEmpty ? localized : value['name_en'].toString(),
              );
            }).toList(),
          );
  Future<List<StartReportOption>> periods(String owner) =>
      (_database.select(_database.cachedReferenceItems)..where(
            (row) =>
                row.ownerUserUuid.equals(owner) &
                row.resourceType.equals('reporting_period'),
          ))
          .get()
          .then(
            (rows) => rows.map((row) {
              final value = jsonDecode(row.payloadJson) as Map<String, dynamic>;
              return StartReportOption(
                row.serverUuid,
                '${value['year']} Q${value['quarter']}',
              );
            }).toList(),
          );
  Future<(int, DateTime?)> _localMetrics(String owner) async {
    final records =
        await (_database.select(_database.operationalRecords)..where(
              (row) =>
                  row.ownerUserUuid.equals(owner) &
                  row.syncStatus.equals('synced').not(),
            ))
            .get();
    final attachments =
        await (_database.select(_database.pendingAttachments)..where(
              (row) =>
                  row.ownerUserUuid.equals(owner) &
                  row.syncStatus.equals('synced').not(),
            ))
            .get();
    final log =
        await (_database.select(_database.localSyncLogs)
              ..where(
                (row) =>
                    row.ownerUserUuid.equals(owner) &
                    row.status.equals('completed'),
              )
              ..orderBy([(row) => OrderingTerm.desc(row.completedAt)])
              ..limit(1))
            .getSingleOrNull();
    return (records.length + attachments.length, log?.completedAt);
  }

  Future<void> _cache(
    String owner,
    Map<String, dynamic> payload,
    String? reportUuid,
  ) => _database
      .into(_database.cachedMasterRecords)
      .insertOnConflictUpdate(
        CachedMasterRecordsCompanion.insert(
          ownerUserUuid: owner,
          resourceType: 'dashboard',
          serverUuid: reportUuid ?? owner,
          payloadJson: jsonEncode(payload),
          recordVersion: 1,
          serverUpdatedAt: DateTime.now().toUtc(),
          cachedAt: DateTime.now().toUtc(),
        ),
      );
  Future<Map<String, dynamic>?> _cached(String owner, String? reportUuid) =>
      (_database.select(_database.cachedMasterRecords)..where(
            (row) =>
                row.ownerUserUuid.equals(owner) &
                row.resourceType.equals('dashboard') &
                row.serverUuid.equals(reportUuid ?? owner),
          ))
          .map((row) => jsonDecode(row.payloadJson) as Map<String, dynamic>)
          .getSingleOrNull();
}

class DashboardOffline implements Exception {
  const DashboardOffline();
}
