import 'package:drift/drift.dart';
import 'package:drift/native.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:tnk_insight_mobile/core/auth/auth_models.dart';
import 'package:tnk_insight_mobile/core/database/app_database.dart';
import 'package:tnk_insight_mobile/features/dashboard/data/dashboard_remote_data_source.dart';
import 'package:tnk_insight_mobile/features/dashboard/data/dashboard_repository.dart';

void main() {
  test(
    'dashboard combines server summary with local sync state and offline cache',
    () async {
      final database = AppDatabase(NativeDatabase.memory());
      addTearDown(database.close);
      final now = DateTime.utc(2026, 8, 11);
      await database
          .into(database.draftReports)
          .insert(
            DraftReportsCompanion.insert(
              localUuid: 'report-local',
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
      await database
          .into(database.operationalRecords)
          .insert(
            OperationalRecordsCompanion.insert(
              localUuid: 'entry-1',
              ownerUserUuid: 'user-1',
              resourceType: 'population',
              reportLocalUuid: 'report-local',
              payloadJson: '{}',
              syncStatus: 'pending_update',
              createdAt: now,
              updatedAt: now,
            ),
          );
      await database
          .into(database.localSyncLogs)
          .insert(
            LocalSyncLogsCompanion.insert(
              uuid: 'log-1',
              ownerUserUuid: 'user-1',
              startedAt: now,
              completedAt: Value(now),
              status: 'completed',
            ),
          );
      final repository = DashboardRepository(database, FakeDashboardRemote());

      final online = await repository.load(_session());
      await repository.load(_session(), reportUuid: 'previous-report');
      final offline = await repository.load(
        _session().copyWith(isOffline: true),
      );

      expect(online.report?.status, 'draft');
      expect(online.pendingSync, 1);
      expect(online.lastSuccessfulSync?.toUtc(), now);
      expect(online.indicators.single.value, '418.0000');
      expect(offline.isOffline, isTrue);
      expect(offline.location['village'], 'Village A1');
    },
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

class FakeDashboardRemote implements DashboardRemoteDataSource {
  @override
  Future<Map<String, dynamic>> load(String token, {String? reportUuid}) async {
    final payload = <String, dynamic>{
      'report': {
        'uuid': 'report-1',
        'village_uuid': 'village-1',
        'reporting_period_uuid': 'period-1',
        'status': 'draft',
        'completeness_percentage': 50,
        'data_quality_score': 80,
        'record_version': 1,
        'sections': <dynamic>[],
      },
      'location': {
        'village': 'Village A1',
        'tikina': 'Tikina A',
        'province': 'Province A',
      },
      'reporting_period': {'label': '2026 Q2'},
      'pending_validation_issues': 2,
      'indicators': [
        {
          'code': 'total_population',
          'name_en': 'Total population',
          'name_fj': 'Lewenivanua',
          'value': '418.0000',
          'unit': 'people',
          'status': 'calculated',
          'quality_rating': 'good',
          'breakdown': <String, dynamic>{},
        },
      ],
    };
    if (reportUuid != null) {
      (payload['location'] as Map<String, dynamic>)['village'] = 'Old village';
    }
    return payload;
  }

  @override
  Future<Map<String, dynamic>> start(
    String token,
    String villageUuid,
    String periodUuid,
  ) => throw UnimplementedError();
}
