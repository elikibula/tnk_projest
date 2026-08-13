import 'package:drift/native.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:tnk_insight_mobile/core/auth/auth_models.dart';
import 'package:tnk_insight_mobile/core/bootstrap/bootstrap_failures.dart';
import 'package:tnk_insight_mobile/core/bootstrap/bootstrap_models.dart';
import 'package:tnk_insight_mobile/core/bootstrap/bootstrap_remote_data_source.dart';
import 'package:tnk_insight_mobile/core/bootstrap/bootstrap_repository.dart';
import 'package:tnk_insight_mobile/core/database/app_database.dart';

void main() {
  late AppDatabase database;
  late FakeBootstrapRemote remote;
  late BootstrapRepository repository;
  final now = DateTime.utc(2026, 8, 11, 9);

  setUp(() {
    database = AppDatabase(NativeDatabase.memory());
    remote = FakeBootstrapRemote(_bundle(now));
    repository = BootstrapRepository(remote, database, clock: () => now);
  });

  tearDown(() => database.close());

  test(
    'online bootstrap atomically caches authorised reference data',
    () async {
      final snapshot = await repository.load(_session());

      expect(snapshot.villageCount, 1);
      expect(snapshot.reportingPeriodCount, 1);
      expect(snapshot.reportCount, 1);
      expect(snapshot.sectionCount, 1);
      expect(snapshot.isOffline, isFalse);
      expect(await repository.readCached('another-user'), isNull);
    },
  );

  test('network failure uses an existing user-scoped cache', () async {
    await repository.load(_session());
    remote.error = const BootstrapNetworkFailure();

    final snapshot = await repository.load(_session());

    expect(snapshot.isOffline, isTrue);
    expect(snapshot.ownerUserUuid, 'user-1');
  });

  test('first bootstrap cannot happen offline', () async {
    await expectLater(
      repository.load(_session(isOffline: true)),
      throwsA(isA<BootstrapUnavailableOfflineFailure>()),
    );
  });

  test('mismatched server user is rejected without writing cache', () async {
    remote.bundle = _bundle(now, userUuid: 'different-user');

    await expectLater(
      repository.load(_session()),
      throwsA(isA<BootstrapUnexpectedFailure>()),
    );
    expect(await repository.readCached('user-1'), isNull);
  });
}

AuthSession _session({bool isOffline = false}) => AuthSession(
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
    deviceUuid: 'device-1',
  ),
  establishedAt: DateTime.utc(2026, 8, 11),
  offlineValidUntil: DateTime.utc(2026, 8, 14),
  isOffline: isOffline,
);

BootstrapBundle _bundle(DateTime now, {String userUuid = 'user-1'}) =>
    BootstrapBundle(
      schemaVersion: 1,
      serverTime: now,
      syncCursor: null,
      user: {'uuid': userUuid, 'username': 'tnk-a1', 'record_version': 2},
      device: {
        'uuid': 'device-1',
        'version_policy': {'force_upgrade': false},
      },
      villages: [
        {
          'uuid': 'village-a1',
          'name_en': 'Village A1',
          'record_version': 3,
          'updated_at': now.toIso8601String(),
        },
      ],
      reportingPeriods: [
        {
          'uuid': 'period-q2',
          'year': 2026,
          'quarter': 2,
          'updated_at': now.toIso8601String(),
        },
      ],
      reports: [
        {
          'uuid': 'report-a1',
          'village_uuid': 'village-a1',
          'record_version': 1,
          'updated_at': now.toIso8601String(),
        },
      ],
      sectionDefinitions: [
        {'code': 'village_profile', 'label': 'Village profile'},
      ],
      workflowCapabilities: const {
        'report-a1': ['edit'],
      },
    );

class FakeBootstrapRemote implements BootstrapRemoteDataSource {
  FakeBootstrapRemote(this.bundle);
  BootstrapBundle bundle;
  Object? error;

  @override
  Future<BootstrapBundle> download(String accessToken) async {
    if (error case final value?) throw value;
    return bundle;
  }
}
