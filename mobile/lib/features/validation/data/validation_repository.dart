import 'dart:convert';

import 'package:drift/drift.dart';

import '../../../core/auth/auth_models.dart';
import '../../../core/database/app_database.dart';
import '../domain/validation_models.dart';
import 'validation_remote_data_source.dart';

class ValidationRepository {
  ValidationRepository(this._database, this._remote);
  final AppDatabase _database;
  final ValidationRemoteDataSource _remote;

  Future<ValidationSnapshot> load(
    AuthSession session,
    String reportUuid,
  ) async {
    final result = await _remote.issues(session.tokens.accessToken, reportUuid);
    await _cacheReport(session.user.uuid, result.report);
    return result;
  }

  Future<ValidationSnapshot> validate(
    AuthSession session,
    String reportUuid,
  ) async {
    final result = await _remote.validate(
      session.tokens.accessToken,
      reportUuid,
    );
    await _cacheReport(session.user.uuid, result.report);
    return result;
  }

  Future<Map<String, dynamic>> submit(
    AuthSession session,
    String reportUuid,
  ) async {
    var report = await _remote.report(session.tokens.accessToken, reportUuid);
    var snapshot = await validate(session, reportUuid);
    if (snapshot.issues.any((issue) => issue.blocking)) return snapshot.report;
    await _remote.declare(session.tokens.accessToken, reportUuid);
    final actions = (report['workflow_actions'] as List<dynamic>? ?? const [])
        .map((value) => value.toString())
        .toSet();
    if (actions.contains('mark_ready')) {
      report = await _remote.transition(
        session.tokens.accessToken,
        reportUuid,
        'mark_ready',
      );
    }
    final refreshedActions =
        (report['workflow_actions'] as List<dynamic>? ?? const [])
            .map((value) => value.toString())
            .toSet();
    if (!refreshedActions.contains('submit')) {
      throw const SubmissionNotConfirmed(
        'The server did not authorize submission.',
      );
    }
    report = await _remote.transition(
      session.tokens.accessToken,
      reportUuid,
      'submit',
    );
    if (report['status'] != 'submitted') throw const SubmissionNotConfirmed();
    await _cacheReport(session.user.uuid, report);
    return report;
  }

  Future<int> unsyncedAttachments(String owner, String reportLocalUuid) =>
      (_database.select(_database.pendingAttachments)..where(
            (row) =>
                row.ownerUserUuid.equals(owner) &
                row.reportLocalUuid.equals(reportLocalUuid) &
                row.syncStatus.equals('synced').not(),
          ))
          .get()
          .then((rows) => rows.length);

  Future<void> _cacheReport(String owner, Map<String, dynamic> report) async {
    final uuid = report['uuid'].toString();
    final now = DateTime.now().toUtc();
    await _database.transaction(() async {
      await (_database.update(_database.cachedMasterRecords)..where(
            (row) =>
                row.ownerUserUuid.equals(owner) &
                row.resourceType.equals('report') &
                row.serverUuid.equals(uuid),
          ))
          .write(
            CachedMasterRecordsCompanion(
              payloadJson: Value(jsonEncode(report)),
              recordVersion: Value(report['record_version'] as int),
              serverUpdatedAt: Value(
                DateTime.parse(report['updated_at'].toString()),
              ),
              cachedAt: Value(now),
            ),
          );
      await (_database.update(_database.draftReports)..where(
            (row) =>
                row.ownerUserUuid.equals(owner) & row.serverUuid.equals(uuid),
          ))
          .write(
            DraftReportsCompanion(
              payloadJson: Value(jsonEncode({'status': report['status']})),
              recordVersion: Value(report['record_version'] as int),
              updatedAt: Value(now),
              serverUpdatedAt: Value(
                DateTime.parse(report['updated_at'].toString()),
              ),
              syncStatus: const Value('synced'),
            ),
          );
    });
  }
}
