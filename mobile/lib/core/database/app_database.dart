import 'dart:convert';
import 'dart:io';

import 'package:drift/drift.dart';
import 'package:drift/native.dart';
import 'package:path/path.dart' as p;
import 'package:path_provider/path_provider.dart';

import 'tables.dart';

part 'app_database.g.dart';

@DriftDatabase(
  tables: [
    CachedReferenceItems,
    CachedMasterRecords,
    DraftReports,
    OperationalRecords,
    PendingAttachments,
    SyncMetadataEntries,
    ConflictRecords,
    LocalSyncLogs,
  ],
)
class AppDatabase extends _$AppDatabase {
  AppDatabase(super.executor);

  factory AppDatabase.encrypted(File file, String encodedKey) {
    final key = base64Url.decode(encodedKey);
    final keyHex = key
        .map((byte) => byte.toRadixString(16).padLeft(2, '0'))
        .join();
    if (key.length != 32) throw StateError('The database key is invalid.');
    return AppDatabase(
      NativeDatabase.createInBackground(
        file,
        setup: (database) {
          database.execute('PRAGMA cipher = chacha20');
          database.execute("PRAGMA key = \"x'$keyHex'\"");
        },
      ),
    );
  }

  @override
  int get schemaVersion => 3;

  @override
  MigrationStrategy get migration => MigrationStrategy(
    onCreate: (migrator) => migrator.createAll(),
    onUpgrade: (migrator, from, to) async {
      if (from < 2) {
        await migrator.addColumn(
          operationalRecords,
          operationalRecords.idempotencyKey,
        );
        await migrator.createTable(localSyncLogs);
      }
      if (from < 3) {
        await migrator.addColumn(
          pendingAttachments,
          pendingAttachments.metadataJson,
        );
        await migrator.addColumn(
          pendingAttachments,
          pendingAttachments.idempotencyKey,
        );
      }
    },
    beforeOpen: (details) async {
      await customStatement('PRAGMA foreign_keys = ON');
      await customStatement('PRAGMA secure_delete = ON');
      await customStatement('PRAGMA journal_mode = WAL');
    },
  );
}

Future<File> mobileDatabaseFile() async {
  final directory = await getApplicationSupportDirectory();
  return File(p.join(directory.path, 'tnk_mobile_v1.sqlite'));
}
