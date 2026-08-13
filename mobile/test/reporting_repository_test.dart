import 'dart:convert';

import 'package:drift/drift.dart';
import 'package:drift/native.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:tnk_insight_mobile/core/database/app_database.dart';
import 'package:tnk_insight_mobile/features/reporting/data/reporting_repository.dart';

void main() {
  late AppDatabase database;
  late ReportingRepository repository;
  final now = DateTime.utc(2026, 8, 11, 10);

  setUp(() {
    database = AppDatabase(NativeDatabase.memory());
    repository = ReportingRepository(database, clock: () => now);
  });

  tearDown(() => database.close());

  test('cached server report becomes an editable local draft', () async {
    await _cacheReport(database, now);

    final reports = await repository.listReports('user-1');
    final localUuid = await repository.materializeReport(
      'user-1',
      reports.single,
    );

    final draft = await database.select(database.draftReports).getSingle();
    expect(draft.localUuid, localUuid);
    expect(draft.serverUuid, 'report-1');
    expect(draft.recordVersion, 4);
  });

  test('offline entry create and edit autosave without duplication', () async {
    await _cacheReport(database, now);
    final report = (await repository.listReports('user-1')).single;
    final localReport = await repository.materializeReport('user-1', report);

    final entryUuid = await repository.saveEntry(
      owner: 'user-1',
      reportLocalUuid: localReport,
      sectionCode: 'population_households',
      entryType: 'population',
      values: {'count': 418},
    );
    await repository.saveEntry(
      owner: 'user-1',
      reportLocalUuid: localReport,
      sectionCode: 'population_households',
      entryType: 'population',
      values: {'count': 445},
      localUuid: entryUuid,
    );

    final entries = await repository.listEntries(
      'user-1',
      localReport,
      'population_households',
    );
    expect(entries, hasLength(1));
    expect(entries.single.values['count'], 445);
    expect(entries.single.syncStatus, 'pending_create');
  });

  test('submitted report cannot be modified through repository', () async {
    await _cacheReport(database, now, status: 'submitted');
    final report = (await repository.listReports('user-1')).single;
    final localReport = await repository.materializeReport('user-1', report);

    await expectLater(
      repository.saveEntry(
        owner: 'user-1',
        reportLocalUuid: localReport,
        sectionCode: 'water',
        entryType: 'source',
        values: const {'source_name': 'Well'},
      ),
      throwsA(isA<ReportReadOnlyFailure>()),
    );
  });

  test('local-only deletion removes entry from the device queue', () async {
    await _cacheReport(database, now);
    final report = (await repository.listReports('user-1')).single;
    final localReport = await repository.materializeReport('user-1', report);
    final entryUuid = await repository.saveEntry(
      owner: 'user-1',
      reportLocalUuid: localReport,
      sectionCode: 'water',
      entryType: 'source',
      values: const {'source_name': 'Well'},
    );

    await repository.deleteEntry(
      owner: 'user-1',
      reportLocalUuid: localReport,
      localUuid: entryUuid,
    );

    expect(await database.select(database.operationalRecords).get(), isEmpty);
  });
}

Future<void> _cacheReport(
  AppDatabase database,
  DateTime now, {
  String status = 'draft',
}) => database
    .into(database.cachedMasterRecords)
    .insert(
      CachedMasterRecordsCompanion.insert(
        ownerUserUuid: 'user-1',
        resourceType: 'report',
        serverUuid: 'report-1',
        villageUuid: const Value('village-a1'),
        payloadJson: jsonEncode({
          'uuid': 'report-1',
          'village_uuid': 'village-a1',
          'reporting_period_uuid': 'period-q2',
          'status': status,
          'completeness_percentage': 10,
          'record_version': 4,
        }),
        recordVersion: 4,
        serverUpdatedAt: now,
        cachedAt: now,
      ),
    );
