import 'dart:convert';

import 'package:drift/drift.dart';
import 'package:drift/native.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:tnk_insight_mobile/core/auth/auth_models.dart';
import 'package:tnk_insight_mobile/core/database/app_database.dart';
import 'package:tnk_insight_mobile/features/validation/data/validation_remote_data_source.dart';
import 'package:tnk_insight_mobile/features/validation/data/validation_repository.dart';
import 'package:tnk_insight_mobile/features/validation/domain/validation_models.dart';

void main() {
  test(
    'submission uses declaration and both authoritative transitions',
    () async {
      final database = await _database();
      addTearDown(database.close);
      final remote = FakeValidationRemote();
      final repository = ValidationRepository(database, remote);

      final result = await repository.submit(_session(), 'report-1');

      expect(result['status'], 'submitted');
      expect(remote.declared, isTrue);
      expect(remote.actions, ['mark_ready', 'submit']);
      final local = await database.select(database.draftReports).getSingle();
      expect(jsonDecode(local.payloadJson), {'status': 'submitted'});
    },
  );

  test('critical server issue prevents workflow transition', () async {
    final database = await _database();
    addTearDown(database.close);
    final remote = FakeValidationRemote(critical: true);
    final result = await ValidationRepository(
      database,
      remote,
    ).submit(_session(), 'report-1');

    expect(result['status'], 'draft');
    expect(remote.declared, isFalse);
    expect(remote.actions, isEmpty);
  });
}

Future<AppDatabase> _database() async {
  final database = AppDatabase(NativeDatabase.memory());
  final now = DateTime.utc(2026, 8, 11);
  final report = _report('draft', ['mark_ready']);
  await database
      .into(database.cachedMasterRecords)
      .insert(
        CachedMasterRecordsCompanion.insert(
          ownerUserUuid: 'user-1',
          resourceType: 'report',
          serverUuid: 'report-1',
          villageUuid: const Value('village-1'),
          payloadJson: jsonEncode(report),
          recordVersion: 1,
          serverUpdatedAt: now,
          cachedAt: now,
        ),
      );
  await database
      .into(database.draftReports)
      .insert(
        DraftReportsCompanion.insert(
          localUuid: 'local-report',
          ownerUserUuid: 'user-1',
          serverUuid: const Value('report-1'),
          villageUuid: 'village-1',
          reportingPeriodUuid: 'period-1',
          payloadJson: '{"status":"draft"}',
          syncStatus: 'synced',
          createdAt: now,
          updatedAt: now,
        ),
      );
  return database;
}

Map<String, dynamic> _report(String status, List<String> actions) => {
  'uuid': 'report-1',
  'village_uuid': 'village-1',
  'reporting_period_uuid': 'period-1',
  'status': status,
  'completeness_percentage': 100,
  'record_version': status == 'submitted' ? 3 : 1,
  'updated_at': '2026-08-11T00:00:00Z',
  'workflow_actions': actions,
};

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

class FakeValidationRemote implements ValidationRemoteDataSource {
  FakeValidationRemote({this.critical = false});
  final bool critical;
  bool declared = false;
  final actions = <String>[];

  @override
  Future<Map<String, dynamic>> report(String token, String reportUuid) async =>
      _report('draft', ['mark_ready']);
  @override
  Future<ValidationSnapshot> issues(String token, String reportUuid) async =>
      _snapshot();
  @override
  Future<ValidationSnapshot> validate(String token, String reportUuid) async =>
      _snapshot();
  ValidationSnapshot _snapshot() => ValidationSnapshot(
    report: _report('draft', ['mark_ready']),
    issues: critical
        ? const [
            QualityIssue(
              uuid: 'issue-1',
              section: 'validation_submission',
              fieldName: '',
              severity: 'critical',
              message: 'Incomplete',
              currentValue: '1',
              previousValue: '',
            ),
          ]
        : const [],
  );
  @override
  Future<void> declare(String token, String reportUuid) async =>
      declared = true;
  @override
  Future<Map<String, dynamic>> transition(
    String token,
    String reportUuid,
    String action,
  ) async {
    actions.add(action);
    return action == 'mark_ready'
        ? _report('ready_for_validation', ['submit'])
        : _report('submitted', const []);
  }
}
