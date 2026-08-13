import 'package:drift/drift.dart';

class CachedReferenceItems extends Table {
  TextColumn get ownerUserUuid => text()();
  TextColumn get resourceType => text()();
  TextColumn get serverUuid => text()();
  TextColumn get payloadJson => text()();
  IntColumn get recordVersion => integer().withDefault(const Constant(1))();
  DateTimeColumn get serverUpdatedAt => dateTime().nullable()();
  DateTimeColumn get cachedAt => dateTime()();

  @override
  Set<Column<Object>> get primaryKey => {
    ownerUserUuid,
    resourceType,
    serverUuid,
  };
}

class CachedMasterRecords extends Table {
  TextColumn get ownerUserUuid => text()();
  TextColumn get resourceType => text()();
  TextColumn get serverUuid => text()();
  TextColumn get villageUuid => text().nullable()();
  TextColumn get confidentialityLevel =>
      text().withDefault(const Constant('internal'))();
  TextColumn get payloadJson => text()();
  IntColumn get recordVersion => integer()();
  DateTimeColumn get serverUpdatedAt => dateTime()();
  DateTimeColumn get cachedAt => dateTime()();

  @override
  Set<Column<Object>> get primaryKey => {
    ownerUserUuid,
    resourceType,
    serverUuid,
  };
}

class DraftReports extends Table {
  TextColumn get localUuid => text()();
  TextColumn get ownerUserUuid => text()();
  TextColumn get serverUuid => text().nullable()();
  TextColumn get villageUuid => text()();
  TextColumn get reportingPeriodUuid => text()();
  TextColumn get payloadJson => text()();
  IntColumn get recordVersion => integer().withDefault(const Constant(0))();
  TextColumn get syncStatus => text()();
  DateTimeColumn get createdAt => dateTime()();
  DateTimeColumn get updatedAt => dateTime()();
  DateTimeColumn get lastSyncedAt => dateTime().nullable()();
  DateTimeColumn get serverUpdatedAt => dateTime().nullable()();
  BoolColumn get deletedLocally =>
      boolean().withDefault(const Constant(false))();
  TextColumn get conflictStatus => text().nullable()();
  TextColumn get syncError => text().nullable()();

  @override
  Set<Column<Object>> get primaryKey => {localUuid};

  @override
  List<Set<Column<Object>>> get uniqueKeys => [
    {ownerUserUuid, serverUuid},
  ];
}

class OperationalRecords extends Table {
  TextColumn get localUuid => text()();
  TextColumn get ownerUserUuid => text()();
  TextColumn get serverUuid => text().nullable()();
  TextColumn get resourceType => text()();
  TextColumn get reportLocalUuid =>
      text().references(DraftReports, #localUuid)();
  TextColumn get payloadJson => text()();
  IntColumn get recordVersion => integer().withDefault(const Constant(0))();
  TextColumn get syncStatus => text()();
  DateTimeColumn get createdAt => dateTime()();
  DateTimeColumn get updatedAt => dateTime()();
  DateTimeColumn get lastSyncedAt => dateTime().nullable()();
  DateTimeColumn get serverUpdatedAt => dateTime().nullable()();
  BoolColumn get deletedLocally =>
      boolean().withDefault(const Constant(false))();
  TextColumn get conflictStatus => text().nullable()();
  TextColumn get syncError => text().nullable()();
  TextColumn get idempotencyKey => text().nullable()();

  @override
  Set<Column<Object>> get primaryKey => {localUuid};

  @override
  List<Set<Column<Object>>> get uniqueKeys => [
    {ownerUserUuid, resourceType, serverUuid},
  ];
}

class PendingAttachments extends Table {
  TextColumn get localUuid => text()();
  TextColumn get ownerUserUuid => text()();
  TextColumn get serverUuid => text().nullable()();
  TextColumn get reportLocalUuid =>
      text().references(DraftReports, #localUuid)();
  TextColumn get localPath => text()();
  TextColumn get mediaType => text()();
  TextColumn get checksumSha256 => text()();
  IntColumn get byteSize => integer()();
  TextColumn get syncStatus => text()();
  IntColumn get retryCount => integer().withDefault(const Constant(0))();
  DateTimeColumn get createdAt => dateTime()();
  DateTimeColumn get updatedAt => dateTime()();
  TextColumn get syncError => text().nullable()();
  TextColumn get metadataJson => text().withDefault(const Constant('{}'))();
  TextColumn get idempotencyKey => text().nullable()();

  @override
  Set<Column<Object>> get primaryKey => {localUuid};

  @override
  List<Set<Column<Object>>> get uniqueKeys => [
    {ownerUserUuid, serverUuid},
  ];
}

class SyncMetadataEntries extends Table {
  TextColumn get ownerUserUuid => text()();
  TextColumn get key => text()();
  TextColumn get value => text().nullable()();
  DateTimeColumn get updatedAt => dateTime()();

  @override
  Set<Column<Object>> get primaryKey => {ownerUserUuid, key};
}

class ConflictRecords extends Table {
  TextColumn get uuid => text()();
  TextColumn get ownerUserUuid => text()();
  TextColumn get resourceType => text()();
  TextColumn get localUuid => text()();
  TextColumn get serverUuid => text().nullable()();
  TextColumn get localPayloadJson => text()();
  TextColumn get serverPayloadJson => text()();
  TextColumn get conflictingFieldsJson => text().nullable()();
  TextColumn get status => text()();
  BoolColumn get serverValueRequired =>
      boolean().withDefault(const Constant(false))();
  DateTimeColumn get detectedAt => dateTime()();
  DateTimeColumn get resolvedAt => dateTime().nullable()();

  @override
  Set<Column<Object>> get primaryKey => {uuid};
}

class LocalSyncLogs extends Table {
  TextColumn get uuid => text()();
  TextColumn get ownerUserUuid => text()();
  DateTimeColumn get startedAt => dateTime()();
  DateTimeColumn get completedAt => dateTime().nullable()();
  IntColumn get uploadedCount => integer().withDefault(const Constant(0))();
  IntColumn get downloadedCount => integer().withDefault(const Constant(0))();
  IntColumn get conflictCount => integer().withDefault(const Constant(0))();
  IntColumn get failedCount => integer().withDefault(const Constant(0))();
  TextColumn get status => text()();
  TextColumn get safeError => text().nullable()();

  @override
  Set<Column<Object>> get primaryKey => {uuid};
}
