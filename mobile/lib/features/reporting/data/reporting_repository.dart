import 'dart:convert';

import 'package:drift/drift.dart';
import 'package:uuid/uuid.dart';

import '../../../core/database/app_database.dart';
import '../../../core/database/sync_status.dart';
import '../domain/reporting_models.dart';

class ReportingRepository {
  ReportingRepository(this._database, {Uuid? uuid, DateTime Function()? clock})
    : _uuid = uuid ?? const Uuid(),
      _clock = clock ?? DateTime.now;

  final AppDatabase _database;
  final Uuid _uuid;
  final DateTime Function() _clock;

  Future<List<LocalReportSummary>> listReports(String owner) async {
    final rows =
        await (_database.select(_database.cachedMasterRecords)..where(
              (row) =>
                  row.ownerUserUuid.equals(owner) &
                  row.resourceType.equals('report'),
            ))
            .get();
    return rows
        .map(
          (row) => LocalReportSummary.fromJson(
            jsonDecode(row.payloadJson) as Map<String, dynamic>,
          ),
        )
        .toList(growable: false);
  }

  Future<DraftReport?> reportByLocalUuid(String owner, String localUuid) =>
      (_database.select(_database.draftReports)..where(
            (row) =>
                row.ownerUserUuid.equals(owner) &
                row.localUuid.equals(localUuid),
          ))
          .getSingleOrNull();

  Future<List<ReportSectionDefinition>> listSections(String owner) async {
    final rows =
        await (_database.select(_database.cachedReferenceItems)
              ..where(
                (row) =>
                    row.ownerUserUuid.equals(owner) &
                    row.resourceType.equals('section_definition'),
              )
              ..orderBy([(row) => OrderingTerm.asc(row.rowId)]))
            .get();
    return rows
        .map(
          (row) => ReportSectionDefinition.fromJson(
            jsonDecode(row.payloadJson) as Map<String, dynamic>,
          ),
        )
        .toList(growable: false);
  }

  Future<String> materializeReport(
    String owner,
    LocalReportSummary report,
  ) async {
    final existing =
        await (_database.select(_database.draftReports)..where(
              (row) =>
                  row.ownerUserUuid.equals(owner) &
                  row.serverUuid.equals(report.uuid),
            ))
            .getSingleOrNull();
    if (existing != null) return existing.localUuid;
    final now = _clock().toUtc();
    final localUuid = _uuid.v4();
    await _database
        .into(_database.draftReports)
        .insert(
          DraftReportsCompanion.insert(
            localUuid: localUuid,
            ownerUserUuid: owner,
            serverUuid: Value(report.uuid),
            villageUuid: report.villageUuid,
            reportingPeriodUuid: report.periodUuid,
            payloadJson: jsonEncode({'status': report.status}),
            recordVersion: Value(report.recordVersion),
            syncStatus: SyncStatus.synced.value,
            createdAt: now,
            updatedAt: now,
          ),
        );
    return localUuid;
  }

  Future<List<LocalReportEntry>> listEntries(
    String owner,
    String reportLocalUuid,
    String sectionCode,
  ) async {
    final rows =
        await (_database.select(_database.operationalRecords)
              ..where(
                (row) =>
                    row.ownerUserUuid.equals(owner) &
                    row.reportLocalUuid.equals(reportLocalUuid) &
                    row.deletedLocally.equals(false),
              )
              ..orderBy([(row) => OrderingTerm.desc(row.updatedAt)]))
            .get();
    return rows
        .map(
          (row) => LocalReportEntry.fromStored(
            localUuid: row.localUuid,
            resourceType: row.resourceType,
            payloadJson: row.payloadJson,
            syncStatus: row.syncStatus,
            updatedAt: row.updatedAt,
            serverUuid: row.serverUuid,
          ),
        )
        .where((entry) => entry.sectionCode == sectionCode)
        .toList(growable: false);
  }

  Future<String> saveEntry({
    required String owner,
    required String reportLocalUuid,
    required String sectionCode,
    required String entryType,
    required Map<String, dynamic> values,
    String? localUuid,
  }) async {
    final now = _clock().toUtc();
    final id = localUuid ?? _uuid.v4();
    await _requireEditableReport(owner, reportLocalUuid);
    final existing =
        await (_database.select(_database.operationalRecords)..where(
              (row) =>
                  row.localUuid.equals(id) & row.ownerUserUuid.equals(owner),
            ))
            .getSingleOrNull();
    final companion = OperationalRecordsCompanion.insert(
      localUuid: id,
      ownerUserUuid: owner,
      serverUuid: Value(existing?.serverUuid),
      resourceType: entryType,
      reportLocalUuid: reportLocalUuid,
      payloadJson: jsonEncode({'section_code': sectionCode, 'values': values}),
      recordVersion: Value(existing?.recordVersion ?? 0),
      syncStatus: existing?.serverUuid == null
          ? SyncStatus.pendingCreate.value
          : SyncStatus.pendingUpdate.value,
      createdAt: existing?.createdAt ?? now,
      updatedAt: now,
    );
    await _database
        .into(_database.operationalRecords)
        .insertOnConflictUpdate(companion);
    await (_database.update(_database.draftReports)..where(
          (row) =>
              row.localUuid.equals(reportLocalUuid) &
              row.ownerUserUuid.equals(owner),
        ))
        .write(
          DraftReportsCompanion(
            updatedAt: Value(now),
            syncStatus: Value(SyncStatus.pendingUpdate.value),
          ),
        );
    return id;
  }

  Future<void> deleteEntry({
    required String owner,
    required String reportLocalUuid,
    required String localUuid,
  }) async {
    await _requireEditableReport(owner, reportLocalUuid);
    final entry =
        await (_database.select(_database.operationalRecords)..where(
              (row) =>
                  row.localUuid.equals(localUuid) &
                  row.ownerUserUuid.equals(owner) &
                  row.reportLocalUuid.equals(reportLocalUuid),
            ))
            .getSingle();
    if (entry.serverUuid == null) {
      await (_database.delete(
        _database.operationalRecords,
      )..where((row) => row.localUuid.equals(localUuid))).go();
    } else {
      await (_database.update(
        _database.operationalRecords,
      )..where((row) => row.localUuid.equals(localUuid))).write(
        OperationalRecordsCompanion(
          deletedLocally: const Value(true),
          syncStatus: Value(SyncStatus.pendingDelete.value),
          updatedAt: Value(_clock().toUtc()),
        ),
      );
    }
  }

  Future<void> _requireEditableReport(String owner, String localUuid) async {
    final report =
        await (_database.select(_database.draftReports)..where(
              (row) =>
                  row.localUuid.equals(localUuid) &
                  row.ownerUserUuid.equals(owner),
            ))
            .getSingle();
    final payload = jsonDecode(report.payloadJson) as Map<String, dynamic>;
    final status = payload['status']?.toString();
    if (status != 'draft' && status != 'returned_to_village') {
      throw const ReportReadOnlyFailure();
    }
  }
}

class ReportReadOnlyFailure implements Exception {
  const ReportReadOnlyFailure();
  String get message => 'Only draft or returned reports can be edited.';
}
