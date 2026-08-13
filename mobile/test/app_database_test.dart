import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:tnk_insight_mobile/core/database/app_database.dart';
import 'package:tnk_insight_mobile/core/database/sync_status.dart';

void main() {
  late Directory directory;
  late File file;
  final key = base64UrlEncode(List<int>.generate(32, (index) => index + 1));

  setUp(() async {
    directory = await Directory.systemTemp.createTemp('tnk-drift-test-');
    file = File('${directory.path}${Platform.pathSeparator}mobile.sqlite');
  });

  tearDown(() async {
    if (directory.existsSync()) await directory.delete(recursive: true);
  });

  test('creates every Phase 4 offline table', () async {
    final database = AppDatabase.encrypted(file, key);
    addTearDown(database.close);

    final tables = await database
        .customSelect("SELECT name FROM sqlite_master WHERE type = 'table'")
        .map((row) => row.read<String>('name'))
        .get();

    expect(
      tables,
      containsAll([
        'cached_reference_items',
        'cached_master_records',
        'draft_reports',
        'operational_records',
        'pending_attachments',
        'sync_metadata_entries',
        'conflict_records',
        'local_sync_logs',
      ]),
    );
  });

  test(
    'encrypted draft survives database restart and is user-scoped',
    () async {
      const sensitiveMarker = 'restricted-health-payload-418';
      final now = DateTime.utc(2026, 8, 11);
      var database = AppDatabase.encrypted(file, key);
      await database
          .into(database.draftReports)
          .insert(
            DraftReportsCompanion.insert(
              localUuid: 'local-report-1',
              ownerUserUuid: 'user-a',
              villageUuid: 'village-a1',
              reportingPeriodUuid: '2026-q2',
              payloadJson: '{"note":"$sensitiveMarker"}',
              syncStatus: SyncStatus.localOnly.value,
              createdAt: now,
              updatedAt: now,
            ),
          );
      await database.close();

      expect(
        utf8.decode(file.readAsBytesSync(), allowMalformed: true),
        isNot(contains(sensitiveMarker)),
      );

      database = AppDatabase.encrypted(file, key);
      final ownRecords = await (database.select(
        database.draftReports,
      )..where((row) => row.ownerUserUuid.equals('user-a'))).get();
      final otherRecords = await (database.select(
        database.draftReports,
      )..where((row) => row.ownerUserUuid.equals('user-b'))).get();
      await database.close();

      expect(ownRecords.single.payloadJson, contains(sensitiveMarker));
      expect(otherRecords, isEmpty);
    },
  );

  test('wrong key cannot read an existing database', () async {
    var database = AppDatabase.encrypted(file, key);
    await database.customSelect('SELECT 1').get();
    await database.close();

    final wrongKey = base64UrlEncode(List<int>.filled(32, 255));
    database = AppDatabase.encrypted(file, wrongKey);
    await expectLater(
      database.customSelect('SELECT count(*) FROM sqlite_master').get(),
      throwsA(anything),
    );
    await database.close();
  });
}
