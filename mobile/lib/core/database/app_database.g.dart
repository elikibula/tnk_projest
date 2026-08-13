// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'app_database.dart';

// ignore_for_file: type=lint
class $CachedReferenceItemsTable extends CachedReferenceItems
    with TableInfo<$CachedReferenceItemsTable, CachedReferenceItem> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $CachedReferenceItemsTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _ownerUserUuidMeta = const VerificationMeta(
    'ownerUserUuid',
  );
  @override
  late final GeneratedColumn<String> ownerUserUuid = GeneratedColumn<String>(
    'owner_user_uuid',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _resourceTypeMeta = const VerificationMeta(
    'resourceType',
  );
  @override
  late final GeneratedColumn<String> resourceType = GeneratedColumn<String>(
    'resource_type',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _serverUuidMeta = const VerificationMeta(
    'serverUuid',
  );
  @override
  late final GeneratedColumn<String> serverUuid = GeneratedColumn<String>(
    'server_uuid',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _payloadJsonMeta = const VerificationMeta(
    'payloadJson',
  );
  @override
  late final GeneratedColumn<String> payloadJson = GeneratedColumn<String>(
    'payload_json',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _recordVersionMeta = const VerificationMeta(
    'recordVersion',
  );
  @override
  late final GeneratedColumn<int> recordVersion = GeneratedColumn<int>(
    'record_version',
    aliasedName,
    false,
    type: DriftSqlType.int,
    requiredDuringInsert: false,
    defaultValue: const Constant(1),
  );
  static const VerificationMeta _serverUpdatedAtMeta = const VerificationMeta(
    'serverUpdatedAt',
  );
  @override
  late final GeneratedColumn<DateTime> serverUpdatedAt =
      GeneratedColumn<DateTime>(
        'server_updated_at',
        aliasedName,
        true,
        type: DriftSqlType.dateTime,
        requiredDuringInsert: false,
      );
  static const VerificationMeta _cachedAtMeta = const VerificationMeta(
    'cachedAt',
  );
  @override
  late final GeneratedColumn<DateTime> cachedAt = GeneratedColumn<DateTime>(
    'cached_at',
    aliasedName,
    false,
    type: DriftSqlType.dateTime,
    requiredDuringInsert: true,
  );
  @override
  List<GeneratedColumn> get $columns => [
    ownerUserUuid,
    resourceType,
    serverUuid,
    payloadJson,
    recordVersion,
    serverUpdatedAt,
    cachedAt,
  ];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'cached_reference_items';
  @override
  VerificationContext validateIntegrity(
    Insertable<CachedReferenceItem> instance, {
    bool isInserting = false,
  }) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('owner_user_uuid')) {
      context.handle(
        _ownerUserUuidMeta,
        ownerUserUuid.isAcceptableOrUnknown(
          data['owner_user_uuid']!,
          _ownerUserUuidMeta,
        ),
      );
    } else if (isInserting) {
      context.missing(_ownerUserUuidMeta);
    }
    if (data.containsKey('resource_type')) {
      context.handle(
        _resourceTypeMeta,
        resourceType.isAcceptableOrUnknown(
          data['resource_type']!,
          _resourceTypeMeta,
        ),
      );
    } else if (isInserting) {
      context.missing(_resourceTypeMeta);
    }
    if (data.containsKey('server_uuid')) {
      context.handle(
        _serverUuidMeta,
        serverUuid.isAcceptableOrUnknown(data['server_uuid']!, _serverUuidMeta),
      );
    } else if (isInserting) {
      context.missing(_serverUuidMeta);
    }
    if (data.containsKey('payload_json')) {
      context.handle(
        _payloadJsonMeta,
        payloadJson.isAcceptableOrUnknown(
          data['payload_json']!,
          _payloadJsonMeta,
        ),
      );
    } else if (isInserting) {
      context.missing(_payloadJsonMeta);
    }
    if (data.containsKey('record_version')) {
      context.handle(
        _recordVersionMeta,
        recordVersion.isAcceptableOrUnknown(
          data['record_version']!,
          _recordVersionMeta,
        ),
      );
    }
    if (data.containsKey('server_updated_at')) {
      context.handle(
        _serverUpdatedAtMeta,
        serverUpdatedAt.isAcceptableOrUnknown(
          data['server_updated_at']!,
          _serverUpdatedAtMeta,
        ),
      );
    }
    if (data.containsKey('cached_at')) {
      context.handle(
        _cachedAtMeta,
        cachedAt.isAcceptableOrUnknown(data['cached_at']!, _cachedAtMeta),
      );
    } else if (isInserting) {
      context.missing(_cachedAtMeta);
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {
    ownerUserUuid,
    resourceType,
    serverUuid,
  };
  @override
  CachedReferenceItem map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return CachedReferenceItem(
      ownerUserUuid: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}owner_user_uuid'],
      )!,
      resourceType: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}resource_type'],
      )!,
      serverUuid: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}server_uuid'],
      )!,
      payloadJson: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}payload_json'],
      )!,
      recordVersion: attachedDatabase.typeMapping.read(
        DriftSqlType.int,
        data['${effectivePrefix}record_version'],
      )!,
      serverUpdatedAt: attachedDatabase.typeMapping.read(
        DriftSqlType.dateTime,
        data['${effectivePrefix}server_updated_at'],
      ),
      cachedAt: attachedDatabase.typeMapping.read(
        DriftSqlType.dateTime,
        data['${effectivePrefix}cached_at'],
      )!,
    );
  }

  @override
  $CachedReferenceItemsTable createAlias(String alias) {
    return $CachedReferenceItemsTable(attachedDatabase, alias);
  }
}

class CachedReferenceItem extends DataClass
    implements Insertable<CachedReferenceItem> {
  final String ownerUserUuid;
  final String resourceType;
  final String serverUuid;
  final String payloadJson;
  final int recordVersion;
  final DateTime? serverUpdatedAt;
  final DateTime cachedAt;
  const CachedReferenceItem({
    required this.ownerUserUuid,
    required this.resourceType,
    required this.serverUuid,
    required this.payloadJson,
    required this.recordVersion,
    this.serverUpdatedAt,
    required this.cachedAt,
  });
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['owner_user_uuid'] = Variable<String>(ownerUserUuid);
    map['resource_type'] = Variable<String>(resourceType);
    map['server_uuid'] = Variable<String>(serverUuid);
    map['payload_json'] = Variable<String>(payloadJson);
    map['record_version'] = Variable<int>(recordVersion);
    if (!nullToAbsent || serverUpdatedAt != null) {
      map['server_updated_at'] = Variable<DateTime>(serverUpdatedAt);
    }
    map['cached_at'] = Variable<DateTime>(cachedAt);
    return map;
  }

  CachedReferenceItemsCompanion toCompanion(bool nullToAbsent) {
    return CachedReferenceItemsCompanion(
      ownerUserUuid: Value(ownerUserUuid),
      resourceType: Value(resourceType),
      serverUuid: Value(serverUuid),
      payloadJson: Value(payloadJson),
      recordVersion: Value(recordVersion),
      serverUpdatedAt: serverUpdatedAt == null && nullToAbsent
          ? const Value.absent()
          : Value(serverUpdatedAt),
      cachedAt: Value(cachedAt),
    );
  }

  factory CachedReferenceItem.fromJson(
    Map<String, dynamic> json, {
    ValueSerializer? serializer,
  }) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return CachedReferenceItem(
      ownerUserUuid: serializer.fromJson<String>(json['ownerUserUuid']),
      resourceType: serializer.fromJson<String>(json['resourceType']),
      serverUuid: serializer.fromJson<String>(json['serverUuid']),
      payloadJson: serializer.fromJson<String>(json['payloadJson']),
      recordVersion: serializer.fromJson<int>(json['recordVersion']),
      serverUpdatedAt: serializer.fromJson<DateTime?>(json['serverUpdatedAt']),
      cachedAt: serializer.fromJson<DateTime>(json['cachedAt']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'ownerUserUuid': serializer.toJson<String>(ownerUserUuid),
      'resourceType': serializer.toJson<String>(resourceType),
      'serverUuid': serializer.toJson<String>(serverUuid),
      'payloadJson': serializer.toJson<String>(payloadJson),
      'recordVersion': serializer.toJson<int>(recordVersion),
      'serverUpdatedAt': serializer.toJson<DateTime?>(serverUpdatedAt),
      'cachedAt': serializer.toJson<DateTime>(cachedAt),
    };
  }

  CachedReferenceItem copyWith({
    String? ownerUserUuid,
    String? resourceType,
    String? serverUuid,
    String? payloadJson,
    int? recordVersion,
    Value<DateTime?> serverUpdatedAt = const Value.absent(),
    DateTime? cachedAt,
  }) => CachedReferenceItem(
    ownerUserUuid: ownerUserUuid ?? this.ownerUserUuid,
    resourceType: resourceType ?? this.resourceType,
    serverUuid: serverUuid ?? this.serverUuid,
    payloadJson: payloadJson ?? this.payloadJson,
    recordVersion: recordVersion ?? this.recordVersion,
    serverUpdatedAt: serverUpdatedAt.present
        ? serverUpdatedAt.value
        : this.serverUpdatedAt,
    cachedAt: cachedAt ?? this.cachedAt,
  );
  CachedReferenceItem copyWithCompanion(CachedReferenceItemsCompanion data) {
    return CachedReferenceItem(
      ownerUserUuid: data.ownerUserUuid.present
          ? data.ownerUserUuid.value
          : this.ownerUserUuid,
      resourceType: data.resourceType.present
          ? data.resourceType.value
          : this.resourceType,
      serverUuid: data.serverUuid.present
          ? data.serverUuid.value
          : this.serverUuid,
      payloadJson: data.payloadJson.present
          ? data.payloadJson.value
          : this.payloadJson,
      recordVersion: data.recordVersion.present
          ? data.recordVersion.value
          : this.recordVersion,
      serverUpdatedAt: data.serverUpdatedAt.present
          ? data.serverUpdatedAt.value
          : this.serverUpdatedAt,
      cachedAt: data.cachedAt.present ? data.cachedAt.value : this.cachedAt,
    );
  }

  @override
  String toString() {
    return (StringBuffer('CachedReferenceItem(')
          ..write('ownerUserUuid: $ownerUserUuid, ')
          ..write('resourceType: $resourceType, ')
          ..write('serverUuid: $serverUuid, ')
          ..write('payloadJson: $payloadJson, ')
          ..write('recordVersion: $recordVersion, ')
          ..write('serverUpdatedAt: $serverUpdatedAt, ')
          ..write('cachedAt: $cachedAt')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(
    ownerUserUuid,
    resourceType,
    serverUuid,
    payloadJson,
    recordVersion,
    serverUpdatedAt,
    cachedAt,
  );
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is CachedReferenceItem &&
          other.ownerUserUuid == this.ownerUserUuid &&
          other.resourceType == this.resourceType &&
          other.serverUuid == this.serverUuid &&
          other.payloadJson == this.payloadJson &&
          other.recordVersion == this.recordVersion &&
          other.serverUpdatedAt == this.serverUpdatedAt &&
          other.cachedAt == this.cachedAt);
}

class CachedReferenceItemsCompanion
    extends UpdateCompanion<CachedReferenceItem> {
  final Value<String> ownerUserUuid;
  final Value<String> resourceType;
  final Value<String> serverUuid;
  final Value<String> payloadJson;
  final Value<int> recordVersion;
  final Value<DateTime?> serverUpdatedAt;
  final Value<DateTime> cachedAt;
  final Value<int> rowid;
  const CachedReferenceItemsCompanion({
    this.ownerUserUuid = const Value.absent(),
    this.resourceType = const Value.absent(),
    this.serverUuid = const Value.absent(),
    this.payloadJson = const Value.absent(),
    this.recordVersion = const Value.absent(),
    this.serverUpdatedAt = const Value.absent(),
    this.cachedAt = const Value.absent(),
    this.rowid = const Value.absent(),
  });
  CachedReferenceItemsCompanion.insert({
    required String ownerUserUuid,
    required String resourceType,
    required String serverUuid,
    required String payloadJson,
    this.recordVersion = const Value.absent(),
    this.serverUpdatedAt = const Value.absent(),
    required DateTime cachedAt,
    this.rowid = const Value.absent(),
  }) : ownerUserUuid = Value(ownerUserUuid),
       resourceType = Value(resourceType),
       serverUuid = Value(serverUuid),
       payloadJson = Value(payloadJson),
       cachedAt = Value(cachedAt);
  static Insertable<CachedReferenceItem> custom({
    Expression<String>? ownerUserUuid,
    Expression<String>? resourceType,
    Expression<String>? serverUuid,
    Expression<String>? payloadJson,
    Expression<int>? recordVersion,
    Expression<DateTime>? serverUpdatedAt,
    Expression<DateTime>? cachedAt,
    Expression<int>? rowid,
  }) {
    return RawValuesInsertable({
      if (ownerUserUuid != null) 'owner_user_uuid': ownerUserUuid,
      if (resourceType != null) 'resource_type': resourceType,
      if (serverUuid != null) 'server_uuid': serverUuid,
      if (payloadJson != null) 'payload_json': payloadJson,
      if (recordVersion != null) 'record_version': recordVersion,
      if (serverUpdatedAt != null) 'server_updated_at': serverUpdatedAt,
      if (cachedAt != null) 'cached_at': cachedAt,
      if (rowid != null) 'rowid': rowid,
    });
  }

  CachedReferenceItemsCompanion copyWith({
    Value<String>? ownerUserUuid,
    Value<String>? resourceType,
    Value<String>? serverUuid,
    Value<String>? payloadJson,
    Value<int>? recordVersion,
    Value<DateTime?>? serverUpdatedAt,
    Value<DateTime>? cachedAt,
    Value<int>? rowid,
  }) {
    return CachedReferenceItemsCompanion(
      ownerUserUuid: ownerUserUuid ?? this.ownerUserUuid,
      resourceType: resourceType ?? this.resourceType,
      serverUuid: serverUuid ?? this.serverUuid,
      payloadJson: payloadJson ?? this.payloadJson,
      recordVersion: recordVersion ?? this.recordVersion,
      serverUpdatedAt: serverUpdatedAt ?? this.serverUpdatedAt,
      cachedAt: cachedAt ?? this.cachedAt,
      rowid: rowid ?? this.rowid,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (ownerUserUuid.present) {
      map['owner_user_uuid'] = Variable<String>(ownerUserUuid.value);
    }
    if (resourceType.present) {
      map['resource_type'] = Variable<String>(resourceType.value);
    }
    if (serverUuid.present) {
      map['server_uuid'] = Variable<String>(serverUuid.value);
    }
    if (payloadJson.present) {
      map['payload_json'] = Variable<String>(payloadJson.value);
    }
    if (recordVersion.present) {
      map['record_version'] = Variable<int>(recordVersion.value);
    }
    if (serverUpdatedAt.present) {
      map['server_updated_at'] = Variable<DateTime>(serverUpdatedAt.value);
    }
    if (cachedAt.present) {
      map['cached_at'] = Variable<DateTime>(cachedAt.value);
    }
    if (rowid.present) {
      map['rowid'] = Variable<int>(rowid.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('CachedReferenceItemsCompanion(')
          ..write('ownerUserUuid: $ownerUserUuid, ')
          ..write('resourceType: $resourceType, ')
          ..write('serverUuid: $serverUuid, ')
          ..write('payloadJson: $payloadJson, ')
          ..write('recordVersion: $recordVersion, ')
          ..write('serverUpdatedAt: $serverUpdatedAt, ')
          ..write('cachedAt: $cachedAt, ')
          ..write('rowid: $rowid')
          ..write(')'))
        .toString();
  }
}

class $CachedMasterRecordsTable extends CachedMasterRecords
    with TableInfo<$CachedMasterRecordsTable, CachedMasterRecord> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $CachedMasterRecordsTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _ownerUserUuidMeta = const VerificationMeta(
    'ownerUserUuid',
  );
  @override
  late final GeneratedColumn<String> ownerUserUuid = GeneratedColumn<String>(
    'owner_user_uuid',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _resourceTypeMeta = const VerificationMeta(
    'resourceType',
  );
  @override
  late final GeneratedColumn<String> resourceType = GeneratedColumn<String>(
    'resource_type',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _serverUuidMeta = const VerificationMeta(
    'serverUuid',
  );
  @override
  late final GeneratedColumn<String> serverUuid = GeneratedColumn<String>(
    'server_uuid',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _villageUuidMeta = const VerificationMeta(
    'villageUuid',
  );
  @override
  late final GeneratedColumn<String> villageUuid = GeneratedColumn<String>(
    'village_uuid',
    aliasedName,
    true,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
  );
  static const VerificationMeta _confidentialityLevelMeta =
      const VerificationMeta('confidentialityLevel');
  @override
  late final GeneratedColumn<String> confidentialityLevel =
      GeneratedColumn<String>(
        'confidentiality_level',
        aliasedName,
        false,
        type: DriftSqlType.string,
        requiredDuringInsert: false,
        defaultValue: const Constant('internal'),
      );
  static const VerificationMeta _payloadJsonMeta = const VerificationMeta(
    'payloadJson',
  );
  @override
  late final GeneratedColumn<String> payloadJson = GeneratedColumn<String>(
    'payload_json',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _recordVersionMeta = const VerificationMeta(
    'recordVersion',
  );
  @override
  late final GeneratedColumn<int> recordVersion = GeneratedColumn<int>(
    'record_version',
    aliasedName,
    false,
    type: DriftSqlType.int,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _serverUpdatedAtMeta = const VerificationMeta(
    'serverUpdatedAt',
  );
  @override
  late final GeneratedColumn<DateTime> serverUpdatedAt =
      GeneratedColumn<DateTime>(
        'server_updated_at',
        aliasedName,
        false,
        type: DriftSqlType.dateTime,
        requiredDuringInsert: true,
      );
  static const VerificationMeta _cachedAtMeta = const VerificationMeta(
    'cachedAt',
  );
  @override
  late final GeneratedColumn<DateTime> cachedAt = GeneratedColumn<DateTime>(
    'cached_at',
    aliasedName,
    false,
    type: DriftSqlType.dateTime,
    requiredDuringInsert: true,
  );
  @override
  List<GeneratedColumn> get $columns => [
    ownerUserUuid,
    resourceType,
    serverUuid,
    villageUuid,
    confidentialityLevel,
    payloadJson,
    recordVersion,
    serverUpdatedAt,
    cachedAt,
  ];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'cached_master_records';
  @override
  VerificationContext validateIntegrity(
    Insertable<CachedMasterRecord> instance, {
    bool isInserting = false,
  }) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('owner_user_uuid')) {
      context.handle(
        _ownerUserUuidMeta,
        ownerUserUuid.isAcceptableOrUnknown(
          data['owner_user_uuid']!,
          _ownerUserUuidMeta,
        ),
      );
    } else if (isInserting) {
      context.missing(_ownerUserUuidMeta);
    }
    if (data.containsKey('resource_type')) {
      context.handle(
        _resourceTypeMeta,
        resourceType.isAcceptableOrUnknown(
          data['resource_type']!,
          _resourceTypeMeta,
        ),
      );
    } else if (isInserting) {
      context.missing(_resourceTypeMeta);
    }
    if (data.containsKey('server_uuid')) {
      context.handle(
        _serverUuidMeta,
        serverUuid.isAcceptableOrUnknown(data['server_uuid']!, _serverUuidMeta),
      );
    } else if (isInserting) {
      context.missing(_serverUuidMeta);
    }
    if (data.containsKey('village_uuid')) {
      context.handle(
        _villageUuidMeta,
        villageUuid.isAcceptableOrUnknown(
          data['village_uuid']!,
          _villageUuidMeta,
        ),
      );
    }
    if (data.containsKey('confidentiality_level')) {
      context.handle(
        _confidentialityLevelMeta,
        confidentialityLevel.isAcceptableOrUnknown(
          data['confidentiality_level']!,
          _confidentialityLevelMeta,
        ),
      );
    }
    if (data.containsKey('payload_json')) {
      context.handle(
        _payloadJsonMeta,
        payloadJson.isAcceptableOrUnknown(
          data['payload_json']!,
          _payloadJsonMeta,
        ),
      );
    } else if (isInserting) {
      context.missing(_payloadJsonMeta);
    }
    if (data.containsKey('record_version')) {
      context.handle(
        _recordVersionMeta,
        recordVersion.isAcceptableOrUnknown(
          data['record_version']!,
          _recordVersionMeta,
        ),
      );
    } else if (isInserting) {
      context.missing(_recordVersionMeta);
    }
    if (data.containsKey('server_updated_at')) {
      context.handle(
        _serverUpdatedAtMeta,
        serverUpdatedAt.isAcceptableOrUnknown(
          data['server_updated_at']!,
          _serverUpdatedAtMeta,
        ),
      );
    } else if (isInserting) {
      context.missing(_serverUpdatedAtMeta);
    }
    if (data.containsKey('cached_at')) {
      context.handle(
        _cachedAtMeta,
        cachedAt.isAcceptableOrUnknown(data['cached_at']!, _cachedAtMeta),
      );
    } else if (isInserting) {
      context.missing(_cachedAtMeta);
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {
    ownerUserUuid,
    resourceType,
    serverUuid,
  };
  @override
  CachedMasterRecord map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return CachedMasterRecord(
      ownerUserUuid: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}owner_user_uuid'],
      )!,
      resourceType: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}resource_type'],
      )!,
      serverUuid: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}server_uuid'],
      )!,
      villageUuid: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}village_uuid'],
      ),
      confidentialityLevel: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}confidentiality_level'],
      )!,
      payloadJson: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}payload_json'],
      )!,
      recordVersion: attachedDatabase.typeMapping.read(
        DriftSqlType.int,
        data['${effectivePrefix}record_version'],
      )!,
      serverUpdatedAt: attachedDatabase.typeMapping.read(
        DriftSqlType.dateTime,
        data['${effectivePrefix}server_updated_at'],
      )!,
      cachedAt: attachedDatabase.typeMapping.read(
        DriftSqlType.dateTime,
        data['${effectivePrefix}cached_at'],
      )!,
    );
  }

  @override
  $CachedMasterRecordsTable createAlias(String alias) {
    return $CachedMasterRecordsTable(attachedDatabase, alias);
  }
}

class CachedMasterRecord extends DataClass
    implements Insertable<CachedMasterRecord> {
  final String ownerUserUuid;
  final String resourceType;
  final String serverUuid;
  final String? villageUuid;
  final String confidentialityLevel;
  final String payloadJson;
  final int recordVersion;
  final DateTime serverUpdatedAt;
  final DateTime cachedAt;
  const CachedMasterRecord({
    required this.ownerUserUuid,
    required this.resourceType,
    required this.serverUuid,
    this.villageUuid,
    required this.confidentialityLevel,
    required this.payloadJson,
    required this.recordVersion,
    required this.serverUpdatedAt,
    required this.cachedAt,
  });
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['owner_user_uuid'] = Variable<String>(ownerUserUuid);
    map['resource_type'] = Variable<String>(resourceType);
    map['server_uuid'] = Variable<String>(serverUuid);
    if (!nullToAbsent || villageUuid != null) {
      map['village_uuid'] = Variable<String>(villageUuid);
    }
    map['confidentiality_level'] = Variable<String>(confidentialityLevel);
    map['payload_json'] = Variable<String>(payloadJson);
    map['record_version'] = Variable<int>(recordVersion);
    map['server_updated_at'] = Variable<DateTime>(serverUpdatedAt);
    map['cached_at'] = Variable<DateTime>(cachedAt);
    return map;
  }

  CachedMasterRecordsCompanion toCompanion(bool nullToAbsent) {
    return CachedMasterRecordsCompanion(
      ownerUserUuid: Value(ownerUserUuid),
      resourceType: Value(resourceType),
      serverUuid: Value(serverUuid),
      villageUuid: villageUuid == null && nullToAbsent
          ? const Value.absent()
          : Value(villageUuid),
      confidentialityLevel: Value(confidentialityLevel),
      payloadJson: Value(payloadJson),
      recordVersion: Value(recordVersion),
      serverUpdatedAt: Value(serverUpdatedAt),
      cachedAt: Value(cachedAt),
    );
  }

  factory CachedMasterRecord.fromJson(
    Map<String, dynamic> json, {
    ValueSerializer? serializer,
  }) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return CachedMasterRecord(
      ownerUserUuid: serializer.fromJson<String>(json['ownerUserUuid']),
      resourceType: serializer.fromJson<String>(json['resourceType']),
      serverUuid: serializer.fromJson<String>(json['serverUuid']),
      villageUuid: serializer.fromJson<String?>(json['villageUuid']),
      confidentialityLevel: serializer.fromJson<String>(
        json['confidentialityLevel'],
      ),
      payloadJson: serializer.fromJson<String>(json['payloadJson']),
      recordVersion: serializer.fromJson<int>(json['recordVersion']),
      serverUpdatedAt: serializer.fromJson<DateTime>(json['serverUpdatedAt']),
      cachedAt: serializer.fromJson<DateTime>(json['cachedAt']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'ownerUserUuid': serializer.toJson<String>(ownerUserUuid),
      'resourceType': serializer.toJson<String>(resourceType),
      'serverUuid': serializer.toJson<String>(serverUuid),
      'villageUuid': serializer.toJson<String?>(villageUuid),
      'confidentialityLevel': serializer.toJson<String>(confidentialityLevel),
      'payloadJson': serializer.toJson<String>(payloadJson),
      'recordVersion': serializer.toJson<int>(recordVersion),
      'serverUpdatedAt': serializer.toJson<DateTime>(serverUpdatedAt),
      'cachedAt': serializer.toJson<DateTime>(cachedAt),
    };
  }

  CachedMasterRecord copyWith({
    String? ownerUserUuid,
    String? resourceType,
    String? serverUuid,
    Value<String?> villageUuid = const Value.absent(),
    String? confidentialityLevel,
    String? payloadJson,
    int? recordVersion,
    DateTime? serverUpdatedAt,
    DateTime? cachedAt,
  }) => CachedMasterRecord(
    ownerUserUuid: ownerUserUuid ?? this.ownerUserUuid,
    resourceType: resourceType ?? this.resourceType,
    serverUuid: serverUuid ?? this.serverUuid,
    villageUuid: villageUuid.present ? villageUuid.value : this.villageUuid,
    confidentialityLevel: confidentialityLevel ?? this.confidentialityLevel,
    payloadJson: payloadJson ?? this.payloadJson,
    recordVersion: recordVersion ?? this.recordVersion,
    serverUpdatedAt: serverUpdatedAt ?? this.serverUpdatedAt,
    cachedAt: cachedAt ?? this.cachedAt,
  );
  CachedMasterRecord copyWithCompanion(CachedMasterRecordsCompanion data) {
    return CachedMasterRecord(
      ownerUserUuid: data.ownerUserUuid.present
          ? data.ownerUserUuid.value
          : this.ownerUserUuid,
      resourceType: data.resourceType.present
          ? data.resourceType.value
          : this.resourceType,
      serverUuid: data.serverUuid.present
          ? data.serverUuid.value
          : this.serverUuid,
      villageUuid: data.villageUuid.present
          ? data.villageUuid.value
          : this.villageUuid,
      confidentialityLevel: data.confidentialityLevel.present
          ? data.confidentialityLevel.value
          : this.confidentialityLevel,
      payloadJson: data.payloadJson.present
          ? data.payloadJson.value
          : this.payloadJson,
      recordVersion: data.recordVersion.present
          ? data.recordVersion.value
          : this.recordVersion,
      serverUpdatedAt: data.serverUpdatedAt.present
          ? data.serverUpdatedAt.value
          : this.serverUpdatedAt,
      cachedAt: data.cachedAt.present ? data.cachedAt.value : this.cachedAt,
    );
  }

  @override
  String toString() {
    return (StringBuffer('CachedMasterRecord(')
          ..write('ownerUserUuid: $ownerUserUuid, ')
          ..write('resourceType: $resourceType, ')
          ..write('serverUuid: $serverUuid, ')
          ..write('villageUuid: $villageUuid, ')
          ..write('confidentialityLevel: $confidentialityLevel, ')
          ..write('payloadJson: $payloadJson, ')
          ..write('recordVersion: $recordVersion, ')
          ..write('serverUpdatedAt: $serverUpdatedAt, ')
          ..write('cachedAt: $cachedAt')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(
    ownerUserUuid,
    resourceType,
    serverUuid,
    villageUuid,
    confidentialityLevel,
    payloadJson,
    recordVersion,
    serverUpdatedAt,
    cachedAt,
  );
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is CachedMasterRecord &&
          other.ownerUserUuid == this.ownerUserUuid &&
          other.resourceType == this.resourceType &&
          other.serverUuid == this.serverUuid &&
          other.villageUuid == this.villageUuid &&
          other.confidentialityLevel == this.confidentialityLevel &&
          other.payloadJson == this.payloadJson &&
          other.recordVersion == this.recordVersion &&
          other.serverUpdatedAt == this.serverUpdatedAt &&
          other.cachedAt == this.cachedAt);
}

class CachedMasterRecordsCompanion extends UpdateCompanion<CachedMasterRecord> {
  final Value<String> ownerUserUuid;
  final Value<String> resourceType;
  final Value<String> serverUuid;
  final Value<String?> villageUuid;
  final Value<String> confidentialityLevel;
  final Value<String> payloadJson;
  final Value<int> recordVersion;
  final Value<DateTime> serverUpdatedAt;
  final Value<DateTime> cachedAt;
  final Value<int> rowid;
  const CachedMasterRecordsCompanion({
    this.ownerUserUuid = const Value.absent(),
    this.resourceType = const Value.absent(),
    this.serverUuid = const Value.absent(),
    this.villageUuid = const Value.absent(),
    this.confidentialityLevel = const Value.absent(),
    this.payloadJson = const Value.absent(),
    this.recordVersion = const Value.absent(),
    this.serverUpdatedAt = const Value.absent(),
    this.cachedAt = const Value.absent(),
    this.rowid = const Value.absent(),
  });
  CachedMasterRecordsCompanion.insert({
    required String ownerUserUuid,
    required String resourceType,
    required String serverUuid,
    this.villageUuid = const Value.absent(),
    this.confidentialityLevel = const Value.absent(),
    required String payloadJson,
    required int recordVersion,
    required DateTime serverUpdatedAt,
    required DateTime cachedAt,
    this.rowid = const Value.absent(),
  }) : ownerUserUuid = Value(ownerUserUuid),
       resourceType = Value(resourceType),
       serverUuid = Value(serverUuid),
       payloadJson = Value(payloadJson),
       recordVersion = Value(recordVersion),
       serverUpdatedAt = Value(serverUpdatedAt),
       cachedAt = Value(cachedAt);
  static Insertable<CachedMasterRecord> custom({
    Expression<String>? ownerUserUuid,
    Expression<String>? resourceType,
    Expression<String>? serverUuid,
    Expression<String>? villageUuid,
    Expression<String>? confidentialityLevel,
    Expression<String>? payloadJson,
    Expression<int>? recordVersion,
    Expression<DateTime>? serverUpdatedAt,
    Expression<DateTime>? cachedAt,
    Expression<int>? rowid,
  }) {
    return RawValuesInsertable({
      if (ownerUserUuid != null) 'owner_user_uuid': ownerUserUuid,
      if (resourceType != null) 'resource_type': resourceType,
      if (serverUuid != null) 'server_uuid': serverUuid,
      if (villageUuid != null) 'village_uuid': villageUuid,
      if (confidentialityLevel != null)
        'confidentiality_level': confidentialityLevel,
      if (payloadJson != null) 'payload_json': payloadJson,
      if (recordVersion != null) 'record_version': recordVersion,
      if (serverUpdatedAt != null) 'server_updated_at': serverUpdatedAt,
      if (cachedAt != null) 'cached_at': cachedAt,
      if (rowid != null) 'rowid': rowid,
    });
  }

  CachedMasterRecordsCompanion copyWith({
    Value<String>? ownerUserUuid,
    Value<String>? resourceType,
    Value<String>? serverUuid,
    Value<String?>? villageUuid,
    Value<String>? confidentialityLevel,
    Value<String>? payloadJson,
    Value<int>? recordVersion,
    Value<DateTime>? serverUpdatedAt,
    Value<DateTime>? cachedAt,
    Value<int>? rowid,
  }) {
    return CachedMasterRecordsCompanion(
      ownerUserUuid: ownerUserUuid ?? this.ownerUserUuid,
      resourceType: resourceType ?? this.resourceType,
      serverUuid: serverUuid ?? this.serverUuid,
      villageUuid: villageUuid ?? this.villageUuid,
      confidentialityLevel: confidentialityLevel ?? this.confidentialityLevel,
      payloadJson: payloadJson ?? this.payloadJson,
      recordVersion: recordVersion ?? this.recordVersion,
      serverUpdatedAt: serverUpdatedAt ?? this.serverUpdatedAt,
      cachedAt: cachedAt ?? this.cachedAt,
      rowid: rowid ?? this.rowid,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (ownerUserUuid.present) {
      map['owner_user_uuid'] = Variable<String>(ownerUserUuid.value);
    }
    if (resourceType.present) {
      map['resource_type'] = Variable<String>(resourceType.value);
    }
    if (serverUuid.present) {
      map['server_uuid'] = Variable<String>(serverUuid.value);
    }
    if (villageUuid.present) {
      map['village_uuid'] = Variable<String>(villageUuid.value);
    }
    if (confidentialityLevel.present) {
      map['confidentiality_level'] = Variable<String>(
        confidentialityLevel.value,
      );
    }
    if (payloadJson.present) {
      map['payload_json'] = Variable<String>(payloadJson.value);
    }
    if (recordVersion.present) {
      map['record_version'] = Variable<int>(recordVersion.value);
    }
    if (serverUpdatedAt.present) {
      map['server_updated_at'] = Variable<DateTime>(serverUpdatedAt.value);
    }
    if (cachedAt.present) {
      map['cached_at'] = Variable<DateTime>(cachedAt.value);
    }
    if (rowid.present) {
      map['rowid'] = Variable<int>(rowid.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('CachedMasterRecordsCompanion(')
          ..write('ownerUserUuid: $ownerUserUuid, ')
          ..write('resourceType: $resourceType, ')
          ..write('serverUuid: $serverUuid, ')
          ..write('villageUuid: $villageUuid, ')
          ..write('confidentialityLevel: $confidentialityLevel, ')
          ..write('payloadJson: $payloadJson, ')
          ..write('recordVersion: $recordVersion, ')
          ..write('serverUpdatedAt: $serverUpdatedAt, ')
          ..write('cachedAt: $cachedAt, ')
          ..write('rowid: $rowid')
          ..write(')'))
        .toString();
  }
}

class $DraftReportsTable extends DraftReports
    with TableInfo<$DraftReportsTable, DraftReport> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $DraftReportsTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _localUuidMeta = const VerificationMeta(
    'localUuid',
  );
  @override
  late final GeneratedColumn<String> localUuid = GeneratedColumn<String>(
    'local_uuid',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _ownerUserUuidMeta = const VerificationMeta(
    'ownerUserUuid',
  );
  @override
  late final GeneratedColumn<String> ownerUserUuid = GeneratedColumn<String>(
    'owner_user_uuid',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _serverUuidMeta = const VerificationMeta(
    'serverUuid',
  );
  @override
  late final GeneratedColumn<String> serverUuid = GeneratedColumn<String>(
    'server_uuid',
    aliasedName,
    true,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
  );
  static const VerificationMeta _villageUuidMeta = const VerificationMeta(
    'villageUuid',
  );
  @override
  late final GeneratedColumn<String> villageUuid = GeneratedColumn<String>(
    'village_uuid',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _reportingPeriodUuidMeta =
      const VerificationMeta('reportingPeriodUuid');
  @override
  late final GeneratedColumn<String> reportingPeriodUuid =
      GeneratedColumn<String>(
        'reporting_period_uuid',
        aliasedName,
        false,
        type: DriftSqlType.string,
        requiredDuringInsert: true,
      );
  static const VerificationMeta _payloadJsonMeta = const VerificationMeta(
    'payloadJson',
  );
  @override
  late final GeneratedColumn<String> payloadJson = GeneratedColumn<String>(
    'payload_json',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _recordVersionMeta = const VerificationMeta(
    'recordVersion',
  );
  @override
  late final GeneratedColumn<int> recordVersion = GeneratedColumn<int>(
    'record_version',
    aliasedName,
    false,
    type: DriftSqlType.int,
    requiredDuringInsert: false,
    defaultValue: const Constant(0),
  );
  static const VerificationMeta _syncStatusMeta = const VerificationMeta(
    'syncStatus',
  );
  @override
  late final GeneratedColumn<String> syncStatus = GeneratedColumn<String>(
    'sync_status',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _createdAtMeta = const VerificationMeta(
    'createdAt',
  );
  @override
  late final GeneratedColumn<DateTime> createdAt = GeneratedColumn<DateTime>(
    'created_at',
    aliasedName,
    false,
    type: DriftSqlType.dateTime,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _updatedAtMeta = const VerificationMeta(
    'updatedAt',
  );
  @override
  late final GeneratedColumn<DateTime> updatedAt = GeneratedColumn<DateTime>(
    'updated_at',
    aliasedName,
    false,
    type: DriftSqlType.dateTime,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _lastSyncedAtMeta = const VerificationMeta(
    'lastSyncedAt',
  );
  @override
  late final GeneratedColumn<DateTime> lastSyncedAt = GeneratedColumn<DateTime>(
    'last_synced_at',
    aliasedName,
    true,
    type: DriftSqlType.dateTime,
    requiredDuringInsert: false,
  );
  static const VerificationMeta _serverUpdatedAtMeta = const VerificationMeta(
    'serverUpdatedAt',
  );
  @override
  late final GeneratedColumn<DateTime> serverUpdatedAt =
      GeneratedColumn<DateTime>(
        'server_updated_at',
        aliasedName,
        true,
        type: DriftSqlType.dateTime,
        requiredDuringInsert: false,
      );
  static const VerificationMeta _deletedLocallyMeta = const VerificationMeta(
    'deletedLocally',
  );
  @override
  late final GeneratedColumn<bool> deletedLocally = GeneratedColumn<bool>(
    'deleted_locally',
    aliasedName,
    false,
    type: DriftSqlType.bool,
    requiredDuringInsert: false,
    defaultConstraints: GeneratedColumn.constraintIsAlways(
      'CHECK ("deleted_locally" IN (0, 1))',
    ),
    defaultValue: const Constant(false),
  );
  static const VerificationMeta _conflictStatusMeta = const VerificationMeta(
    'conflictStatus',
  );
  @override
  late final GeneratedColumn<String> conflictStatus = GeneratedColumn<String>(
    'conflict_status',
    aliasedName,
    true,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
  );
  static const VerificationMeta _syncErrorMeta = const VerificationMeta(
    'syncError',
  );
  @override
  late final GeneratedColumn<String> syncError = GeneratedColumn<String>(
    'sync_error',
    aliasedName,
    true,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
  );
  @override
  List<GeneratedColumn> get $columns => [
    localUuid,
    ownerUserUuid,
    serverUuid,
    villageUuid,
    reportingPeriodUuid,
    payloadJson,
    recordVersion,
    syncStatus,
    createdAt,
    updatedAt,
    lastSyncedAt,
    serverUpdatedAt,
    deletedLocally,
    conflictStatus,
    syncError,
  ];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'draft_reports';
  @override
  VerificationContext validateIntegrity(
    Insertable<DraftReport> instance, {
    bool isInserting = false,
  }) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('local_uuid')) {
      context.handle(
        _localUuidMeta,
        localUuid.isAcceptableOrUnknown(data['local_uuid']!, _localUuidMeta),
      );
    } else if (isInserting) {
      context.missing(_localUuidMeta);
    }
    if (data.containsKey('owner_user_uuid')) {
      context.handle(
        _ownerUserUuidMeta,
        ownerUserUuid.isAcceptableOrUnknown(
          data['owner_user_uuid']!,
          _ownerUserUuidMeta,
        ),
      );
    } else if (isInserting) {
      context.missing(_ownerUserUuidMeta);
    }
    if (data.containsKey('server_uuid')) {
      context.handle(
        _serverUuidMeta,
        serverUuid.isAcceptableOrUnknown(data['server_uuid']!, _serverUuidMeta),
      );
    }
    if (data.containsKey('village_uuid')) {
      context.handle(
        _villageUuidMeta,
        villageUuid.isAcceptableOrUnknown(
          data['village_uuid']!,
          _villageUuidMeta,
        ),
      );
    } else if (isInserting) {
      context.missing(_villageUuidMeta);
    }
    if (data.containsKey('reporting_period_uuid')) {
      context.handle(
        _reportingPeriodUuidMeta,
        reportingPeriodUuid.isAcceptableOrUnknown(
          data['reporting_period_uuid']!,
          _reportingPeriodUuidMeta,
        ),
      );
    } else if (isInserting) {
      context.missing(_reportingPeriodUuidMeta);
    }
    if (data.containsKey('payload_json')) {
      context.handle(
        _payloadJsonMeta,
        payloadJson.isAcceptableOrUnknown(
          data['payload_json']!,
          _payloadJsonMeta,
        ),
      );
    } else if (isInserting) {
      context.missing(_payloadJsonMeta);
    }
    if (data.containsKey('record_version')) {
      context.handle(
        _recordVersionMeta,
        recordVersion.isAcceptableOrUnknown(
          data['record_version']!,
          _recordVersionMeta,
        ),
      );
    }
    if (data.containsKey('sync_status')) {
      context.handle(
        _syncStatusMeta,
        syncStatus.isAcceptableOrUnknown(data['sync_status']!, _syncStatusMeta),
      );
    } else if (isInserting) {
      context.missing(_syncStatusMeta);
    }
    if (data.containsKey('created_at')) {
      context.handle(
        _createdAtMeta,
        createdAt.isAcceptableOrUnknown(data['created_at']!, _createdAtMeta),
      );
    } else if (isInserting) {
      context.missing(_createdAtMeta);
    }
    if (data.containsKey('updated_at')) {
      context.handle(
        _updatedAtMeta,
        updatedAt.isAcceptableOrUnknown(data['updated_at']!, _updatedAtMeta),
      );
    } else if (isInserting) {
      context.missing(_updatedAtMeta);
    }
    if (data.containsKey('last_synced_at')) {
      context.handle(
        _lastSyncedAtMeta,
        lastSyncedAt.isAcceptableOrUnknown(
          data['last_synced_at']!,
          _lastSyncedAtMeta,
        ),
      );
    }
    if (data.containsKey('server_updated_at')) {
      context.handle(
        _serverUpdatedAtMeta,
        serverUpdatedAt.isAcceptableOrUnknown(
          data['server_updated_at']!,
          _serverUpdatedAtMeta,
        ),
      );
    }
    if (data.containsKey('deleted_locally')) {
      context.handle(
        _deletedLocallyMeta,
        deletedLocally.isAcceptableOrUnknown(
          data['deleted_locally']!,
          _deletedLocallyMeta,
        ),
      );
    }
    if (data.containsKey('conflict_status')) {
      context.handle(
        _conflictStatusMeta,
        conflictStatus.isAcceptableOrUnknown(
          data['conflict_status']!,
          _conflictStatusMeta,
        ),
      );
    }
    if (data.containsKey('sync_error')) {
      context.handle(
        _syncErrorMeta,
        syncError.isAcceptableOrUnknown(data['sync_error']!, _syncErrorMeta),
      );
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {localUuid};
  @override
  List<Set<GeneratedColumn>> get uniqueKeys => [
    {ownerUserUuid, serverUuid},
  ];
  @override
  DraftReport map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return DraftReport(
      localUuid: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}local_uuid'],
      )!,
      ownerUserUuid: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}owner_user_uuid'],
      )!,
      serverUuid: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}server_uuid'],
      ),
      villageUuid: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}village_uuid'],
      )!,
      reportingPeriodUuid: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}reporting_period_uuid'],
      )!,
      payloadJson: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}payload_json'],
      )!,
      recordVersion: attachedDatabase.typeMapping.read(
        DriftSqlType.int,
        data['${effectivePrefix}record_version'],
      )!,
      syncStatus: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}sync_status'],
      )!,
      createdAt: attachedDatabase.typeMapping.read(
        DriftSqlType.dateTime,
        data['${effectivePrefix}created_at'],
      )!,
      updatedAt: attachedDatabase.typeMapping.read(
        DriftSqlType.dateTime,
        data['${effectivePrefix}updated_at'],
      )!,
      lastSyncedAt: attachedDatabase.typeMapping.read(
        DriftSqlType.dateTime,
        data['${effectivePrefix}last_synced_at'],
      ),
      serverUpdatedAt: attachedDatabase.typeMapping.read(
        DriftSqlType.dateTime,
        data['${effectivePrefix}server_updated_at'],
      ),
      deletedLocally: attachedDatabase.typeMapping.read(
        DriftSqlType.bool,
        data['${effectivePrefix}deleted_locally'],
      )!,
      conflictStatus: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}conflict_status'],
      ),
      syncError: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}sync_error'],
      ),
    );
  }

  @override
  $DraftReportsTable createAlias(String alias) {
    return $DraftReportsTable(attachedDatabase, alias);
  }
}

class DraftReport extends DataClass implements Insertable<DraftReport> {
  final String localUuid;
  final String ownerUserUuid;
  final String? serverUuid;
  final String villageUuid;
  final String reportingPeriodUuid;
  final String payloadJson;
  final int recordVersion;
  final String syncStatus;
  final DateTime createdAt;
  final DateTime updatedAt;
  final DateTime? lastSyncedAt;
  final DateTime? serverUpdatedAt;
  final bool deletedLocally;
  final String? conflictStatus;
  final String? syncError;
  const DraftReport({
    required this.localUuid,
    required this.ownerUserUuid,
    this.serverUuid,
    required this.villageUuid,
    required this.reportingPeriodUuid,
    required this.payloadJson,
    required this.recordVersion,
    required this.syncStatus,
    required this.createdAt,
    required this.updatedAt,
    this.lastSyncedAt,
    this.serverUpdatedAt,
    required this.deletedLocally,
    this.conflictStatus,
    this.syncError,
  });
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['local_uuid'] = Variable<String>(localUuid);
    map['owner_user_uuid'] = Variable<String>(ownerUserUuid);
    if (!nullToAbsent || serverUuid != null) {
      map['server_uuid'] = Variable<String>(serverUuid);
    }
    map['village_uuid'] = Variable<String>(villageUuid);
    map['reporting_period_uuid'] = Variable<String>(reportingPeriodUuid);
    map['payload_json'] = Variable<String>(payloadJson);
    map['record_version'] = Variable<int>(recordVersion);
    map['sync_status'] = Variable<String>(syncStatus);
    map['created_at'] = Variable<DateTime>(createdAt);
    map['updated_at'] = Variable<DateTime>(updatedAt);
    if (!nullToAbsent || lastSyncedAt != null) {
      map['last_synced_at'] = Variable<DateTime>(lastSyncedAt);
    }
    if (!nullToAbsent || serverUpdatedAt != null) {
      map['server_updated_at'] = Variable<DateTime>(serverUpdatedAt);
    }
    map['deleted_locally'] = Variable<bool>(deletedLocally);
    if (!nullToAbsent || conflictStatus != null) {
      map['conflict_status'] = Variable<String>(conflictStatus);
    }
    if (!nullToAbsent || syncError != null) {
      map['sync_error'] = Variable<String>(syncError);
    }
    return map;
  }

  DraftReportsCompanion toCompanion(bool nullToAbsent) {
    return DraftReportsCompanion(
      localUuid: Value(localUuid),
      ownerUserUuid: Value(ownerUserUuid),
      serverUuid: serverUuid == null && nullToAbsent
          ? const Value.absent()
          : Value(serverUuid),
      villageUuid: Value(villageUuid),
      reportingPeriodUuid: Value(reportingPeriodUuid),
      payloadJson: Value(payloadJson),
      recordVersion: Value(recordVersion),
      syncStatus: Value(syncStatus),
      createdAt: Value(createdAt),
      updatedAt: Value(updatedAt),
      lastSyncedAt: lastSyncedAt == null && nullToAbsent
          ? const Value.absent()
          : Value(lastSyncedAt),
      serverUpdatedAt: serverUpdatedAt == null && nullToAbsent
          ? const Value.absent()
          : Value(serverUpdatedAt),
      deletedLocally: Value(deletedLocally),
      conflictStatus: conflictStatus == null && nullToAbsent
          ? const Value.absent()
          : Value(conflictStatus),
      syncError: syncError == null && nullToAbsent
          ? const Value.absent()
          : Value(syncError),
    );
  }

  factory DraftReport.fromJson(
    Map<String, dynamic> json, {
    ValueSerializer? serializer,
  }) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return DraftReport(
      localUuid: serializer.fromJson<String>(json['localUuid']),
      ownerUserUuid: serializer.fromJson<String>(json['ownerUserUuid']),
      serverUuid: serializer.fromJson<String?>(json['serverUuid']),
      villageUuid: serializer.fromJson<String>(json['villageUuid']),
      reportingPeriodUuid: serializer.fromJson<String>(
        json['reportingPeriodUuid'],
      ),
      payloadJson: serializer.fromJson<String>(json['payloadJson']),
      recordVersion: serializer.fromJson<int>(json['recordVersion']),
      syncStatus: serializer.fromJson<String>(json['syncStatus']),
      createdAt: serializer.fromJson<DateTime>(json['createdAt']),
      updatedAt: serializer.fromJson<DateTime>(json['updatedAt']),
      lastSyncedAt: serializer.fromJson<DateTime?>(json['lastSyncedAt']),
      serverUpdatedAt: serializer.fromJson<DateTime?>(json['serverUpdatedAt']),
      deletedLocally: serializer.fromJson<bool>(json['deletedLocally']),
      conflictStatus: serializer.fromJson<String?>(json['conflictStatus']),
      syncError: serializer.fromJson<String?>(json['syncError']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'localUuid': serializer.toJson<String>(localUuid),
      'ownerUserUuid': serializer.toJson<String>(ownerUserUuid),
      'serverUuid': serializer.toJson<String?>(serverUuid),
      'villageUuid': serializer.toJson<String>(villageUuid),
      'reportingPeriodUuid': serializer.toJson<String>(reportingPeriodUuid),
      'payloadJson': serializer.toJson<String>(payloadJson),
      'recordVersion': serializer.toJson<int>(recordVersion),
      'syncStatus': serializer.toJson<String>(syncStatus),
      'createdAt': serializer.toJson<DateTime>(createdAt),
      'updatedAt': serializer.toJson<DateTime>(updatedAt),
      'lastSyncedAt': serializer.toJson<DateTime?>(lastSyncedAt),
      'serverUpdatedAt': serializer.toJson<DateTime?>(serverUpdatedAt),
      'deletedLocally': serializer.toJson<bool>(deletedLocally),
      'conflictStatus': serializer.toJson<String?>(conflictStatus),
      'syncError': serializer.toJson<String?>(syncError),
    };
  }

  DraftReport copyWith({
    String? localUuid,
    String? ownerUserUuid,
    Value<String?> serverUuid = const Value.absent(),
    String? villageUuid,
    String? reportingPeriodUuid,
    String? payloadJson,
    int? recordVersion,
    String? syncStatus,
    DateTime? createdAt,
    DateTime? updatedAt,
    Value<DateTime?> lastSyncedAt = const Value.absent(),
    Value<DateTime?> serverUpdatedAt = const Value.absent(),
    bool? deletedLocally,
    Value<String?> conflictStatus = const Value.absent(),
    Value<String?> syncError = const Value.absent(),
  }) => DraftReport(
    localUuid: localUuid ?? this.localUuid,
    ownerUserUuid: ownerUserUuid ?? this.ownerUserUuid,
    serverUuid: serverUuid.present ? serverUuid.value : this.serverUuid,
    villageUuid: villageUuid ?? this.villageUuid,
    reportingPeriodUuid: reportingPeriodUuid ?? this.reportingPeriodUuid,
    payloadJson: payloadJson ?? this.payloadJson,
    recordVersion: recordVersion ?? this.recordVersion,
    syncStatus: syncStatus ?? this.syncStatus,
    createdAt: createdAt ?? this.createdAt,
    updatedAt: updatedAt ?? this.updatedAt,
    lastSyncedAt: lastSyncedAt.present ? lastSyncedAt.value : this.lastSyncedAt,
    serverUpdatedAt: serverUpdatedAt.present
        ? serverUpdatedAt.value
        : this.serverUpdatedAt,
    deletedLocally: deletedLocally ?? this.deletedLocally,
    conflictStatus: conflictStatus.present
        ? conflictStatus.value
        : this.conflictStatus,
    syncError: syncError.present ? syncError.value : this.syncError,
  );
  DraftReport copyWithCompanion(DraftReportsCompanion data) {
    return DraftReport(
      localUuid: data.localUuid.present ? data.localUuid.value : this.localUuid,
      ownerUserUuid: data.ownerUserUuid.present
          ? data.ownerUserUuid.value
          : this.ownerUserUuid,
      serverUuid: data.serverUuid.present
          ? data.serverUuid.value
          : this.serverUuid,
      villageUuid: data.villageUuid.present
          ? data.villageUuid.value
          : this.villageUuid,
      reportingPeriodUuid: data.reportingPeriodUuid.present
          ? data.reportingPeriodUuid.value
          : this.reportingPeriodUuid,
      payloadJson: data.payloadJson.present
          ? data.payloadJson.value
          : this.payloadJson,
      recordVersion: data.recordVersion.present
          ? data.recordVersion.value
          : this.recordVersion,
      syncStatus: data.syncStatus.present
          ? data.syncStatus.value
          : this.syncStatus,
      createdAt: data.createdAt.present ? data.createdAt.value : this.createdAt,
      updatedAt: data.updatedAt.present ? data.updatedAt.value : this.updatedAt,
      lastSyncedAt: data.lastSyncedAt.present
          ? data.lastSyncedAt.value
          : this.lastSyncedAt,
      serverUpdatedAt: data.serverUpdatedAt.present
          ? data.serverUpdatedAt.value
          : this.serverUpdatedAt,
      deletedLocally: data.deletedLocally.present
          ? data.deletedLocally.value
          : this.deletedLocally,
      conflictStatus: data.conflictStatus.present
          ? data.conflictStatus.value
          : this.conflictStatus,
      syncError: data.syncError.present ? data.syncError.value : this.syncError,
    );
  }

  @override
  String toString() {
    return (StringBuffer('DraftReport(')
          ..write('localUuid: $localUuid, ')
          ..write('ownerUserUuid: $ownerUserUuid, ')
          ..write('serverUuid: $serverUuid, ')
          ..write('villageUuid: $villageUuid, ')
          ..write('reportingPeriodUuid: $reportingPeriodUuid, ')
          ..write('payloadJson: $payloadJson, ')
          ..write('recordVersion: $recordVersion, ')
          ..write('syncStatus: $syncStatus, ')
          ..write('createdAt: $createdAt, ')
          ..write('updatedAt: $updatedAt, ')
          ..write('lastSyncedAt: $lastSyncedAt, ')
          ..write('serverUpdatedAt: $serverUpdatedAt, ')
          ..write('deletedLocally: $deletedLocally, ')
          ..write('conflictStatus: $conflictStatus, ')
          ..write('syncError: $syncError')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(
    localUuid,
    ownerUserUuid,
    serverUuid,
    villageUuid,
    reportingPeriodUuid,
    payloadJson,
    recordVersion,
    syncStatus,
    createdAt,
    updatedAt,
    lastSyncedAt,
    serverUpdatedAt,
    deletedLocally,
    conflictStatus,
    syncError,
  );
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is DraftReport &&
          other.localUuid == this.localUuid &&
          other.ownerUserUuid == this.ownerUserUuid &&
          other.serverUuid == this.serverUuid &&
          other.villageUuid == this.villageUuid &&
          other.reportingPeriodUuid == this.reportingPeriodUuid &&
          other.payloadJson == this.payloadJson &&
          other.recordVersion == this.recordVersion &&
          other.syncStatus == this.syncStatus &&
          other.createdAt == this.createdAt &&
          other.updatedAt == this.updatedAt &&
          other.lastSyncedAt == this.lastSyncedAt &&
          other.serverUpdatedAt == this.serverUpdatedAt &&
          other.deletedLocally == this.deletedLocally &&
          other.conflictStatus == this.conflictStatus &&
          other.syncError == this.syncError);
}

class DraftReportsCompanion extends UpdateCompanion<DraftReport> {
  final Value<String> localUuid;
  final Value<String> ownerUserUuid;
  final Value<String?> serverUuid;
  final Value<String> villageUuid;
  final Value<String> reportingPeriodUuid;
  final Value<String> payloadJson;
  final Value<int> recordVersion;
  final Value<String> syncStatus;
  final Value<DateTime> createdAt;
  final Value<DateTime> updatedAt;
  final Value<DateTime?> lastSyncedAt;
  final Value<DateTime?> serverUpdatedAt;
  final Value<bool> deletedLocally;
  final Value<String?> conflictStatus;
  final Value<String?> syncError;
  final Value<int> rowid;
  const DraftReportsCompanion({
    this.localUuid = const Value.absent(),
    this.ownerUserUuid = const Value.absent(),
    this.serverUuid = const Value.absent(),
    this.villageUuid = const Value.absent(),
    this.reportingPeriodUuid = const Value.absent(),
    this.payloadJson = const Value.absent(),
    this.recordVersion = const Value.absent(),
    this.syncStatus = const Value.absent(),
    this.createdAt = const Value.absent(),
    this.updatedAt = const Value.absent(),
    this.lastSyncedAt = const Value.absent(),
    this.serverUpdatedAt = const Value.absent(),
    this.deletedLocally = const Value.absent(),
    this.conflictStatus = const Value.absent(),
    this.syncError = const Value.absent(),
    this.rowid = const Value.absent(),
  });
  DraftReportsCompanion.insert({
    required String localUuid,
    required String ownerUserUuid,
    this.serverUuid = const Value.absent(),
    required String villageUuid,
    required String reportingPeriodUuid,
    required String payloadJson,
    this.recordVersion = const Value.absent(),
    required String syncStatus,
    required DateTime createdAt,
    required DateTime updatedAt,
    this.lastSyncedAt = const Value.absent(),
    this.serverUpdatedAt = const Value.absent(),
    this.deletedLocally = const Value.absent(),
    this.conflictStatus = const Value.absent(),
    this.syncError = const Value.absent(),
    this.rowid = const Value.absent(),
  }) : localUuid = Value(localUuid),
       ownerUserUuid = Value(ownerUserUuid),
       villageUuid = Value(villageUuid),
       reportingPeriodUuid = Value(reportingPeriodUuid),
       payloadJson = Value(payloadJson),
       syncStatus = Value(syncStatus),
       createdAt = Value(createdAt),
       updatedAt = Value(updatedAt);
  static Insertable<DraftReport> custom({
    Expression<String>? localUuid,
    Expression<String>? ownerUserUuid,
    Expression<String>? serverUuid,
    Expression<String>? villageUuid,
    Expression<String>? reportingPeriodUuid,
    Expression<String>? payloadJson,
    Expression<int>? recordVersion,
    Expression<String>? syncStatus,
    Expression<DateTime>? createdAt,
    Expression<DateTime>? updatedAt,
    Expression<DateTime>? lastSyncedAt,
    Expression<DateTime>? serverUpdatedAt,
    Expression<bool>? deletedLocally,
    Expression<String>? conflictStatus,
    Expression<String>? syncError,
    Expression<int>? rowid,
  }) {
    return RawValuesInsertable({
      if (localUuid != null) 'local_uuid': localUuid,
      if (ownerUserUuid != null) 'owner_user_uuid': ownerUserUuid,
      if (serverUuid != null) 'server_uuid': serverUuid,
      if (villageUuid != null) 'village_uuid': villageUuid,
      if (reportingPeriodUuid != null)
        'reporting_period_uuid': reportingPeriodUuid,
      if (payloadJson != null) 'payload_json': payloadJson,
      if (recordVersion != null) 'record_version': recordVersion,
      if (syncStatus != null) 'sync_status': syncStatus,
      if (createdAt != null) 'created_at': createdAt,
      if (updatedAt != null) 'updated_at': updatedAt,
      if (lastSyncedAt != null) 'last_synced_at': lastSyncedAt,
      if (serverUpdatedAt != null) 'server_updated_at': serverUpdatedAt,
      if (deletedLocally != null) 'deleted_locally': deletedLocally,
      if (conflictStatus != null) 'conflict_status': conflictStatus,
      if (syncError != null) 'sync_error': syncError,
      if (rowid != null) 'rowid': rowid,
    });
  }

  DraftReportsCompanion copyWith({
    Value<String>? localUuid,
    Value<String>? ownerUserUuid,
    Value<String?>? serverUuid,
    Value<String>? villageUuid,
    Value<String>? reportingPeriodUuid,
    Value<String>? payloadJson,
    Value<int>? recordVersion,
    Value<String>? syncStatus,
    Value<DateTime>? createdAt,
    Value<DateTime>? updatedAt,
    Value<DateTime?>? lastSyncedAt,
    Value<DateTime?>? serverUpdatedAt,
    Value<bool>? deletedLocally,
    Value<String?>? conflictStatus,
    Value<String?>? syncError,
    Value<int>? rowid,
  }) {
    return DraftReportsCompanion(
      localUuid: localUuid ?? this.localUuid,
      ownerUserUuid: ownerUserUuid ?? this.ownerUserUuid,
      serverUuid: serverUuid ?? this.serverUuid,
      villageUuid: villageUuid ?? this.villageUuid,
      reportingPeriodUuid: reportingPeriodUuid ?? this.reportingPeriodUuid,
      payloadJson: payloadJson ?? this.payloadJson,
      recordVersion: recordVersion ?? this.recordVersion,
      syncStatus: syncStatus ?? this.syncStatus,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      lastSyncedAt: lastSyncedAt ?? this.lastSyncedAt,
      serverUpdatedAt: serverUpdatedAt ?? this.serverUpdatedAt,
      deletedLocally: deletedLocally ?? this.deletedLocally,
      conflictStatus: conflictStatus ?? this.conflictStatus,
      syncError: syncError ?? this.syncError,
      rowid: rowid ?? this.rowid,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (localUuid.present) {
      map['local_uuid'] = Variable<String>(localUuid.value);
    }
    if (ownerUserUuid.present) {
      map['owner_user_uuid'] = Variable<String>(ownerUserUuid.value);
    }
    if (serverUuid.present) {
      map['server_uuid'] = Variable<String>(serverUuid.value);
    }
    if (villageUuid.present) {
      map['village_uuid'] = Variable<String>(villageUuid.value);
    }
    if (reportingPeriodUuid.present) {
      map['reporting_period_uuid'] = Variable<String>(
        reportingPeriodUuid.value,
      );
    }
    if (payloadJson.present) {
      map['payload_json'] = Variable<String>(payloadJson.value);
    }
    if (recordVersion.present) {
      map['record_version'] = Variable<int>(recordVersion.value);
    }
    if (syncStatus.present) {
      map['sync_status'] = Variable<String>(syncStatus.value);
    }
    if (createdAt.present) {
      map['created_at'] = Variable<DateTime>(createdAt.value);
    }
    if (updatedAt.present) {
      map['updated_at'] = Variable<DateTime>(updatedAt.value);
    }
    if (lastSyncedAt.present) {
      map['last_synced_at'] = Variable<DateTime>(lastSyncedAt.value);
    }
    if (serverUpdatedAt.present) {
      map['server_updated_at'] = Variable<DateTime>(serverUpdatedAt.value);
    }
    if (deletedLocally.present) {
      map['deleted_locally'] = Variable<bool>(deletedLocally.value);
    }
    if (conflictStatus.present) {
      map['conflict_status'] = Variable<String>(conflictStatus.value);
    }
    if (syncError.present) {
      map['sync_error'] = Variable<String>(syncError.value);
    }
    if (rowid.present) {
      map['rowid'] = Variable<int>(rowid.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('DraftReportsCompanion(')
          ..write('localUuid: $localUuid, ')
          ..write('ownerUserUuid: $ownerUserUuid, ')
          ..write('serverUuid: $serverUuid, ')
          ..write('villageUuid: $villageUuid, ')
          ..write('reportingPeriodUuid: $reportingPeriodUuid, ')
          ..write('payloadJson: $payloadJson, ')
          ..write('recordVersion: $recordVersion, ')
          ..write('syncStatus: $syncStatus, ')
          ..write('createdAt: $createdAt, ')
          ..write('updatedAt: $updatedAt, ')
          ..write('lastSyncedAt: $lastSyncedAt, ')
          ..write('serverUpdatedAt: $serverUpdatedAt, ')
          ..write('deletedLocally: $deletedLocally, ')
          ..write('conflictStatus: $conflictStatus, ')
          ..write('syncError: $syncError, ')
          ..write('rowid: $rowid')
          ..write(')'))
        .toString();
  }
}

class $OperationalRecordsTable extends OperationalRecords
    with TableInfo<$OperationalRecordsTable, OperationalRecord> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $OperationalRecordsTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _localUuidMeta = const VerificationMeta(
    'localUuid',
  );
  @override
  late final GeneratedColumn<String> localUuid = GeneratedColumn<String>(
    'local_uuid',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _ownerUserUuidMeta = const VerificationMeta(
    'ownerUserUuid',
  );
  @override
  late final GeneratedColumn<String> ownerUserUuid = GeneratedColumn<String>(
    'owner_user_uuid',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _serverUuidMeta = const VerificationMeta(
    'serverUuid',
  );
  @override
  late final GeneratedColumn<String> serverUuid = GeneratedColumn<String>(
    'server_uuid',
    aliasedName,
    true,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
  );
  static const VerificationMeta _resourceTypeMeta = const VerificationMeta(
    'resourceType',
  );
  @override
  late final GeneratedColumn<String> resourceType = GeneratedColumn<String>(
    'resource_type',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _reportLocalUuidMeta = const VerificationMeta(
    'reportLocalUuid',
  );
  @override
  late final GeneratedColumn<String> reportLocalUuid = GeneratedColumn<String>(
    'report_local_uuid',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
    defaultConstraints: GeneratedColumn.constraintIsAlways(
      'REFERENCES draft_reports (local_uuid)',
    ),
  );
  static const VerificationMeta _payloadJsonMeta = const VerificationMeta(
    'payloadJson',
  );
  @override
  late final GeneratedColumn<String> payloadJson = GeneratedColumn<String>(
    'payload_json',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _recordVersionMeta = const VerificationMeta(
    'recordVersion',
  );
  @override
  late final GeneratedColumn<int> recordVersion = GeneratedColumn<int>(
    'record_version',
    aliasedName,
    false,
    type: DriftSqlType.int,
    requiredDuringInsert: false,
    defaultValue: const Constant(0),
  );
  static const VerificationMeta _syncStatusMeta = const VerificationMeta(
    'syncStatus',
  );
  @override
  late final GeneratedColumn<String> syncStatus = GeneratedColumn<String>(
    'sync_status',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _createdAtMeta = const VerificationMeta(
    'createdAt',
  );
  @override
  late final GeneratedColumn<DateTime> createdAt = GeneratedColumn<DateTime>(
    'created_at',
    aliasedName,
    false,
    type: DriftSqlType.dateTime,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _updatedAtMeta = const VerificationMeta(
    'updatedAt',
  );
  @override
  late final GeneratedColumn<DateTime> updatedAt = GeneratedColumn<DateTime>(
    'updated_at',
    aliasedName,
    false,
    type: DriftSqlType.dateTime,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _lastSyncedAtMeta = const VerificationMeta(
    'lastSyncedAt',
  );
  @override
  late final GeneratedColumn<DateTime> lastSyncedAt = GeneratedColumn<DateTime>(
    'last_synced_at',
    aliasedName,
    true,
    type: DriftSqlType.dateTime,
    requiredDuringInsert: false,
  );
  static const VerificationMeta _serverUpdatedAtMeta = const VerificationMeta(
    'serverUpdatedAt',
  );
  @override
  late final GeneratedColumn<DateTime> serverUpdatedAt =
      GeneratedColumn<DateTime>(
        'server_updated_at',
        aliasedName,
        true,
        type: DriftSqlType.dateTime,
        requiredDuringInsert: false,
      );
  static const VerificationMeta _deletedLocallyMeta = const VerificationMeta(
    'deletedLocally',
  );
  @override
  late final GeneratedColumn<bool> deletedLocally = GeneratedColumn<bool>(
    'deleted_locally',
    aliasedName,
    false,
    type: DriftSqlType.bool,
    requiredDuringInsert: false,
    defaultConstraints: GeneratedColumn.constraintIsAlways(
      'CHECK ("deleted_locally" IN (0, 1))',
    ),
    defaultValue: const Constant(false),
  );
  static const VerificationMeta _conflictStatusMeta = const VerificationMeta(
    'conflictStatus',
  );
  @override
  late final GeneratedColumn<String> conflictStatus = GeneratedColumn<String>(
    'conflict_status',
    aliasedName,
    true,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
  );
  static const VerificationMeta _syncErrorMeta = const VerificationMeta(
    'syncError',
  );
  @override
  late final GeneratedColumn<String> syncError = GeneratedColumn<String>(
    'sync_error',
    aliasedName,
    true,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
  );
  static const VerificationMeta _idempotencyKeyMeta = const VerificationMeta(
    'idempotencyKey',
  );
  @override
  late final GeneratedColumn<String> idempotencyKey = GeneratedColumn<String>(
    'idempotency_key',
    aliasedName,
    true,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
  );
  @override
  List<GeneratedColumn> get $columns => [
    localUuid,
    ownerUserUuid,
    serverUuid,
    resourceType,
    reportLocalUuid,
    payloadJson,
    recordVersion,
    syncStatus,
    createdAt,
    updatedAt,
    lastSyncedAt,
    serverUpdatedAt,
    deletedLocally,
    conflictStatus,
    syncError,
    idempotencyKey,
  ];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'operational_records';
  @override
  VerificationContext validateIntegrity(
    Insertable<OperationalRecord> instance, {
    bool isInserting = false,
  }) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('local_uuid')) {
      context.handle(
        _localUuidMeta,
        localUuid.isAcceptableOrUnknown(data['local_uuid']!, _localUuidMeta),
      );
    } else if (isInserting) {
      context.missing(_localUuidMeta);
    }
    if (data.containsKey('owner_user_uuid')) {
      context.handle(
        _ownerUserUuidMeta,
        ownerUserUuid.isAcceptableOrUnknown(
          data['owner_user_uuid']!,
          _ownerUserUuidMeta,
        ),
      );
    } else if (isInserting) {
      context.missing(_ownerUserUuidMeta);
    }
    if (data.containsKey('server_uuid')) {
      context.handle(
        _serverUuidMeta,
        serverUuid.isAcceptableOrUnknown(data['server_uuid']!, _serverUuidMeta),
      );
    }
    if (data.containsKey('resource_type')) {
      context.handle(
        _resourceTypeMeta,
        resourceType.isAcceptableOrUnknown(
          data['resource_type']!,
          _resourceTypeMeta,
        ),
      );
    } else if (isInserting) {
      context.missing(_resourceTypeMeta);
    }
    if (data.containsKey('report_local_uuid')) {
      context.handle(
        _reportLocalUuidMeta,
        reportLocalUuid.isAcceptableOrUnknown(
          data['report_local_uuid']!,
          _reportLocalUuidMeta,
        ),
      );
    } else if (isInserting) {
      context.missing(_reportLocalUuidMeta);
    }
    if (data.containsKey('payload_json')) {
      context.handle(
        _payloadJsonMeta,
        payloadJson.isAcceptableOrUnknown(
          data['payload_json']!,
          _payloadJsonMeta,
        ),
      );
    } else if (isInserting) {
      context.missing(_payloadJsonMeta);
    }
    if (data.containsKey('record_version')) {
      context.handle(
        _recordVersionMeta,
        recordVersion.isAcceptableOrUnknown(
          data['record_version']!,
          _recordVersionMeta,
        ),
      );
    }
    if (data.containsKey('sync_status')) {
      context.handle(
        _syncStatusMeta,
        syncStatus.isAcceptableOrUnknown(data['sync_status']!, _syncStatusMeta),
      );
    } else if (isInserting) {
      context.missing(_syncStatusMeta);
    }
    if (data.containsKey('created_at')) {
      context.handle(
        _createdAtMeta,
        createdAt.isAcceptableOrUnknown(data['created_at']!, _createdAtMeta),
      );
    } else if (isInserting) {
      context.missing(_createdAtMeta);
    }
    if (data.containsKey('updated_at')) {
      context.handle(
        _updatedAtMeta,
        updatedAt.isAcceptableOrUnknown(data['updated_at']!, _updatedAtMeta),
      );
    } else if (isInserting) {
      context.missing(_updatedAtMeta);
    }
    if (data.containsKey('last_synced_at')) {
      context.handle(
        _lastSyncedAtMeta,
        lastSyncedAt.isAcceptableOrUnknown(
          data['last_synced_at']!,
          _lastSyncedAtMeta,
        ),
      );
    }
    if (data.containsKey('server_updated_at')) {
      context.handle(
        _serverUpdatedAtMeta,
        serverUpdatedAt.isAcceptableOrUnknown(
          data['server_updated_at']!,
          _serverUpdatedAtMeta,
        ),
      );
    }
    if (data.containsKey('deleted_locally')) {
      context.handle(
        _deletedLocallyMeta,
        deletedLocally.isAcceptableOrUnknown(
          data['deleted_locally']!,
          _deletedLocallyMeta,
        ),
      );
    }
    if (data.containsKey('conflict_status')) {
      context.handle(
        _conflictStatusMeta,
        conflictStatus.isAcceptableOrUnknown(
          data['conflict_status']!,
          _conflictStatusMeta,
        ),
      );
    }
    if (data.containsKey('sync_error')) {
      context.handle(
        _syncErrorMeta,
        syncError.isAcceptableOrUnknown(data['sync_error']!, _syncErrorMeta),
      );
    }
    if (data.containsKey('idempotency_key')) {
      context.handle(
        _idempotencyKeyMeta,
        idempotencyKey.isAcceptableOrUnknown(
          data['idempotency_key']!,
          _idempotencyKeyMeta,
        ),
      );
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {localUuid};
  @override
  List<Set<GeneratedColumn>> get uniqueKeys => [
    {ownerUserUuid, resourceType, serverUuid},
  ];
  @override
  OperationalRecord map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return OperationalRecord(
      localUuid: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}local_uuid'],
      )!,
      ownerUserUuid: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}owner_user_uuid'],
      )!,
      serverUuid: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}server_uuid'],
      ),
      resourceType: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}resource_type'],
      )!,
      reportLocalUuid: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}report_local_uuid'],
      )!,
      payloadJson: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}payload_json'],
      )!,
      recordVersion: attachedDatabase.typeMapping.read(
        DriftSqlType.int,
        data['${effectivePrefix}record_version'],
      )!,
      syncStatus: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}sync_status'],
      )!,
      createdAt: attachedDatabase.typeMapping.read(
        DriftSqlType.dateTime,
        data['${effectivePrefix}created_at'],
      )!,
      updatedAt: attachedDatabase.typeMapping.read(
        DriftSqlType.dateTime,
        data['${effectivePrefix}updated_at'],
      )!,
      lastSyncedAt: attachedDatabase.typeMapping.read(
        DriftSqlType.dateTime,
        data['${effectivePrefix}last_synced_at'],
      ),
      serverUpdatedAt: attachedDatabase.typeMapping.read(
        DriftSqlType.dateTime,
        data['${effectivePrefix}server_updated_at'],
      ),
      deletedLocally: attachedDatabase.typeMapping.read(
        DriftSqlType.bool,
        data['${effectivePrefix}deleted_locally'],
      )!,
      conflictStatus: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}conflict_status'],
      ),
      syncError: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}sync_error'],
      ),
      idempotencyKey: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}idempotency_key'],
      ),
    );
  }

  @override
  $OperationalRecordsTable createAlias(String alias) {
    return $OperationalRecordsTable(attachedDatabase, alias);
  }
}

class OperationalRecord extends DataClass
    implements Insertable<OperationalRecord> {
  final String localUuid;
  final String ownerUserUuid;
  final String? serverUuid;
  final String resourceType;
  final String reportLocalUuid;
  final String payloadJson;
  final int recordVersion;
  final String syncStatus;
  final DateTime createdAt;
  final DateTime updatedAt;
  final DateTime? lastSyncedAt;
  final DateTime? serverUpdatedAt;
  final bool deletedLocally;
  final String? conflictStatus;
  final String? syncError;
  final String? idempotencyKey;
  const OperationalRecord({
    required this.localUuid,
    required this.ownerUserUuid,
    this.serverUuid,
    required this.resourceType,
    required this.reportLocalUuid,
    required this.payloadJson,
    required this.recordVersion,
    required this.syncStatus,
    required this.createdAt,
    required this.updatedAt,
    this.lastSyncedAt,
    this.serverUpdatedAt,
    required this.deletedLocally,
    this.conflictStatus,
    this.syncError,
    this.idempotencyKey,
  });
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['local_uuid'] = Variable<String>(localUuid);
    map['owner_user_uuid'] = Variable<String>(ownerUserUuid);
    if (!nullToAbsent || serverUuid != null) {
      map['server_uuid'] = Variable<String>(serverUuid);
    }
    map['resource_type'] = Variable<String>(resourceType);
    map['report_local_uuid'] = Variable<String>(reportLocalUuid);
    map['payload_json'] = Variable<String>(payloadJson);
    map['record_version'] = Variable<int>(recordVersion);
    map['sync_status'] = Variable<String>(syncStatus);
    map['created_at'] = Variable<DateTime>(createdAt);
    map['updated_at'] = Variable<DateTime>(updatedAt);
    if (!nullToAbsent || lastSyncedAt != null) {
      map['last_synced_at'] = Variable<DateTime>(lastSyncedAt);
    }
    if (!nullToAbsent || serverUpdatedAt != null) {
      map['server_updated_at'] = Variable<DateTime>(serverUpdatedAt);
    }
    map['deleted_locally'] = Variable<bool>(deletedLocally);
    if (!nullToAbsent || conflictStatus != null) {
      map['conflict_status'] = Variable<String>(conflictStatus);
    }
    if (!nullToAbsent || syncError != null) {
      map['sync_error'] = Variable<String>(syncError);
    }
    if (!nullToAbsent || idempotencyKey != null) {
      map['idempotency_key'] = Variable<String>(idempotencyKey);
    }
    return map;
  }

  OperationalRecordsCompanion toCompanion(bool nullToAbsent) {
    return OperationalRecordsCompanion(
      localUuid: Value(localUuid),
      ownerUserUuid: Value(ownerUserUuid),
      serverUuid: serverUuid == null && nullToAbsent
          ? const Value.absent()
          : Value(serverUuid),
      resourceType: Value(resourceType),
      reportLocalUuid: Value(reportLocalUuid),
      payloadJson: Value(payloadJson),
      recordVersion: Value(recordVersion),
      syncStatus: Value(syncStatus),
      createdAt: Value(createdAt),
      updatedAt: Value(updatedAt),
      lastSyncedAt: lastSyncedAt == null && nullToAbsent
          ? const Value.absent()
          : Value(lastSyncedAt),
      serverUpdatedAt: serverUpdatedAt == null && nullToAbsent
          ? const Value.absent()
          : Value(serverUpdatedAt),
      deletedLocally: Value(deletedLocally),
      conflictStatus: conflictStatus == null && nullToAbsent
          ? const Value.absent()
          : Value(conflictStatus),
      syncError: syncError == null && nullToAbsent
          ? const Value.absent()
          : Value(syncError),
      idempotencyKey: idempotencyKey == null && nullToAbsent
          ? const Value.absent()
          : Value(idempotencyKey),
    );
  }

  factory OperationalRecord.fromJson(
    Map<String, dynamic> json, {
    ValueSerializer? serializer,
  }) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return OperationalRecord(
      localUuid: serializer.fromJson<String>(json['localUuid']),
      ownerUserUuid: serializer.fromJson<String>(json['ownerUserUuid']),
      serverUuid: serializer.fromJson<String?>(json['serverUuid']),
      resourceType: serializer.fromJson<String>(json['resourceType']),
      reportLocalUuid: serializer.fromJson<String>(json['reportLocalUuid']),
      payloadJson: serializer.fromJson<String>(json['payloadJson']),
      recordVersion: serializer.fromJson<int>(json['recordVersion']),
      syncStatus: serializer.fromJson<String>(json['syncStatus']),
      createdAt: serializer.fromJson<DateTime>(json['createdAt']),
      updatedAt: serializer.fromJson<DateTime>(json['updatedAt']),
      lastSyncedAt: serializer.fromJson<DateTime?>(json['lastSyncedAt']),
      serverUpdatedAt: serializer.fromJson<DateTime?>(json['serverUpdatedAt']),
      deletedLocally: serializer.fromJson<bool>(json['deletedLocally']),
      conflictStatus: serializer.fromJson<String?>(json['conflictStatus']),
      syncError: serializer.fromJson<String?>(json['syncError']),
      idempotencyKey: serializer.fromJson<String?>(json['idempotencyKey']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'localUuid': serializer.toJson<String>(localUuid),
      'ownerUserUuid': serializer.toJson<String>(ownerUserUuid),
      'serverUuid': serializer.toJson<String?>(serverUuid),
      'resourceType': serializer.toJson<String>(resourceType),
      'reportLocalUuid': serializer.toJson<String>(reportLocalUuid),
      'payloadJson': serializer.toJson<String>(payloadJson),
      'recordVersion': serializer.toJson<int>(recordVersion),
      'syncStatus': serializer.toJson<String>(syncStatus),
      'createdAt': serializer.toJson<DateTime>(createdAt),
      'updatedAt': serializer.toJson<DateTime>(updatedAt),
      'lastSyncedAt': serializer.toJson<DateTime?>(lastSyncedAt),
      'serverUpdatedAt': serializer.toJson<DateTime?>(serverUpdatedAt),
      'deletedLocally': serializer.toJson<bool>(deletedLocally),
      'conflictStatus': serializer.toJson<String?>(conflictStatus),
      'syncError': serializer.toJson<String?>(syncError),
      'idempotencyKey': serializer.toJson<String?>(idempotencyKey),
    };
  }

  OperationalRecord copyWith({
    String? localUuid,
    String? ownerUserUuid,
    Value<String?> serverUuid = const Value.absent(),
    String? resourceType,
    String? reportLocalUuid,
    String? payloadJson,
    int? recordVersion,
    String? syncStatus,
    DateTime? createdAt,
    DateTime? updatedAt,
    Value<DateTime?> lastSyncedAt = const Value.absent(),
    Value<DateTime?> serverUpdatedAt = const Value.absent(),
    bool? deletedLocally,
    Value<String?> conflictStatus = const Value.absent(),
    Value<String?> syncError = const Value.absent(),
    Value<String?> idempotencyKey = const Value.absent(),
  }) => OperationalRecord(
    localUuid: localUuid ?? this.localUuid,
    ownerUserUuid: ownerUserUuid ?? this.ownerUserUuid,
    serverUuid: serverUuid.present ? serverUuid.value : this.serverUuid,
    resourceType: resourceType ?? this.resourceType,
    reportLocalUuid: reportLocalUuid ?? this.reportLocalUuid,
    payloadJson: payloadJson ?? this.payloadJson,
    recordVersion: recordVersion ?? this.recordVersion,
    syncStatus: syncStatus ?? this.syncStatus,
    createdAt: createdAt ?? this.createdAt,
    updatedAt: updatedAt ?? this.updatedAt,
    lastSyncedAt: lastSyncedAt.present ? lastSyncedAt.value : this.lastSyncedAt,
    serverUpdatedAt: serverUpdatedAt.present
        ? serverUpdatedAt.value
        : this.serverUpdatedAt,
    deletedLocally: deletedLocally ?? this.deletedLocally,
    conflictStatus: conflictStatus.present
        ? conflictStatus.value
        : this.conflictStatus,
    syncError: syncError.present ? syncError.value : this.syncError,
    idempotencyKey: idempotencyKey.present
        ? idempotencyKey.value
        : this.idempotencyKey,
  );
  OperationalRecord copyWithCompanion(OperationalRecordsCompanion data) {
    return OperationalRecord(
      localUuid: data.localUuid.present ? data.localUuid.value : this.localUuid,
      ownerUserUuid: data.ownerUserUuid.present
          ? data.ownerUserUuid.value
          : this.ownerUserUuid,
      serverUuid: data.serverUuid.present
          ? data.serverUuid.value
          : this.serverUuid,
      resourceType: data.resourceType.present
          ? data.resourceType.value
          : this.resourceType,
      reportLocalUuid: data.reportLocalUuid.present
          ? data.reportLocalUuid.value
          : this.reportLocalUuid,
      payloadJson: data.payloadJson.present
          ? data.payloadJson.value
          : this.payloadJson,
      recordVersion: data.recordVersion.present
          ? data.recordVersion.value
          : this.recordVersion,
      syncStatus: data.syncStatus.present
          ? data.syncStatus.value
          : this.syncStatus,
      createdAt: data.createdAt.present ? data.createdAt.value : this.createdAt,
      updatedAt: data.updatedAt.present ? data.updatedAt.value : this.updatedAt,
      lastSyncedAt: data.lastSyncedAt.present
          ? data.lastSyncedAt.value
          : this.lastSyncedAt,
      serverUpdatedAt: data.serverUpdatedAt.present
          ? data.serverUpdatedAt.value
          : this.serverUpdatedAt,
      deletedLocally: data.deletedLocally.present
          ? data.deletedLocally.value
          : this.deletedLocally,
      conflictStatus: data.conflictStatus.present
          ? data.conflictStatus.value
          : this.conflictStatus,
      syncError: data.syncError.present ? data.syncError.value : this.syncError,
      idempotencyKey: data.idempotencyKey.present
          ? data.idempotencyKey.value
          : this.idempotencyKey,
    );
  }

  @override
  String toString() {
    return (StringBuffer('OperationalRecord(')
          ..write('localUuid: $localUuid, ')
          ..write('ownerUserUuid: $ownerUserUuid, ')
          ..write('serverUuid: $serverUuid, ')
          ..write('resourceType: $resourceType, ')
          ..write('reportLocalUuid: $reportLocalUuid, ')
          ..write('payloadJson: $payloadJson, ')
          ..write('recordVersion: $recordVersion, ')
          ..write('syncStatus: $syncStatus, ')
          ..write('createdAt: $createdAt, ')
          ..write('updatedAt: $updatedAt, ')
          ..write('lastSyncedAt: $lastSyncedAt, ')
          ..write('serverUpdatedAt: $serverUpdatedAt, ')
          ..write('deletedLocally: $deletedLocally, ')
          ..write('conflictStatus: $conflictStatus, ')
          ..write('syncError: $syncError, ')
          ..write('idempotencyKey: $idempotencyKey')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(
    localUuid,
    ownerUserUuid,
    serverUuid,
    resourceType,
    reportLocalUuid,
    payloadJson,
    recordVersion,
    syncStatus,
    createdAt,
    updatedAt,
    lastSyncedAt,
    serverUpdatedAt,
    deletedLocally,
    conflictStatus,
    syncError,
    idempotencyKey,
  );
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is OperationalRecord &&
          other.localUuid == this.localUuid &&
          other.ownerUserUuid == this.ownerUserUuid &&
          other.serverUuid == this.serverUuid &&
          other.resourceType == this.resourceType &&
          other.reportLocalUuid == this.reportLocalUuid &&
          other.payloadJson == this.payloadJson &&
          other.recordVersion == this.recordVersion &&
          other.syncStatus == this.syncStatus &&
          other.createdAt == this.createdAt &&
          other.updatedAt == this.updatedAt &&
          other.lastSyncedAt == this.lastSyncedAt &&
          other.serverUpdatedAt == this.serverUpdatedAt &&
          other.deletedLocally == this.deletedLocally &&
          other.conflictStatus == this.conflictStatus &&
          other.syncError == this.syncError &&
          other.idempotencyKey == this.idempotencyKey);
}

class OperationalRecordsCompanion extends UpdateCompanion<OperationalRecord> {
  final Value<String> localUuid;
  final Value<String> ownerUserUuid;
  final Value<String?> serverUuid;
  final Value<String> resourceType;
  final Value<String> reportLocalUuid;
  final Value<String> payloadJson;
  final Value<int> recordVersion;
  final Value<String> syncStatus;
  final Value<DateTime> createdAt;
  final Value<DateTime> updatedAt;
  final Value<DateTime?> lastSyncedAt;
  final Value<DateTime?> serverUpdatedAt;
  final Value<bool> deletedLocally;
  final Value<String?> conflictStatus;
  final Value<String?> syncError;
  final Value<String?> idempotencyKey;
  final Value<int> rowid;
  const OperationalRecordsCompanion({
    this.localUuid = const Value.absent(),
    this.ownerUserUuid = const Value.absent(),
    this.serverUuid = const Value.absent(),
    this.resourceType = const Value.absent(),
    this.reportLocalUuid = const Value.absent(),
    this.payloadJson = const Value.absent(),
    this.recordVersion = const Value.absent(),
    this.syncStatus = const Value.absent(),
    this.createdAt = const Value.absent(),
    this.updatedAt = const Value.absent(),
    this.lastSyncedAt = const Value.absent(),
    this.serverUpdatedAt = const Value.absent(),
    this.deletedLocally = const Value.absent(),
    this.conflictStatus = const Value.absent(),
    this.syncError = const Value.absent(),
    this.idempotencyKey = const Value.absent(),
    this.rowid = const Value.absent(),
  });
  OperationalRecordsCompanion.insert({
    required String localUuid,
    required String ownerUserUuid,
    this.serverUuid = const Value.absent(),
    required String resourceType,
    required String reportLocalUuid,
    required String payloadJson,
    this.recordVersion = const Value.absent(),
    required String syncStatus,
    required DateTime createdAt,
    required DateTime updatedAt,
    this.lastSyncedAt = const Value.absent(),
    this.serverUpdatedAt = const Value.absent(),
    this.deletedLocally = const Value.absent(),
    this.conflictStatus = const Value.absent(),
    this.syncError = const Value.absent(),
    this.idempotencyKey = const Value.absent(),
    this.rowid = const Value.absent(),
  }) : localUuid = Value(localUuid),
       ownerUserUuid = Value(ownerUserUuid),
       resourceType = Value(resourceType),
       reportLocalUuid = Value(reportLocalUuid),
       payloadJson = Value(payloadJson),
       syncStatus = Value(syncStatus),
       createdAt = Value(createdAt),
       updatedAt = Value(updatedAt);
  static Insertable<OperationalRecord> custom({
    Expression<String>? localUuid,
    Expression<String>? ownerUserUuid,
    Expression<String>? serverUuid,
    Expression<String>? resourceType,
    Expression<String>? reportLocalUuid,
    Expression<String>? payloadJson,
    Expression<int>? recordVersion,
    Expression<String>? syncStatus,
    Expression<DateTime>? createdAt,
    Expression<DateTime>? updatedAt,
    Expression<DateTime>? lastSyncedAt,
    Expression<DateTime>? serverUpdatedAt,
    Expression<bool>? deletedLocally,
    Expression<String>? conflictStatus,
    Expression<String>? syncError,
    Expression<String>? idempotencyKey,
    Expression<int>? rowid,
  }) {
    return RawValuesInsertable({
      if (localUuid != null) 'local_uuid': localUuid,
      if (ownerUserUuid != null) 'owner_user_uuid': ownerUserUuid,
      if (serverUuid != null) 'server_uuid': serverUuid,
      if (resourceType != null) 'resource_type': resourceType,
      if (reportLocalUuid != null) 'report_local_uuid': reportLocalUuid,
      if (payloadJson != null) 'payload_json': payloadJson,
      if (recordVersion != null) 'record_version': recordVersion,
      if (syncStatus != null) 'sync_status': syncStatus,
      if (createdAt != null) 'created_at': createdAt,
      if (updatedAt != null) 'updated_at': updatedAt,
      if (lastSyncedAt != null) 'last_synced_at': lastSyncedAt,
      if (serverUpdatedAt != null) 'server_updated_at': serverUpdatedAt,
      if (deletedLocally != null) 'deleted_locally': deletedLocally,
      if (conflictStatus != null) 'conflict_status': conflictStatus,
      if (syncError != null) 'sync_error': syncError,
      if (idempotencyKey != null) 'idempotency_key': idempotencyKey,
      if (rowid != null) 'rowid': rowid,
    });
  }

  OperationalRecordsCompanion copyWith({
    Value<String>? localUuid,
    Value<String>? ownerUserUuid,
    Value<String?>? serverUuid,
    Value<String>? resourceType,
    Value<String>? reportLocalUuid,
    Value<String>? payloadJson,
    Value<int>? recordVersion,
    Value<String>? syncStatus,
    Value<DateTime>? createdAt,
    Value<DateTime>? updatedAt,
    Value<DateTime?>? lastSyncedAt,
    Value<DateTime?>? serverUpdatedAt,
    Value<bool>? deletedLocally,
    Value<String?>? conflictStatus,
    Value<String?>? syncError,
    Value<String?>? idempotencyKey,
    Value<int>? rowid,
  }) {
    return OperationalRecordsCompanion(
      localUuid: localUuid ?? this.localUuid,
      ownerUserUuid: ownerUserUuid ?? this.ownerUserUuid,
      serverUuid: serverUuid ?? this.serverUuid,
      resourceType: resourceType ?? this.resourceType,
      reportLocalUuid: reportLocalUuid ?? this.reportLocalUuid,
      payloadJson: payloadJson ?? this.payloadJson,
      recordVersion: recordVersion ?? this.recordVersion,
      syncStatus: syncStatus ?? this.syncStatus,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      lastSyncedAt: lastSyncedAt ?? this.lastSyncedAt,
      serverUpdatedAt: serverUpdatedAt ?? this.serverUpdatedAt,
      deletedLocally: deletedLocally ?? this.deletedLocally,
      conflictStatus: conflictStatus ?? this.conflictStatus,
      syncError: syncError ?? this.syncError,
      idempotencyKey: idempotencyKey ?? this.idempotencyKey,
      rowid: rowid ?? this.rowid,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (localUuid.present) {
      map['local_uuid'] = Variable<String>(localUuid.value);
    }
    if (ownerUserUuid.present) {
      map['owner_user_uuid'] = Variable<String>(ownerUserUuid.value);
    }
    if (serverUuid.present) {
      map['server_uuid'] = Variable<String>(serverUuid.value);
    }
    if (resourceType.present) {
      map['resource_type'] = Variable<String>(resourceType.value);
    }
    if (reportLocalUuid.present) {
      map['report_local_uuid'] = Variable<String>(reportLocalUuid.value);
    }
    if (payloadJson.present) {
      map['payload_json'] = Variable<String>(payloadJson.value);
    }
    if (recordVersion.present) {
      map['record_version'] = Variable<int>(recordVersion.value);
    }
    if (syncStatus.present) {
      map['sync_status'] = Variable<String>(syncStatus.value);
    }
    if (createdAt.present) {
      map['created_at'] = Variable<DateTime>(createdAt.value);
    }
    if (updatedAt.present) {
      map['updated_at'] = Variable<DateTime>(updatedAt.value);
    }
    if (lastSyncedAt.present) {
      map['last_synced_at'] = Variable<DateTime>(lastSyncedAt.value);
    }
    if (serverUpdatedAt.present) {
      map['server_updated_at'] = Variable<DateTime>(serverUpdatedAt.value);
    }
    if (deletedLocally.present) {
      map['deleted_locally'] = Variable<bool>(deletedLocally.value);
    }
    if (conflictStatus.present) {
      map['conflict_status'] = Variable<String>(conflictStatus.value);
    }
    if (syncError.present) {
      map['sync_error'] = Variable<String>(syncError.value);
    }
    if (idempotencyKey.present) {
      map['idempotency_key'] = Variable<String>(idempotencyKey.value);
    }
    if (rowid.present) {
      map['rowid'] = Variable<int>(rowid.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('OperationalRecordsCompanion(')
          ..write('localUuid: $localUuid, ')
          ..write('ownerUserUuid: $ownerUserUuid, ')
          ..write('serverUuid: $serverUuid, ')
          ..write('resourceType: $resourceType, ')
          ..write('reportLocalUuid: $reportLocalUuid, ')
          ..write('payloadJson: $payloadJson, ')
          ..write('recordVersion: $recordVersion, ')
          ..write('syncStatus: $syncStatus, ')
          ..write('createdAt: $createdAt, ')
          ..write('updatedAt: $updatedAt, ')
          ..write('lastSyncedAt: $lastSyncedAt, ')
          ..write('serverUpdatedAt: $serverUpdatedAt, ')
          ..write('deletedLocally: $deletedLocally, ')
          ..write('conflictStatus: $conflictStatus, ')
          ..write('syncError: $syncError, ')
          ..write('idempotencyKey: $idempotencyKey, ')
          ..write('rowid: $rowid')
          ..write(')'))
        .toString();
  }
}

class $PendingAttachmentsTable extends PendingAttachments
    with TableInfo<$PendingAttachmentsTable, PendingAttachment> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $PendingAttachmentsTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _localUuidMeta = const VerificationMeta(
    'localUuid',
  );
  @override
  late final GeneratedColumn<String> localUuid = GeneratedColumn<String>(
    'local_uuid',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _ownerUserUuidMeta = const VerificationMeta(
    'ownerUserUuid',
  );
  @override
  late final GeneratedColumn<String> ownerUserUuid = GeneratedColumn<String>(
    'owner_user_uuid',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _serverUuidMeta = const VerificationMeta(
    'serverUuid',
  );
  @override
  late final GeneratedColumn<String> serverUuid = GeneratedColumn<String>(
    'server_uuid',
    aliasedName,
    true,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
  );
  static const VerificationMeta _reportLocalUuidMeta = const VerificationMeta(
    'reportLocalUuid',
  );
  @override
  late final GeneratedColumn<String> reportLocalUuid = GeneratedColumn<String>(
    'report_local_uuid',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
    defaultConstraints: GeneratedColumn.constraintIsAlways(
      'REFERENCES draft_reports (local_uuid)',
    ),
  );
  static const VerificationMeta _localPathMeta = const VerificationMeta(
    'localPath',
  );
  @override
  late final GeneratedColumn<String> localPath = GeneratedColumn<String>(
    'local_path',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _mediaTypeMeta = const VerificationMeta(
    'mediaType',
  );
  @override
  late final GeneratedColumn<String> mediaType = GeneratedColumn<String>(
    'media_type',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _checksumSha256Meta = const VerificationMeta(
    'checksumSha256',
  );
  @override
  late final GeneratedColumn<String> checksumSha256 = GeneratedColumn<String>(
    'checksum_sha256',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _byteSizeMeta = const VerificationMeta(
    'byteSize',
  );
  @override
  late final GeneratedColumn<int> byteSize = GeneratedColumn<int>(
    'byte_size',
    aliasedName,
    false,
    type: DriftSqlType.int,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _syncStatusMeta = const VerificationMeta(
    'syncStatus',
  );
  @override
  late final GeneratedColumn<String> syncStatus = GeneratedColumn<String>(
    'sync_status',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _retryCountMeta = const VerificationMeta(
    'retryCount',
  );
  @override
  late final GeneratedColumn<int> retryCount = GeneratedColumn<int>(
    'retry_count',
    aliasedName,
    false,
    type: DriftSqlType.int,
    requiredDuringInsert: false,
    defaultValue: const Constant(0),
  );
  static const VerificationMeta _createdAtMeta = const VerificationMeta(
    'createdAt',
  );
  @override
  late final GeneratedColumn<DateTime> createdAt = GeneratedColumn<DateTime>(
    'created_at',
    aliasedName,
    false,
    type: DriftSqlType.dateTime,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _updatedAtMeta = const VerificationMeta(
    'updatedAt',
  );
  @override
  late final GeneratedColumn<DateTime> updatedAt = GeneratedColumn<DateTime>(
    'updated_at',
    aliasedName,
    false,
    type: DriftSqlType.dateTime,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _syncErrorMeta = const VerificationMeta(
    'syncError',
  );
  @override
  late final GeneratedColumn<String> syncError = GeneratedColumn<String>(
    'sync_error',
    aliasedName,
    true,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
  );
  static const VerificationMeta _metadataJsonMeta = const VerificationMeta(
    'metadataJson',
  );
  @override
  late final GeneratedColumn<String> metadataJson = GeneratedColumn<String>(
    'metadata_json',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
    defaultValue: const Constant('{}'),
  );
  static const VerificationMeta _idempotencyKeyMeta = const VerificationMeta(
    'idempotencyKey',
  );
  @override
  late final GeneratedColumn<String> idempotencyKey = GeneratedColumn<String>(
    'idempotency_key',
    aliasedName,
    true,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
  );
  @override
  List<GeneratedColumn> get $columns => [
    localUuid,
    ownerUserUuid,
    serverUuid,
    reportLocalUuid,
    localPath,
    mediaType,
    checksumSha256,
    byteSize,
    syncStatus,
    retryCount,
    createdAt,
    updatedAt,
    syncError,
    metadataJson,
    idempotencyKey,
  ];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'pending_attachments';
  @override
  VerificationContext validateIntegrity(
    Insertable<PendingAttachment> instance, {
    bool isInserting = false,
  }) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('local_uuid')) {
      context.handle(
        _localUuidMeta,
        localUuid.isAcceptableOrUnknown(data['local_uuid']!, _localUuidMeta),
      );
    } else if (isInserting) {
      context.missing(_localUuidMeta);
    }
    if (data.containsKey('owner_user_uuid')) {
      context.handle(
        _ownerUserUuidMeta,
        ownerUserUuid.isAcceptableOrUnknown(
          data['owner_user_uuid']!,
          _ownerUserUuidMeta,
        ),
      );
    } else if (isInserting) {
      context.missing(_ownerUserUuidMeta);
    }
    if (data.containsKey('server_uuid')) {
      context.handle(
        _serverUuidMeta,
        serverUuid.isAcceptableOrUnknown(data['server_uuid']!, _serverUuidMeta),
      );
    }
    if (data.containsKey('report_local_uuid')) {
      context.handle(
        _reportLocalUuidMeta,
        reportLocalUuid.isAcceptableOrUnknown(
          data['report_local_uuid']!,
          _reportLocalUuidMeta,
        ),
      );
    } else if (isInserting) {
      context.missing(_reportLocalUuidMeta);
    }
    if (data.containsKey('local_path')) {
      context.handle(
        _localPathMeta,
        localPath.isAcceptableOrUnknown(data['local_path']!, _localPathMeta),
      );
    } else if (isInserting) {
      context.missing(_localPathMeta);
    }
    if (data.containsKey('media_type')) {
      context.handle(
        _mediaTypeMeta,
        mediaType.isAcceptableOrUnknown(data['media_type']!, _mediaTypeMeta),
      );
    } else if (isInserting) {
      context.missing(_mediaTypeMeta);
    }
    if (data.containsKey('checksum_sha256')) {
      context.handle(
        _checksumSha256Meta,
        checksumSha256.isAcceptableOrUnknown(
          data['checksum_sha256']!,
          _checksumSha256Meta,
        ),
      );
    } else if (isInserting) {
      context.missing(_checksumSha256Meta);
    }
    if (data.containsKey('byte_size')) {
      context.handle(
        _byteSizeMeta,
        byteSize.isAcceptableOrUnknown(data['byte_size']!, _byteSizeMeta),
      );
    } else if (isInserting) {
      context.missing(_byteSizeMeta);
    }
    if (data.containsKey('sync_status')) {
      context.handle(
        _syncStatusMeta,
        syncStatus.isAcceptableOrUnknown(data['sync_status']!, _syncStatusMeta),
      );
    } else if (isInserting) {
      context.missing(_syncStatusMeta);
    }
    if (data.containsKey('retry_count')) {
      context.handle(
        _retryCountMeta,
        retryCount.isAcceptableOrUnknown(data['retry_count']!, _retryCountMeta),
      );
    }
    if (data.containsKey('created_at')) {
      context.handle(
        _createdAtMeta,
        createdAt.isAcceptableOrUnknown(data['created_at']!, _createdAtMeta),
      );
    } else if (isInserting) {
      context.missing(_createdAtMeta);
    }
    if (data.containsKey('updated_at')) {
      context.handle(
        _updatedAtMeta,
        updatedAt.isAcceptableOrUnknown(data['updated_at']!, _updatedAtMeta),
      );
    } else if (isInserting) {
      context.missing(_updatedAtMeta);
    }
    if (data.containsKey('sync_error')) {
      context.handle(
        _syncErrorMeta,
        syncError.isAcceptableOrUnknown(data['sync_error']!, _syncErrorMeta),
      );
    }
    if (data.containsKey('metadata_json')) {
      context.handle(
        _metadataJsonMeta,
        metadataJson.isAcceptableOrUnknown(
          data['metadata_json']!,
          _metadataJsonMeta,
        ),
      );
    }
    if (data.containsKey('idempotency_key')) {
      context.handle(
        _idempotencyKeyMeta,
        idempotencyKey.isAcceptableOrUnknown(
          data['idempotency_key']!,
          _idempotencyKeyMeta,
        ),
      );
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {localUuid};
  @override
  List<Set<GeneratedColumn>> get uniqueKeys => [
    {ownerUserUuid, serverUuid},
  ];
  @override
  PendingAttachment map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return PendingAttachment(
      localUuid: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}local_uuid'],
      )!,
      ownerUserUuid: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}owner_user_uuid'],
      )!,
      serverUuid: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}server_uuid'],
      ),
      reportLocalUuid: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}report_local_uuid'],
      )!,
      localPath: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}local_path'],
      )!,
      mediaType: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}media_type'],
      )!,
      checksumSha256: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}checksum_sha256'],
      )!,
      byteSize: attachedDatabase.typeMapping.read(
        DriftSqlType.int,
        data['${effectivePrefix}byte_size'],
      )!,
      syncStatus: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}sync_status'],
      )!,
      retryCount: attachedDatabase.typeMapping.read(
        DriftSqlType.int,
        data['${effectivePrefix}retry_count'],
      )!,
      createdAt: attachedDatabase.typeMapping.read(
        DriftSqlType.dateTime,
        data['${effectivePrefix}created_at'],
      )!,
      updatedAt: attachedDatabase.typeMapping.read(
        DriftSqlType.dateTime,
        data['${effectivePrefix}updated_at'],
      )!,
      syncError: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}sync_error'],
      ),
      metadataJson: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}metadata_json'],
      )!,
      idempotencyKey: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}idempotency_key'],
      ),
    );
  }

  @override
  $PendingAttachmentsTable createAlias(String alias) {
    return $PendingAttachmentsTable(attachedDatabase, alias);
  }
}

class PendingAttachment extends DataClass
    implements Insertable<PendingAttachment> {
  final String localUuid;
  final String ownerUserUuid;
  final String? serverUuid;
  final String reportLocalUuid;
  final String localPath;
  final String mediaType;
  final String checksumSha256;
  final int byteSize;
  final String syncStatus;
  final int retryCount;
  final DateTime createdAt;
  final DateTime updatedAt;
  final String? syncError;
  final String metadataJson;
  final String? idempotencyKey;
  const PendingAttachment({
    required this.localUuid,
    required this.ownerUserUuid,
    this.serverUuid,
    required this.reportLocalUuid,
    required this.localPath,
    required this.mediaType,
    required this.checksumSha256,
    required this.byteSize,
    required this.syncStatus,
    required this.retryCount,
    required this.createdAt,
    required this.updatedAt,
    this.syncError,
    required this.metadataJson,
    this.idempotencyKey,
  });
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['local_uuid'] = Variable<String>(localUuid);
    map['owner_user_uuid'] = Variable<String>(ownerUserUuid);
    if (!nullToAbsent || serverUuid != null) {
      map['server_uuid'] = Variable<String>(serverUuid);
    }
    map['report_local_uuid'] = Variable<String>(reportLocalUuid);
    map['local_path'] = Variable<String>(localPath);
    map['media_type'] = Variable<String>(mediaType);
    map['checksum_sha256'] = Variable<String>(checksumSha256);
    map['byte_size'] = Variable<int>(byteSize);
    map['sync_status'] = Variable<String>(syncStatus);
    map['retry_count'] = Variable<int>(retryCount);
    map['created_at'] = Variable<DateTime>(createdAt);
    map['updated_at'] = Variable<DateTime>(updatedAt);
    if (!nullToAbsent || syncError != null) {
      map['sync_error'] = Variable<String>(syncError);
    }
    map['metadata_json'] = Variable<String>(metadataJson);
    if (!nullToAbsent || idempotencyKey != null) {
      map['idempotency_key'] = Variable<String>(idempotencyKey);
    }
    return map;
  }

  PendingAttachmentsCompanion toCompanion(bool nullToAbsent) {
    return PendingAttachmentsCompanion(
      localUuid: Value(localUuid),
      ownerUserUuid: Value(ownerUserUuid),
      serverUuid: serverUuid == null && nullToAbsent
          ? const Value.absent()
          : Value(serverUuid),
      reportLocalUuid: Value(reportLocalUuid),
      localPath: Value(localPath),
      mediaType: Value(mediaType),
      checksumSha256: Value(checksumSha256),
      byteSize: Value(byteSize),
      syncStatus: Value(syncStatus),
      retryCount: Value(retryCount),
      createdAt: Value(createdAt),
      updatedAt: Value(updatedAt),
      syncError: syncError == null && nullToAbsent
          ? const Value.absent()
          : Value(syncError),
      metadataJson: Value(metadataJson),
      idempotencyKey: idempotencyKey == null && nullToAbsent
          ? const Value.absent()
          : Value(idempotencyKey),
    );
  }

  factory PendingAttachment.fromJson(
    Map<String, dynamic> json, {
    ValueSerializer? serializer,
  }) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return PendingAttachment(
      localUuid: serializer.fromJson<String>(json['localUuid']),
      ownerUserUuid: serializer.fromJson<String>(json['ownerUserUuid']),
      serverUuid: serializer.fromJson<String?>(json['serverUuid']),
      reportLocalUuid: serializer.fromJson<String>(json['reportLocalUuid']),
      localPath: serializer.fromJson<String>(json['localPath']),
      mediaType: serializer.fromJson<String>(json['mediaType']),
      checksumSha256: serializer.fromJson<String>(json['checksumSha256']),
      byteSize: serializer.fromJson<int>(json['byteSize']),
      syncStatus: serializer.fromJson<String>(json['syncStatus']),
      retryCount: serializer.fromJson<int>(json['retryCount']),
      createdAt: serializer.fromJson<DateTime>(json['createdAt']),
      updatedAt: serializer.fromJson<DateTime>(json['updatedAt']),
      syncError: serializer.fromJson<String?>(json['syncError']),
      metadataJson: serializer.fromJson<String>(json['metadataJson']),
      idempotencyKey: serializer.fromJson<String?>(json['idempotencyKey']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'localUuid': serializer.toJson<String>(localUuid),
      'ownerUserUuid': serializer.toJson<String>(ownerUserUuid),
      'serverUuid': serializer.toJson<String?>(serverUuid),
      'reportLocalUuid': serializer.toJson<String>(reportLocalUuid),
      'localPath': serializer.toJson<String>(localPath),
      'mediaType': serializer.toJson<String>(mediaType),
      'checksumSha256': serializer.toJson<String>(checksumSha256),
      'byteSize': serializer.toJson<int>(byteSize),
      'syncStatus': serializer.toJson<String>(syncStatus),
      'retryCount': serializer.toJson<int>(retryCount),
      'createdAt': serializer.toJson<DateTime>(createdAt),
      'updatedAt': serializer.toJson<DateTime>(updatedAt),
      'syncError': serializer.toJson<String?>(syncError),
      'metadataJson': serializer.toJson<String>(metadataJson),
      'idempotencyKey': serializer.toJson<String?>(idempotencyKey),
    };
  }

  PendingAttachment copyWith({
    String? localUuid,
    String? ownerUserUuid,
    Value<String?> serverUuid = const Value.absent(),
    String? reportLocalUuid,
    String? localPath,
    String? mediaType,
    String? checksumSha256,
    int? byteSize,
    String? syncStatus,
    int? retryCount,
    DateTime? createdAt,
    DateTime? updatedAt,
    Value<String?> syncError = const Value.absent(),
    String? metadataJson,
    Value<String?> idempotencyKey = const Value.absent(),
  }) => PendingAttachment(
    localUuid: localUuid ?? this.localUuid,
    ownerUserUuid: ownerUserUuid ?? this.ownerUserUuid,
    serverUuid: serverUuid.present ? serverUuid.value : this.serverUuid,
    reportLocalUuid: reportLocalUuid ?? this.reportLocalUuid,
    localPath: localPath ?? this.localPath,
    mediaType: mediaType ?? this.mediaType,
    checksumSha256: checksumSha256 ?? this.checksumSha256,
    byteSize: byteSize ?? this.byteSize,
    syncStatus: syncStatus ?? this.syncStatus,
    retryCount: retryCount ?? this.retryCount,
    createdAt: createdAt ?? this.createdAt,
    updatedAt: updatedAt ?? this.updatedAt,
    syncError: syncError.present ? syncError.value : this.syncError,
    metadataJson: metadataJson ?? this.metadataJson,
    idempotencyKey: idempotencyKey.present
        ? idempotencyKey.value
        : this.idempotencyKey,
  );
  PendingAttachment copyWithCompanion(PendingAttachmentsCompanion data) {
    return PendingAttachment(
      localUuid: data.localUuid.present ? data.localUuid.value : this.localUuid,
      ownerUserUuid: data.ownerUserUuid.present
          ? data.ownerUserUuid.value
          : this.ownerUserUuid,
      serverUuid: data.serverUuid.present
          ? data.serverUuid.value
          : this.serverUuid,
      reportLocalUuid: data.reportLocalUuid.present
          ? data.reportLocalUuid.value
          : this.reportLocalUuid,
      localPath: data.localPath.present ? data.localPath.value : this.localPath,
      mediaType: data.mediaType.present ? data.mediaType.value : this.mediaType,
      checksumSha256: data.checksumSha256.present
          ? data.checksumSha256.value
          : this.checksumSha256,
      byteSize: data.byteSize.present ? data.byteSize.value : this.byteSize,
      syncStatus: data.syncStatus.present
          ? data.syncStatus.value
          : this.syncStatus,
      retryCount: data.retryCount.present
          ? data.retryCount.value
          : this.retryCount,
      createdAt: data.createdAt.present ? data.createdAt.value : this.createdAt,
      updatedAt: data.updatedAt.present ? data.updatedAt.value : this.updatedAt,
      syncError: data.syncError.present ? data.syncError.value : this.syncError,
      metadataJson: data.metadataJson.present
          ? data.metadataJson.value
          : this.metadataJson,
      idempotencyKey: data.idempotencyKey.present
          ? data.idempotencyKey.value
          : this.idempotencyKey,
    );
  }

  @override
  String toString() {
    return (StringBuffer('PendingAttachment(')
          ..write('localUuid: $localUuid, ')
          ..write('ownerUserUuid: $ownerUserUuid, ')
          ..write('serverUuid: $serverUuid, ')
          ..write('reportLocalUuid: $reportLocalUuid, ')
          ..write('localPath: $localPath, ')
          ..write('mediaType: $mediaType, ')
          ..write('checksumSha256: $checksumSha256, ')
          ..write('byteSize: $byteSize, ')
          ..write('syncStatus: $syncStatus, ')
          ..write('retryCount: $retryCount, ')
          ..write('createdAt: $createdAt, ')
          ..write('updatedAt: $updatedAt, ')
          ..write('syncError: $syncError, ')
          ..write('metadataJson: $metadataJson, ')
          ..write('idempotencyKey: $idempotencyKey')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(
    localUuid,
    ownerUserUuid,
    serverUuid,
    reportLocalUuid,
    localPath,
    mediaType,
    checksumSha256,
    byteSize,
    syncStatus,
    retryCount,
    createdAt,
    updatedAt,
    syncError,
    metadataJson,
    idempotencyKey,
  );
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is PendingAttachment &&
          other.localUuid == this.localUuid &&
          other.ownerUserUuid == this.ownerUserUuid &&
          other.serverUuid == this.serverUuid &&
          other.reportLocalUuid == this.reportLocalUuid &&
          other.localPath == this.localPath &&
          other.mediaType == this.mediaType &&
          other.checksumSha256 == this.checksumSha256 &&
          other.byteSize == this.byteSize &&
          other.syncStatus == this.syncStatus &&
          other.retryCount == this.retryCount &&
          other.createdAt == this.createdAt &&
          other.updatedAt == this.updatedAt &&
          other.syncError == this.syncError &&
          other.metadataJson == this.metadataJson &&
          other.idempotencyKey == this.idempotencyKey);
}

class PendingAttachmentsCompanion extends UpdateCompanion<PendingAttachment> {
  final Value<String> localUuid;
  final Value<String> ownerUserUuid;
  final Value<String?> serverUuid;
  final Value<String> reportLocalUuid;
  final Value<String> localPath;
  final Value<String> mediaType;
  final Value<String> checksumSha256;
  final Value<int> byteSize;
  final Value<String> syncStatus;
  final Value<int> retryCount;
  final Value<DateTime> createdAt;
  final Value<DateTime> updatedAt;
  final Value<String?> syncError;
  final Value<String> metadataJson;
  final Value<String?> idempotencyKey;
  final Value<int> rowid;
  const PendingAttachmentsCompanion({
    this.localUuid = const Value.absent(),
    this.ownerUserUuid = const Value.absent(),
    this.serverUuid = const Value.absent(),
    this.reportLocalUuid = const Value.absent(),
    this.localPath = const Value.absent(),
    this.mediaType = const Value.absent(),
    this.checksumSha256 = const Value.absent(),
    this.byteSize = const Value.absent(),
    this.syncStatus = const Value.absent(),
    this.retryCount = const Value.absent(),
    this.createdAt = const Value.absent(),
    this.updatedAt = const Value.absent(),
    this.syncError = const Value.absent(),
    this.metadataJson = const Value.absent(),
    this.idempotencyKey = const Value.absent(),
    this.rowid = const Value.absent(),
  });
  PendingAttachmentsCompanion.insert({
    required String localUuid,
    required String ownerUserUuid,
    this.serverUuid = const Value.absent(),
    required String reportLocalUuid,
    required String localPath,
    required String mediaType,
    required String checksumSha256,
    required int byteSize,
    required String syncStatus,
    this.retryCount = const Value.absent(),
    required DateTime createdAt,
    required DateTime updatedAt,
    this.syncError = const Value.absent(),
    this.metadataJson = const Value.absent(),
    this.idempotencyKey = const Value.absent(),
    this.rowid = const Value.absent(),
  }) : localUuid = Value(localUuid),
       ownerUserUuid = Value(ownerUserUuid),
       reportLocalUuid = Value(reportLocalUuid),
       localPath = Value(localPath),
       mediaType = Value(mediaType),
       checksumSha256 = Value(checksumSha256),
       byteSize = Value(byteSize),
       syncStatus = Value(syncStatus),
       createdAt = Value(createdAt),
       updatedAt = Value(updatedAt);
  static Insertable<PendingAttachment> custom({
    Expression<String>? localUuid,
    Expression<String>? ownerUserUuid,
    Expression<String>? serverUuid,
    Expression<String>? reportLocalUuid,
    Expression<String>? localPath,
    Expression<String>? mediaType,
    Expression<String>? checksumSha256,
    Expression<int>? byteSize,
    Expression<String>? syncStatus,
    Expression<int>? retryCount,
    Expression<DateTime>? createdAt,
    Expression<DateTime>? updatedAt,
    Expression<String>? syncError,
    Expression<String>? metadataJson,
    Expression<String>? idempotencyKey,
    Expression<int>? rowid,
  }) {
    return RawValuesInsertable({
      if (localUuid != null) 'local_uuid': localUuid,
      if (ownerUserUuid != null) 'owner_user_uuid': ownerUserUuid,
      if (serverUuid != null) 'server_uuid': serverUuid,
      if (reportLocalUuid != null) 'report_local_uuid': reportLocalUuid,
      if (localPath != null) 'local_path': localPath,
      if (mediaType != null) 'media_type': mediaType,
      if (checksumSha256 != null) 'checksum_sha256': checksumSha256,
      if (byteSize != null) 'byte_size': byteSize,
      if (syncStatus != null) 'sync_status': syncStatus,
      if (retryCount != null) 'retry_count': retryCount,
      if (createdAt != null) 'created_at': createdAt,
      if (updatedAt != null) 'updated_at': updatedAt,
      if (syncError != null) 'sync_error': syncError,
      if (metadataJson != null) 'metadata_json': metadataJson,
      if (idempotencyKey != null) 'idempotency_key': idempotencyKey,
      if (rowid != null) 'rowid': rowid,
    });
  }

  PendingAttachmentsCompanion copyWith({
    Value<String>? localUuid,
    Value<String>? ownerUserUuid,
    Value<String?>? serverUuid,
    Value<String>? reportLocalUuid,
    Value<String>? localPath,
    Value<String>? mediaType,
    Value<String>? checksumSha256,
    Value<int>? byteSize,
    Value<String>? syncStatus,
    Value<int>? retryCount,
    Value<DateTime>? createdAt,
    Value<DateTime>? updatedAt,
    Value<String?>? syncError,
    Value<String>? metadataJson,
    Value<String?>? idempotencyKey,
    Value<int>? rowid,
  }) {
    return PendingAttachmentsCompanion(
      localUuid: localUuid ?? this.localUuid,
      ownerUserUuid: ownerUserUuid ?? this.ownerUserUuid,
      serverUuid: serverUuid ?? this.serverUuid,
      reportLocalUuid: reportLocalUuid ?? this.reportLocalUuid,
      localPath: localPath ?? this.localPath,
      mediaType: mediaType ?? this.mediaType,
      checksumSha256: checksumSha256 ?? this.checksumSha256,
      byteSize: byteSize ?? this.byteSize,
      syncStatus: syncStatus ?? this.syncStatus,
      retryCount: retryCount ?? this.retryCount,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      syncError: syncError ?? this.syncError,
      metadataJson: metadataJson ?? this.metadataJson,
      idempotencyKey: idempotencyKey ?? this.idempotencyKey,
      rowid: rowid ?? this.rowid,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (localUuid.present) {
      map['local_uuid'] = Variable<String>(localUuid.value);
    }
    if (ownerUserUuid.present) {
      map['owner_user_uuid'] = Variable<String>(ownerUserUuid.value);
    }
    if (serverUuid.present) {
      map['server_uuid'] = Variable<String>(serverUuid.value);
    }
    if (reportLocalUuid.present) {
      map['report_local_uuid'] = Variable<String>(reportLocalUuid.value);
    }
    if (localPath.present) {
      map['local_path'] = Variable<String>(localPath.value);
    }
    if (mediaType.present) {
      map['media_type'] = Variable<String>(mediaType.value);
    }
    if (checksumSha256.present) {
      map['checksum_sha256'] = Variable<String>(checksumSha256.value);
    }
    if (byteSize.present) {
      map['byte_size'] = Variable<int>(byteSize.value);
    }
    if (syncStatus.present) {
      map['sync_status'] = Variable<String>(syncStatus.value);
    }
    if (retryCount.present) {
      map['retry_count'] = Variable<int>(retryCount.value);
    }
    if (createdAt.present) {
      map['created_at'] = Variable<DateTime>(createdAt.value);
    }
    if (updatedAt.present) {
      map['updated_at'] = Variable<DateTime>(updatedAt.value);
    }
    if (syncError.present) {
      map['sync_error'] = Variable<String>(syncError.value);
    }
    if (metadataJson.present) {
      map['metadata_json'] = Variable<String>(metadataJson.value);
    }
    if (idempotencyKey.present) {
      map['idempotency_key'] = Variable<String>(idempotencyKey.value);
    }
    if (rowid.present) {
      map['rowid'] = Variable<int>(rowid.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('PendingAttachmentsCompanion(')
          ..write('localUuid: $localUuid, ')
          ..write('ownerUserUuid: $ownerUserUuid, ')
          ..write('serverUuid: $serverUuid, ')
          ..write('reportLocalUuid: $reportLocalUuid, ')
          ..write('localPath: $localPath, ')
          ..write('mediaType: $mediaType, ')
          ..write('checksumSha256: $checksumSha256, ')
          ..write('byteSize: $byteSize, ')
          ..write('syncStatus: $syncStatus, ')
          ..write('retryCount: $retryCount, ')
          ..write('createdAt: $createdAt, ')
          ..write('updatedAt: $updatedAt, ')
          ..write('syncError: $syncError, ')
          ..write('metadataJson: $metadataJson, ')
          ..write('idempotencyKey: $idempotencyKey, ')
          ..write('rowid: $rowid')
          ..write(')'))
        .toString();
  }
}

class $SyncMetadataEntriesTable extends SyncMetadataEntries
    with TableInfo<$SyncMetadataEntriesTable, SyncMetadataEntry> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $SyncMetadataEntriesTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _ownerUserUuidMeta = const VerificationMeta(
    'ownerUserUuid',
  );
  @override
  late final GeneratedColumn<String> ownerUserUuid = GeneratedColumn<String>(
    'owner_user_uuid',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _keyMeta = const VerificationMeta('key');
  @override
  late final GeneratedColumn<String> key = GeneratedColumn<String>(
    'key',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _valueMeta = const VerificationMeta('value');
  @override
  late final GeneratedColumn<String> value = GeneratedColumn<String>(
    'value',
    aliasedName,
    true,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
  );
  static const VerificationMeta _updatedAtMeta = const VerificationMeta(
    'updatedAt',
  );
  @override
  late final GeneratedColumn<DateTime> updatedAt = GeneratedColumn<DateTime>(
    'updated_at',
    aliasedName,
    false,
    type: DriftSqlType.dateTime,
    requiredDuringInsert: true,
  );
  @override
  List<GeneratedColumn> get $columns => [ownerUserUuid, key, value, updatedAt];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'sync_metadata_entries';
  @override
  VerificationContext validateIntegrity(
    Insertable<SyncMetadataEntry> instance, {
    bool isInserting = false,
  }) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('owner_user_uuid')) {
      context.handle(
        _ownerUserUuidMeta,
        ownerUserUuid.isAcceptableOrUnknown(
          data['owner_user_uuid']!,
          _ownerUserUuidMeta,
        ),
      );
    } else if (isInserting) {
      context.missing(_ownerUserUuidMeta);
    }
    if (data.containsKey('key')) {
      context.handle(
        _keyMeta,
        key.isAcceptableOrUnknown(data['key']!, _keyMeta),
      );
    } else if (isInserting) {
      context.missing(_keyMeta);
    }
    if (data.containsKey('value')) {
      context.handle(
        _valueMeta,
        value.isAcceptableOrUnknown(data['value']!, _valueMeta),
      );
    }
    if (data.containsKey('updated_at')) {
      context.handle(
        _updatedAtMeta,
        updatedAt.isAcceptableOrUnknown(data['updated_at']!, _updatedAtMeta),
      );
    } else if (isInserting) {
      context.missing(_updatedAtMeta);
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {ownerUserUuid, key};
  @override
  SyncMetadataEntry map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return SyncMetadataEntry(
      ownerUserUuid: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}owner_user_uuid'],
      )!,
      key: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}key'],
      )!,
      value: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}value'],
      ),
      updatedAt: attachedDatabase.typeMapping.read(
        DriftSqlType.dateTime,
        data['${effectivePrefix}updated_at'],
      )!,
    );
  }

  @override
  $SyncMetadataEntriesTable createAlias(String alias) {
    return $SyncMetadataEntriesTable(attachedDatabase, alias);
  }
}

class SyncMetadataEntry extends DataClass
    implements Insertable<SyncMetadataEntry> {
  final String ownerUserUuid;
  final String key;
  final String? value;
  final DateTime updatedAt;
  const SyncMetadataEntry({
    required this.ownerUserUuid,
    required this.key,
    this.value,
    required this.updatedAt,
  });
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['owner_user_uuid'] = Variable<String>(ownerUserUuid);
    map['key'] = Variable<String>(key);
    if (!nullToAbsent || value != null) {
      map['value'] = Variable<String>(value);
    }
    map['updated_at'] = Variable<DateTime>(updatedAt);
    return map;
  }

  SyncMetadataEntriesCompanion toCompanion(bool nullToAbsent) {
    return SyncMetadataEntriesCompanion(
      ownerUserUuid: Value(ownerUserUuid),
      key: Value(key),
      value: value == null && nullToAbsent
          ? const Value.absent()
          : Value(value),
      updatedAt: Value(updatedAt),
    );
  }

  factory SyncMetadataEntry.fromJson(
    Map<String, dynamic> json, {
    ValueSerializer? serializer,
  }) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return SyncMetadataEntry(
      ownerUserUuid: serializer.fromJson<String>(json['ownerUserUuid']),
      key: serializer.fromJson<String>(json['key']),
      value: serializer.fromJson<String?>(json['value']),
      updatedAt: serializer.fromJson<DateTime>(json['updatedAt']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'ownerUserUuid': serializer.toJson<String>(ownerUserUuid),
      'key': serializer.toJson<String>(key),
      'value': serializer.toJson<String?>(value),
      'updatedAt': serializer.toJson<DateTime>(updatedAt),
    };
  }

  SyncMetadataEntry copyWith({
    String? ownerUserUuid,
    String? key,
    Value<String?> value = const Value.absent(),
    DateTime? updatedAt,
  }) => SyncMetadataEntry(
    ownerUserUuid: ownerUserUuid ?? this.ownerUserUuid,
    key: key ?? this.key,
    value: value.present ? value.value : this.value,
    updatedAt: updatedAt ?? this.updatedAt,
  );
  SyncMetadataEntry copyWithCompanion(SyncMetadataEntriesCompanion data) {
    return SyncMetadataEntry(
      ownerUserUuid: data.ownerUserUuid.present
          ? data.ownerUserUuid.value
          : this.ownerUserUuid,
      key: data.key.present ? data.key.value : this.key,
      value: data.value.present ? data.value.value : this.value,
      updatedAt: data.updatedAt.present ? data.updatedAt.value : this.updatedAt,
    );
  }

  @override
  String toString() {
    return (StringBuffer('SyncMetadataEntry(')
          ..write('ownerUserUuid: $ownerUserUuid, ')
          ..write('key: $key, ')
          ..write('value: $value, ')
          ..write('updatedAt: $updatedAt')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(ownerUserUuid, key, value, updatedAt);
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is SyncMetadataEntry &&
          other.ownerUserUuid == this.ownerUserUuid &&
          other.key == this.key &&
          other.value == this.value &&
          other.updatedAt == this.updatedAt);
}

class SyncMetadataEntriesCompanion extends UpdateCompanion<SyncMetadataEntry> {
  final Value<String> ownerUserUuid;
  final Value<String> key;
  final Value<String?> value;
  final Value<DateTime> updatedAt;
  final Value<int> rowid;
  const SyncMetadataEntriesCompanion({
    this.ownerUserUuid = const Value.absent(),
    this.key = const Value.absent(),
    this.value = const Value.absent(),
    this.updatedAt = const Value.absent(),
    this.rowid = const Value.absent(),
  });
  SyncMetadataEntriesCompanion.insert({
    required String ownerUserUuid,
    required String key,
    this.value = const Value.absent(),
    required DateTime updatedAt,
    this.rowid = const Value.absent(),
  }) : ownerUserUuid = Value(ownerUserUuid),
       key = Value(key),
       updatedAt = Value(updatedAt);
  static Insertable<SyncMetadataEntry> custom({
    Expression<String>? ownerUserUuid,
    Expression<String>? key,
    Expression<String>? value,
    Expression<DateTime>? updatedAt,
    Expression<int>? rowid,
  }) {
    return RawValuesInsertable({
      if (ownerUserUuid != null) 'owner_user_uuid': ownerUserUuid,
      if (key != null) 'key': key,
      if (value != null) 'value': value,
      if (updatedAt != null) 'updated_at': updatedAt,
      if (rowid != null) 'rowid': rowid,
    });
  }

  SyncMetadataEntriesCompanion copyWith({
    Value<String>? ownerUserUuid,
    Value<String>? key,
    Value<String?>? value,
    Value<DateTime>? updatedAt,
    Value<int>? rowid,
  }) {
    return SyncMetadataEntriesCompanion(
      ownerUserUuid: ownerUserUuid ?? this.ownerUserUuid,
      key: key ?? this.key,
      value: value ?? this.value,
      updatedAt: updatedAt ?? this.updatedAt,
      rowid: rowid ?? this.rowid,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (ownerUserUuid.present) {
      map['owner_user_uuid'] = Variable<String>(ownerUserUuid.value);
    }
    if (key.present) {
      map['key'] = Variable<String>(key.value);
    }
    if (value.present) {
      map['value'] = Variable<String>(value.value);
    }
    if (updatedAt.present) {
      map['updated_at'] = Variable<DateTime>(updatedAt.value);
    }
    if (rowid.present) {
      map['rowid'] = Variable<int>(rowid.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('SyncMetadataEntriesCompanion(')
          ..write('ownerUserUuid: $ownerUserUuid, ')
          ..write('key: $key, ')
          ..write('value: $value, ')
          ..write('updatedAt: $updatedAt, ')
          ..write('rowid: $rowid')
          ..write(')'))
        .toString();
  }
}

class $ConflictRecordsTable extends ConflictRecords
    with TableInfo<$ConflictRecordsTable, ConflictRecord> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $ConflictRecordsTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _uuidMeta = const VerificationMeta('uuid');
  @override
  late final GeneratedColumn<String> uuid = GeneratedColumn<String>(
    'uuid',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _ownerUserUuidMeta = const VerificationMeta(
    'ownerUserUuid',
  );
  @override
  late final GeneratedColumn<String> ownerUserUuid = GeneratedColumn<String>(
    'owner_user_uuid',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _resourceTypeMeta = const VerificationMeta(
    'resourceType',
  );
  @override
  late final GeneratedColumn<String> resourceType = GeneratedColumn<String>(
    'resource_type',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _localUuidMeta = const VerificationMeta(
    'localUuid',
  );
  @override
  late final GeneratedColumn<String> localUuid = GeneratedColumn<String>(
    'local_uuid',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _serverUuidMeta = const VerificationMeta(
    'serverUuid',
  );
  @override
  late final GeneratedColumn<String> serverUuid = GeneratedColumn<String>(
    'server_uuid',
    aliasedName,
    true,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
  );
  static const VerificationMeta _localPayloadJsonMeta = const VerificationMeta(
    'localPayloadJson',
  );
  @override
  late final GeneratedColumn<String> localPayloadJson = GeneratedColumn<String>(
    'local_payload_json',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _serverPayloadJsonMeta = const VerificationMeta(
    'serverPayloadJson',
  );
  @override
  late final GeneratedColumn<String> serverPayloadJson =
      GeneratedColumn<String>(
        'server_payload_json',
        aliasedName,
        false,
        type: DriftSqlType.string,
        requiredDuringInsert: true,
      );
  static const VerificationMeta _conflictingFieldsJsonMeta =
      const VerificationMeta('conflictingFieldsJson');
  @override
  late final GeneratedColumn<String> conflictingFieldsJson =
      GeneratedColumn<String>(
        'conflicting_fields_json',
        aliasedName,
        true,
        type: DriftSqlType.string,
        requiredDuringInsert: false,
      );
  static const VerificationMeta _statusMeta = const VerificationMeta('status');
  @override
  late final GeneratedColumn<String> status = GeneratedColumn<String>(
    'status',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _serverValueRequiredMeta =
      const VerificationMeta('serverValueRequired');
  @override
  late final GeneratedColumn<bool> serverValueRequired = GeneratedColumn<bool>(
    'server_value_required',
    aliasedName,
    false,
    type: DriftSqlType.bool,
    requiredDuringInsert: false,
    defaultConstraints: GeneratedColumn.constraintIsAlways(
      'CHECK ("server_value_required" IN (0, 1))',
    ),
    defaultValue: const Constant(false),
  );
  static const VerificationMeta _detectedAtMeta = const VerificationMeta(
    'detectedAt',
  );
  @override
  late final GeneratedColumn<DateTime> detectedAt = GeneratedColumn<DateTime>(
    'detected_at',
    aliasedName,
    false,
    type: DriftSqlType.dateTime,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _resolvedAtMeta = const VerificationMeta(
    'resolvedAt',
  );
  @override
  late final GeneratedColumn<DateTime> resolvedAt = GeneratedColumn<DateTime>(
    'resolved_at',
    aliasedName,
    true,
    type: DriftSqlType.dateTime,
    requiredDuringInsert: false,
  );
  @override
  List<GeneratedColumn> get $columns => [
    uuid,
    ownerUserUuid,
    resourceType,
    localUuid,
    serverUuid,
    localPayloadJson,
    serverPayloadJson,
    conflictingFieldsJson,
    status,
    serverValueRequired,
    detectedAt,
    resolvedAt,
  ];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'conflict_records';
  @override
  VerificationContext validateIntegrity(
    Insertable<ConflictRecord> instance, {
    bool isInserting = false,
  }) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('uuid')) {
      context.handle(
        _uuidMeta,
        uuid.isAcceptableOrUnknown(data['uuid']!, _uuidMeta),
      );
    } else if (isInserting) {
      context.missing(_uuidMeta);
    }
    if (data.containsKey('owner_user_uuid')) {
      context.handle(
        _ownerUserUuidMeta,
        ownerUserUuid.isAcceptableOrUnknown(
          data['owner_user_uuid']!,
          _ownerUserUuidMeta,
        ),
      );
    } else if (isInserting) {
      context.missing(_ownerUserUuidMeta);
    }
    if (data.containsKey('resource_type')) {
      context.handle(
        _resourceTypeMeta,
        resourceType.isAcceptableOrUnknown(
          data['resource_type']!,
          _resourceTypeMeta,
        ),
      );
    } else if (isInserting) {
      context.missing(_resourceTypeMeta);
    }
    if (data.containsKey('local_uuid')) {
      context.handle(
        _localUuidMeta,
        localUuid.isAcceptableOrUnknown(data['local_uuid']!, _localUuidMeta),
      );
    } else if (isInserting) {
      context.missing(_localUuidMeta);
    }
    if (data.containsKey('server_uuid')) {
      context.handle(
        _serverUuidMeta,
        serverUuid.isAcceptableOrUnknown(data['server_uuid']!, _serverUuidMeta),
      );
    }
    if (data.containsKey('local_payload_json')) {
      context.handle(
        _localPayloadJsonMeta,
        localPayloadJson.isAcceptableOrUnknown(
          data['local_payload_json']!,
          _localPayloadJsonMeta,
        ),
      );
    } else if (isInserting) {
      context.missing(_localPayloadJsonMeta);
    }
    if (data.containsKey('server_payload_json')) {
      context.handle(
        _serverPayloadJsonMeta,
        serverPayloadJson.isAcceptableOrUnknown(
          data['server_payload_json']!,
          _serverPayloadJsonMeta,
        ),
      );
    } else if (isInserting) {
      context.missing(_serverPayloadJsonMeta);
    }
    if (data.containsKey('conflicting_fields_json')) {
      context.handle(
        _conflictingFieldsJsonMeta,
        conflictingFieldsJson.isAcceptableOrUnknown(
          data['conflicting_fields_json']!,
          _conflictingFieldsJsonMeta,
        ),
      );
    }
    if (data.containsKey('status')) {
      context.handle(
        _statusMeta,
        status.isAcceptableOrUnknown(data['status']!, _statusMeta),
      );
    } else if (isInserting) {
      context.missing(_statusMeta);
    }
    if (data.containsKey('server_value_required')) {
      context.handle(
        _serverValueRequiredMeta,
        serverValueRequired.isAcceptableOrUnknown(
          data['server_value_required']!,
          _serverValueRequiredMeta,
        ),
      );
    }
    if (data.containsKey('detected_at')) {
      context.handle(
        _detectedAtMeta,
        detectedAt.isAcceptableOrUnknown(data['detected_at']!, _detectedAtMeta),
      );
    } else if (isInserting) {
      context.missing(_detectedAtMeta);
    }
    if (data.containsKey('resolved_at')) {
      context.handle(
        _resolvedAtMeta,
        resolvedAt.isAcceptableOrUnknown(data['resolved_at']!, _resolvedAtMeta),
      );
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {uuid};
  @override
  ConflictRecord map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return ConflictRecord(
      uuid: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}uuid'],
      )!,
      ownerUserUuid: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}owner_user_uuid'],
      )!,
      resourceType: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}resource_type'],
      )!,
      localUuid: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}local_uuid'],
      )!,
      serverUuid: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}server_uuid'],
      ),
      localPayloadJson: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}local_payload_json'],
      )!,
      serverPayloadJson: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}server_payload_json'],
      )!,
      conflictingFieldsJson: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}conflicting_fields_json'],
      ),
      status: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}status'],
      )!,
      serverValueRequired: attachedDatabase.typeMapping.read(
        DriftSqlType.bool,
        data['${effectivePrefix}server_value_required'],
      )!,
      detectedAt: attachedDatabase.typeMapping.read(
        DriftSqlType.dateTime,
        data['${effectivePrefix}detected_at'],
      )!,
      resolvedAt: attachedDatabase.typeMapping.read(
        DriftSqlType.dateTime,
        data['${effectivePrefix}resolved_at'],
      ),
    );
  }

  @override
  $ConflictRecordsTable createAlias(String alias) {
    return $ConflictRecordsTable(attachedDatabase, alias);
  }
}

class ConflictRecord extends DataClass implements Insertable<ConflictRecord> {
  final String uuid;
  final String ownerUserUuid;
  final String resourceType;
  final String localUuid;
  final String? serverUuid;
  final String localPayloadJson;
  final String serverPayloadJson;
  final String? conflictingFieldsJson;
  final String status;
  final bool serverValueRequired;
  final DateTime detectedAt;
  final DateTime? resolvedAt;
  const ConflictRecord({
    required this.uuid,
    required this.ownerUserUuid,
    required this.resourceType,
    required this.localUuid,
    this.serverUuid,
    required this.localPayloadJson,
    required this.serverPayloadJson,
    this.conflictingFieldsJson,
    required this.status,
    required this.serverValueRequired,
    required this.detectedAt,
    this.resolvedAt,
  });
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['uuid'] = Variable<String>(uuid);
    map['owner_user_uuid'] = Variable<String>(ownerUserUuid);
    map['resource_type'] = Variable<String>(resourceType);
    map['local_uuid'] = Variable<String>(localUuid);
    if (!nullToAbsent || serverUuid != null) {
      map['server_uuid'] = Variable<String>(serverUuid);
    }
    map['local_payload_json'] = Variable<String>(localPayloadJson);
    map['server_payload_json'] = Variable<String>(serverPayloadJson);
    if (!nullToAbsent || conflictingFieldsJson != null) {
      map['conflicting_fields_json'] = Variable<String>(conflictingFieldsJson);
    }
    map['status'] = Variable<String>(status);
    map['server_value_required'] = Variable<bool>(serverValueRequired);
    map['detected_at'] = Variable<DateTime>(detectedAt);
    if (!nullToAbsent || resolvedAt != null) {
      map['resolved_at'] = Variable<DateTime>(resolvedAt);
    }
    return map;
  }

  ConflictRecordsCompanion toCompanion(bool nullToAbsent) {
    return ConflictRecordsCompanion(
      uuid: Value(uuid),
      ownerUserUuid: Value(ownerUserUuid),
      resourceType: Value(resourceType),
      localUuid: Value(localUuid),
      serverUuid: serverUuid == null && nullToAbsent
          ? const Value.absent()
          : Value(serverUuid),
      localPayloadJson: Value(localPayloadJson),
      serverPayloadJson: Value(serverPayloadJson),
      conflictingFieldsJson: conflictingFieldsJson == null && nullToAbsent
          ? const Value.absent()
          : Value(conflictingFieldsJson),
      status: Value(status),
      serverValueRequired: Value(serverValueRequired),
      detectedAt: Value(detectedAt),
      resolvedAt: resolvedAt == null && nullToAbsent
          ? const Value.absent()
          : Value(resolvedAt),
    );
  }

  factory ConflictRecord.fromJson(
    Map<String, dynamic> json, {
    ValueSerializer? serializer,
  }) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return ConflictRecord(
      uuid: serializer.fromJson<String>(json['uuid']),
      ownerUserUuid: serializer.fromJson<String>(json['ownerUserUuid']),
      resourceType: serializer.fromJson<String>(json['resourceType']),
      localUuid: serializer.fromJson<String>(json['localUuid']),
      serverUuid: serializer.fromJson<String?>(json['serverUuid']),
      localPayloadJson: serializer.fromJson<String>(json['localPayloadJson']),
      serverPayloadJson: serializer.fromJson<String>(json['serverPayloadJson']),
      conflictingFieldsJson: serializer.fromJson<String?>(
        json['conflictingFieldsJson'],
      ),
      status: serializer.fromJson<String>(json['status']),
      serverValueRequired: serializer.fromJson<bool>(
        json['serverValueRequired'],
      ),
      detectedAt: serializer.fromJson<DateTime>(json['detectedAt']),
      resolvedAt: serializer.fromJson<DateTime?>(json['resolvedAt']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'uuid': serializer.toJson<String>(uuid),
      'ownerUserUuid': serializer.toJson<String>(ownerUserUuid),
      'resourceType': serializer.toJson<String>(resourceType),
      'localUuid': serializer.toJson<String>(localUuid),
      'serverUuid': serializer.toJson<String?>(serverUuid),
      'localPayloadJson': serializer.toJson<String>(localPayloadJson),
      'serverPayloadJson': serializer.toJson<String>(serverPayloadJson),
      'conflictingFieldsJson': serializer.toJson<String?>(
        conflictingFieldsJson,
      ),
      'status': serializer.toJson<String>(status),
      'serverValueRequired': serializer.toJson<bool>(serverValueRequired),
      'detectedAt': serializer.toJson<DateTime>(detectedAt),
      'resolvedAt': serializer.toJson<DateTime?>(resolvedAt),
    };
  }

  ConflictRecord copyWith({
    String? uuid,
    String? ownerUserUuid,
    String? resourceType,
    String? localUuid,
    Value<String?> serverUuid = const Value.absent(),
    String? localPayloadJson,
    String? serverPayloadJson,
    Value<String?> conflictingFieldsJson = const Value.absent(),
    String? status,
    bool? serverValueRequired,
    DateTime? detectedAt,
    Value<DateTime?> resolvedAt = const Value.absent(),
  }) => ConflictRecord(
    uuid: uuid ?? this.uuid,
    ownerUserUuid: ownerUserUuid ?? this.ownerUserUuid,
    resourceType: resourceType ?? this.resourceType,
    localUuid: localUuid ?? this.localUuid,
    serverUuid: serverUuid.present ? serverUuid.value : this.serverUuid,
    localPayloadJson: localPayloadJson ?? this.localPayloadJson,
    serverPayloadJson: serverPayloadJson ?? this.serverPayloadJson,
    conflictingFieldsJson: conflictingFieldsJson.present
        ? conflictingFieldsJson.value
        : this.conflictingFieldsJson,
    status: status ?? this.status,
    serverValueRequired: serverValueRequired ?? this.serverValueRequired,
    detectedAt: detectedAt ?? this.detectedAt,
    resolvedAt: resolvedAt.present ? resolvedAt.value : this.resolvedAt,
  );
  ConflictRecord copyWithCompanion(ConflictRecordsCompanion data) {
    return ConflictRecord(
      uuid: data.uuid.present ? data.uuid.value : this.uuid,
      ownerUserUuid: data.ownerUserUuid.present
          ? data.ownerUserUuid.value
          : this.ownerUserUuid,
      resourceType: data.resourceType.present
          ? data.resourceType.value
          : this.resourceType,
      localUuid: data.localUuid.present ? data.localUuid.value : this.localUuid,
      serverUuid: data.serverUuid.present
          ? data.serverUuid.value
          : this.serverUuid,
      localPayloadJson: data.localPayloadJson.present
          ? data.localPayloadJson.value
          : this.localPayloadJson,
      serverPayloadJson: data.serverPayloadJson.present
          ? data.serverPayloadJson.value
          : this.serverPayloadJson,
      conflictingFieldsJson: data.conflictingFieldsJson.present
          ? data.conflictingFieldsJson.value
          : this.conflictingFieldsJson,
      status: data.status.present ? data.status.value : this.status,
      serverValueRequired: data.serverValueRequired.present
          ? data.serverValueRequired.value
          : this.serverValueRequired,
      detectedAt: data.detectedAt.present
          ? data.detectedAt.value
          : this.detectedAt,
      resolvedAt: data.resolvedAt.present
          ? data.resolvedAt.value
          : this.resolvedAt,
    );
  }

  @override
  String toString() {
    return (StringBuffer('ConflictRecord(')
          ..write('uuid: $uuid, ')
          ..write('ownerUserUuid: $ownerUserUuid, ')
          ..write('resourceType: $resourceType, ')
          ..write('localUuid: $localUuid, ')
          ..write('serverUuid: $serverUuid, ')
          ..write('localPayloadJson: $localPayloadJson, ')
          ..write('serverPayloadJson: $serverPayloadJson, ')
          ..write('conflictingFieldsJson: $conflictingFieldsJson, ')
          ..write('status: $status, ')
          ..write('serverValueRequired: $serverValueRequired, ')
          ..write('detectedAt: $detectedAt, ')
          ..write('resolvedAt: $resolvedAt')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(
    uuid,
    ownerUserUuid,
    resourceType,
    localUuid,
    serverUuid,
    localPayloadJson,
    serverPayloadJson,
    conflictingFieldsJson,
    status,
    serverValueRequired,
    detectedAt,
    resolvedAt,
  );
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is ConflictRecord &&
          other.uuid == this.uuid &&
          other.ownerUserUuid == this.ownerUserUuid &&
          other.resourceType == this.resourceType &&
          other.localUuid == this.localUuid &&
          other.serverUuid == this.serverUuid &&
          other.localPayloadJson == this.localPayloadJson &&
          other.serverPayloadJson == this.serverPayloadJson &&
          other.conflictingFieldsJson == this.conflictingFieldsJson &&
          other.status == this.status &&
          other.serverValueRequired == this.serverValueRequired &&
          other.detectedAt == this.detectedAt &&
          other.resolvedAt == this.resolvedAt);
}

class ConflictRecordsCompanion extends UpdateCompanion<ConflictRecord> {
  final Value<String> uuid;
  final Value<String> ownerUserUuid;
  final Value<String> resourceType;
  final Value<String> localUuid;
  final Value<String?> serverUuid;
  final Value<String> localPayloadJson;
  final Value<String> serverPayloadJson;
  final Value<String?> conflictingFieldsJson;
  final Value<String> status;
  final Value<bool> serverValueRequired;
  final Value<DateTime> detectedAt;
  final Value<DateTime?> resolvedAt;
  final Value<int> rowid;
  const ConflictRecordsCompanion({
    this.uuid = const Value.absent(),
    this.ownerUserUuid = const Value.absent(),
    this.resourceType = const Value.absent(),
    this.localUuid = const Value.absent(),
    this.serverUuid = const Value.absent(),
    this.localPayloadJson = const Value.absent(),
    this.serverPayloadJson = const Value.absent(),
    this.conflictingFieldsJson = const Value.absent(),
    this.status = const Value.absent(),
    this.serverValueRequired = const Value.absent(),
    this.detectedAt = const Value.absent(),
    this.resolvedAt = const Value.absent(),
    this.rowid = const Value.absent(),
  });
  ConflictRecordsCompanion.insert({
    required String uuid,
    required String ownerUserUuid,
    required String resourceType,
    required String localUuid,
    this.serverUuid = const Value.absent(),
    required String localPayloadJson,
    required String serverPayloadJson,
    this.conflictingFieldsJson = const Value.absent(),
    required String status,
    this.serverValueRequired = const Value.absent(),
    required DateTime detectedAt,
    this.resolvedAt = const Value.absent(),
    this.rowid = const Value.absent(),
  }) : uuid = Value(uuid),
       ownerUserUuid = Value(ownerUserUuid),
       resourceType = Value(resourceType),
       localUuid = Value(localUuid),
       localPayloadJson = Value(localPayloadJson),
       serverPayloadJson = Value(serverPayloadJson),
       status = Value(status),
       detectedAt = Value(detectedAt);
  static Insertable<ConflictRecord> custom({
    Expression<String>? uuid,
    Expression<String>? ownerUserUuid,
    Expression<String>? resourceType,
    Expression<String>? localUuid,
    Expression<String>? serverUuid,
    Expression<String>? localPayloadJson,
    Expression<String>? serverPayloadJson,
    Expression<String>? conflictingFieldsJson,
    Expression<String>? status,
    Expression<bool>? serverValueRequired,
    Expression<DateTime>? detectedAt,
    Expression<DateTime>? resolvedAt,
    Expression<int>? rowid,
  }) {
    return RawValuesInsertable({
      if (uuid != null) 'uuid': uuid,
      if (ownerUserUuid != null) 'owner_user_uuid': ownerUserUuid,
      if (resourceType != null) 'resource_type': resourceType,
      if (localUuid != null) 'local_uuid': localUuid,
      if (serverUuid != null) 'server_uuid': serverUuid,
      if (localPayloadJson != null) 'local_payload_json': localPayloadJson,
      if (serverPayloadJson != null) 'server_payload_json': serverPayloadJson,
      if (conflictingFieldsJson != null)
        'conflicting_fields_json': conflictingFieldsJson,
      if (status != null) 'status': status,
      if (serverValueRequired != null)
        'server_value_required': serverValueRequired,
      if (detectedAt != null) 'detected_at': detectedAt,
      if (resolvedAt != null) 'resolved_at': resolvedAt,
      if (rowid != null) 'rowid': rowid,
    });
  }

  ConflictRecordsCompanion copyWith({
    Value<String>? uuid,
    Value<String>? ownerUserUuid,
    Value<String>? resourceType,
    Value<String>? localUuid,
    Value<String?>? serverUuid,
    Value<String>? localPayloadJson,
    Value<String>? serverPayloadJson,
    Value<String?>? conflictingFieldsJson,
    Value<String>? status,
    Value<bool>? serverValueRequired,
    Value<DateTime>? detectedAt,
    Value<DateTime?>? resolvedAt,
    Value<int>? rowid,
  }) {
    return ConflictRecordsCompanion(
      uuid: uuid ?? this.uuid,
      ownerUserUuid: ownerUserUuid ?? this.ownerUserUuid,
      resourceType: resourceType ?? this.resourceType,
      localUuid: localUuid ?? this.localUuid,
      serverUuid: serverUuid ?? this.serverUuid,
      localPayloadJson: localPayloadJson ?? this.localPayloadJson,
      serverPayloadJson: serverPayloadJson ?? this.serverPayloadJson,
      conflictingFieldsJson:
          conflictingFieldsJson ?? this.conflictingFieldsJson,
      status: status ?? this.status,
      serverValueRequired: serverValueRequired ?? this.serverValueRequired,
      detectedAt: detectedAt ?? this.detectedAt,
      resolvedAt: resolvedAt ?? this.resolvedAt,
      rowid: rowid ?? this.rowid,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (uuid.present) {
      map['uuid'] = Variable<String>(uuid.value);
    }
    if (ownerUserUuid.present) {
      map['owner_user_uuid'] = Variable<String>(ownerUserUuid.value);
    }
    if (resourceType.present) {
      map['resource_type'] = Variable<String>(resourceType.value);
    }
    if (localUuid.present) {
      map['local_uuid'] = Variable<String>(localUuid.value);
    }
    if (serverUuid.present) {
      map['server_uuid'] = Variable<String>(serverUuid.value);
    }
    if (localPayloadJson.present) {
      map['local_payload_json'] = Variable<String>(localPayloadJson.value);
    }
    if (serverPayloadJson.present) {
      map['server_payload_json'] = Variable<String>(serverPayloadJson.value);
    }
    if (conflictingFieldsJson.present) {
      map['conflicting_fields_json'] = Variable<String>(
        conflictingFieldsJson.value,
      );
    }
    if (status.present) {
      map['status'] = Variable<String>(status.value);
    }
    if (serverValueRequired.present) {
      map['server_value_required'] = Variable<bool>(serverValueRequired.value);
    }
    if (detectedAt.present) {
      map['detected_at'] = Variable<DateTime>(detectedAt.value);
    }
    if (resolvedAt.present) {
      map['resolved_at'] = Variable<DateTime>(resolvedAt.value);
    }
    if (rowid.present) {
      map['rowid'] = Variable<int>(rowid.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('ConflictRecordsCompanion(')
          ..write('uuid: $uuid, ')
          ..write('ownerUserUuid: $ownerUserUuid, ')
          ..write('resourceType: $resourceType, ')
          ..write('localUuid: $localUuid, ')
          ..write('serverUuid: $serverUuid, ')
          ..write('localPayloadJson: $localPayloadJson, ')
          ..write('serverPayloadJson: $serverPayloadJson, ')
          ..write('conflictingFieldsJson: $conflictingFieldsJson, ')
          ..write('status: $status, ')
          ..write('serverValueRequired: $serverValueRequired, ')
          ..write('detectedAt: $detectedAt, ')
          ..write('resolvedAt: $resolvedAt, ')
          ..write('rowid: $rowid')
          ..write(')'))
        .toString();
  }
}

class $LocalSyncLogsTable extends LocalSyncLogs
    with TableInfo<$LocalSyncLogsTable, LocalSyncLog> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $LocalSyncLogsTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _uuidMeta = const VerificationMeta('uuid');
  @override
  late final GeneratedColumn<String> uuid = GeneratedColumn<String>(
    'uuid',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _ownerUserUuidMeta = const VerificationMeta(
    'ownerUserUuid',
  );
  @override
  late final GeneratedColumn<String> ownerUserUuid = GeneratedColumn<String>(
    'owner_user_uuid',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _startedAtMeta = const VerificationMeta(
    'startedAt',
  );
  @override
  late final GeneratedColumn<DateTime> startedAt = GeneratedColumn<DateTime>(
    'started_at',
    aliasedName,
    false,
    type: DriftSqlType.dateTime,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _completedAtMeta = const VerificationMeta(
    'completedAt',
  );
  @override
  late final GeneratedColumn<DateTime> completedAt = GeneratedColumn<DateTime>(
    'completed_at',
    aliasedName,
    true,
    type: DriftSqlType.dateTime,
    requiredDuringInsert: false,
  );
  static const VerificationMeta _uploadedCountMeta = const VerificationMeta(
    'uploadedCount',
  );
  @override
  late final GeneratedColumn<int> uploadedCount = GeneratedColumn<int>(
    'uploaded_count',
    aliasedName,
    false,
    type: DriftSqlType.int,
    requiredDuringInsert: false,
    defaultValue: const Constant(0),
  );
  static const VerificationMeta _downloadedCountMeta = const VerificationMeta(
    'downloadedCount',
  );
  @override
  late final GeneratedColumn<int> downloadedCount = GeneratedColumn<int>(
    'downloaded_count',
    aliasedName,
    false,
    type: DriftSqlType.int,
    requiredDuringInsert: false,
    defaultValue: const Constant(0),
  );
  static const VerificationMeta _conflictCountMeta = const VerificationMeta(
    'conflictCount',
  );
  @override
  late final GeneratedColumn<int> conflictCount = GeneratedColumn<int>(
    'conflict_count',
    aliasedName,
    false,
    type: DriftSqlType.int,
    requiredDuringInsert: false,
    defaultValue: const Constant(0),
  );
  static const VerificationMeta _failedCountMeta = const VerificationMeta(
    'failedCount',
  );
  @override
  late final GeneratedColumn<int> failedCount = GeneratedColumn<int>(
    'failed_count',
    aliasedName,
    false,
    type: DriftSqlType.int,
    requiredDuringInsert: false,
    defaultValue: const Constant(0),
  );
  static const VerificationMeta _statusMeta = const VerificationMeta('status');
  @override
  late final GeneratedColumn<String> status = GeneratedColumn<String>(
    'status',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _safeErrorMeta = const VerificationMeta(
    'safeError',
  );
  @override
  late final GeneratedColumn<String> safeError = GeneratedColumn<String>(
    'safe_error',
    aliasedName,
    true,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
  );
  @override
  List<GeneratedColumn> get $columns => [
    uuid,
    ownerUserUuid,
    startedAt,
    completedAt,
    uploadedCount,
    downloadedCount,
    conflictCount,
    failedCount,
    status,
    safeError,
  ];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'local_sync_logs';
  @override
  VerificationContext validateIntegrity(
    Insertable<LocalSyncLog> instance, {
    bool isInserting = false,
  }) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('uuid')) {
      context.handle(
        _uuidMeta,
        uuid.isAcceptableOrUnknown(data['uuid']!, _uuidMeta),
      );
    } else if (isInserting) {
      context.missing(_uuidMeta);
    }
    if (data.containsKey('owner_user_uuid')) {
      context.handle(
        _ownerUserUuidMeta,
        ownerUserUuid.isAcceptableOrUnknown(
          data['owner_user_uuid']!,
          _ownerUserUuidMeta,
        ),
      );
    } else if (isInserting) {
      context.missing(_ownerUserUuidMeta);
    }
    if (data.containsKey('started_at')) {
      context.handle(
        _startedAtMeta,
        startedAt.isAcceptableOrUnknown(data['started_at']!, _startedAtMeta),
      );
    } else if (isInserting) {
      context.missing(_startedAtMeta);
    }
    if (data.containsKey('completed_at')) {
      context.handle(
        _completedAtMeta,
        completedAt.isAcceptableOrUnknown(
          data['completed_at']!,
          _completedAtMeta,
        ),
      );
    }
    if (data.containsKey('uploaded_count')) {
      context.handle(
        _uploadedCountMeta,
        uploadedCount.isAcceptableOrUnknown(
          data['uploaded_count']!,
          _uploadedCountMeta,
        ),
      );
    }
    if (data.containsKey('downloaded_count')) {
      context.handle(
        _downloadedCountMeta,
        downloadedCount.isAcceptableOrUnknown(
          data['downloaded_count']!,
          _downloadedCountMeta,
        ),
      );
    }
    if (data.containsKey('conflict_count')) {
      context.handle(
        _conflictCountMeta,
        conflictCount.isAcceptableOrUnknown(
          data['conflict_count']!,
          _conflictCountMeta,
        ),
      );
    }
    if (data.containsKey('failed_count')) {
      context.handle(
        _failedCountMeta,
        failedCount.isAcceptableOrUnknown(
          data['failed_count']!,
          _failedCountMeta,
        ),
      );
    }
    if (data.containsKey('status')) {
      context.handle(
        _statusMeta,
        status.isAcceptableOrUnknown(data['status']!, _statusMeta),
      );
    } else if (isInserting) {
      context.missing(_statusMeta);
    }
    if (data.containsKey('safe_error')) {
      context.handle(
        _safeErrorMeta,
        safeError.isAcceptableOrUnknown(data['safe_error']!, _safeErrorMeta),
      );
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {uuid};
  @override
  LocalSyncLog map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return LocalSyncLog(
      uuid: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}uuid'],
      )!,
      ownerUserUuid: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}owner_user_uuid'],
      )!,
      startedAt: attachedDatabase.typeMapping.read(
        DriftSqlType.dateTime,
        data['${effectivePrefix}started_at'],
      )!,
      completedAt: attachedDatabase.typeMapping.read(
        DriftSqlType.dateTime,
        data['${effectivePrefix}completed_at'],
      ),
      uploadedCount: attachedDatabase.typeMapping.read(
        DriftSqlType.int,
        data['${effectivePrefix}uploaded_count'],
      )!,
      downloadedCount: attachedDatabase.typeMapping.read(
        DriftSqlType.int,
        data['${effectivePrefix}downloaded_count'],
      )!,
      conflictCount: attachedDatabase.typeMapping.read(
        DriftSqlType.int,
        data['${effectivePrefix}conflict_count'],
      )!,
      failedCount: attachedDatabase.typeMapping.read(
        DriftSqlType.int,
        data['${effectivePrefix}failed_count'],
      )!,
      status: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}status'],
      )!,
      safeError: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}safe_error'],
      ),
    );
  }

  @override
  $LocalSyncLogsTable createAlias(String alias) {
    return $LocalSyncLogsTable(attachedDatabase, alias);
  }
}

class LocalSyncLog extends DataClass implements Insertable<LocalSyncLog> {
  final String uuid;
  final String ownerUserUuid;
  final DateTime startedAt;
  final DateTime? completedAt;
  final int uploadedCount;
  final int downloadedCount;
  final int conflictCount;
  final int failedCount;
  final String status;
  final String? safeError;
  const LocalSyncLog({
    required this.uuid,
    required this.ownerUserUuid,
    required this.startedAt,
    this.completedAt,
    required this.uploadedCount,
    required this.downloadedCount,
    required this.conflictCount,
    required this.failedCount,
    required this.status,
    this.safeError,
  });
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['uuid'] = Variable<String>(uuid);
    map['owner_user_uuid'] = Variable<String>(ownerUserUuid);
    map['started_at'] = Variable<DateTime>(startedAt);
    if (!nullToAbsent || completedAt != null) {
      map['completed_at'] = Variable<DateTime>(completedAt);
    }
    map['uploaded_count'] = Variable<int>(uploadedCount);
    map['downloaded_count'] = Variable<int>(downloadedCount);
    map['conflict_count'] = Variable<int>(conflictCount);
    map['failed_count'] = Variable<int>(failedCount);
    map['status'] = Variable<String>(status);
    if (!nullToAbsent || safeError != null) {
      map['safe_error'] = Variable<String>(safeError);
    }
    return map;
  }

  LocalSyncLogsCompanion toCompanion(bool nullToAbsent) {
    return LocalSyncLogsCompanion(
      uuid: Value(uuid),
      ownerUserUuid: Value(ownerUserUuid),
      startedAt: Value(startedAt),
      completedAt: completedAt == null && nullToAbsent
          ? const Value.absent()
          : Value(completedAt),
      uploadedCount: Value(uploadedCount),
      downloadedCount: Value(downloadedCount),
      conflictCount: Value(conflictCount),
      failedCount: Value(failedCount),
      status: Value(status),
      safeError: safeError == null && nullToAbsent
          ? const Value.absent()
          : Value(safeError),
    );
  }

  factory LocalSyncLog.fromJson(
    Map<String, dynamic> json, {
    ValueSerializer? serializer,
  }) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return LocalSyncLog(
      uuid: serializer.fromJson<String>(json['uuid']),
      ownerUserUuid: serializer.fromJson<String>(json['ownerUserUuid']),
      startedAt: serializer.fromJson<DateTime>(json['startedAt']),
      completedAt: serializer.fromJson<DateTime?>(json['completedAt']),
      uploadedCount: serializer.fromJson<int>(json['uploadedCount']),
      downloadedCount: serializer.fromJson<int>(json['downloadedCount']),
      conflictCount: serializer.fromJson<int>(json['conflictCount']),
      failedCount: serializer.fromJson<int>(json['failedCount']),
      status: serializer.fromJson<String>(json['status']),
      safeError: serializer.fromJson<String?>(json['safeError']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'uuid': serializer.toJson<String>(uuid),
      'ownerUserUuid': serializer.toJson<String>(ownerUserUuid),
      'startedAt': serializer.toJson<DateTime>(startedAt),
      'completedAt': serializer.toJson<DateTime?>(completedAt),
      'uploadedCount': serializer.toJson<int>(uploadedCount),
      'downloadedCount': serializer.toJson<int>(downloadedCount),
      'conflictCount': serializer.toJson<int>(conflictCount),
      'failedCount': serializer.toJson<int>(failedCount),
      'status': serializer.toJson<String>(status),
      'safeError': serializer.toJson<String?>(safeError),
    };
  }

  LocalSyncLog copyWith({
    String? uuid,
    String? ownerUserUuid,
    DateTime? startedAt,
    Value<DateTime?> completedAt = const Value.absent(),
    int? uploadedCount,
    int? downloadedCount,
    int? conflictCount,
    int? failedCount,
    String? status,
    Value<String?> safeError = const Value.absent(),
  }) => LocalSyncLog(
    uuid: uuid ?? this.uuid,
    ownerUserUuid: ownerUserUuid ?? this.ownerUserUuid,
    startedAt: startedAt ?? this.startedAt,
    completedAt: completedAt.present ? completedAt.value : this.completedAt,
    uploadedCount: uploadedCount ?? this.uploadedCount,
    downloadedCount: downloadedCount ?? this.downloadedCount,
    conflictCount: conflictCount ?? this.conflictCount,
    failedCount: failedCount ?? this.failedCount,
    status: status ?? this.status,
    safeError: safeError.present ? safeError.value : this.safeError,
  );
  LocalSyncLog copyWithCompanion(LocalSyncLogsCompanion data) {
    return LocalSyncLog(
      uuid: data.uuid.present ? data.uuid.value : this.uuid,
      ownerUserUuid: data.ownerUserUuid.present
          ? data.ownerUserUuid.value
          : this.ownerUserUuid,
      startedAt: data.startedAt.present ? data.startedAt.value : this.startedAt,
      completedAt: data.completedAt.present
          ? data.completedAt.value
          : this.completedAt,
      uploadedCount: data.uploadedCount.present
          ? data.uploadedCount.value
          : this.uploadedCount,
      downloadedCount: data.downloadedCount.present
          ? data.downloadedCount.value
          : this.downloadedCount,
      conflictCount: data.conflictCount.present
          ? data.conflictCount.value
          : this.conflictCount,
      failedCount: data.failedCount.present
          ? data.failedCount.value
          : this.failedCount,
      status: data.status.present ? data.status.value : this.status,
      safeError: data.safeError.present ? data.safeError.value : this.safeError,
    );
  }

  @override
  String toString() {
    return (StringBuffer('LocalSyncLog(')
          ..write('uuid: $uuid, ')
          ..write('ownerUserUuid: $ownerUserUuid, ')
          ..write('startedAt: $startedAt, ')
          ..write('completedAt: $completedAt, ')
          ..write('uploadedCount: $uploadedCount, ')
          ..write('downloadedCount: $downloadedCount, ')
          ..write('conflictCount: $conflictCount, ')
          ..write('failedCount: $failedCount, ')
          ..write('status: $status, ')
          ..write('safeError: $safeError')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(
    uuid,
    ownerUserUuid,
    startedAt,
    completedAt,
    uploadedCount,
    downloadedCount,
    conflictCount,
    failedCount,
    status,
    safeError,
  );
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is LocalSyncLog &&
          other.uuid == this.uuid &&
          other.ownerUserUuid == this.ownerUserUuid &&
          other.startedAt == this.startedAt &&
          other.completedAt == this.completedAt &&
          other.uploadedCount == this.uploadedCount &&
          other.downloadedCount == this.downloadedCount &&
          other.conflictCount == this.conflictCount &&
          other.failedCount == this.failedCount &&
          other.status == this.status &&
          other.safeError == this.safeError);
}

class LocalSyncLogsCompanion extends UpdateCompanion<LocalSyncLog> {
  final Value<String> uuid;
  final Value<String> ownerUserUuid;
  final Value<DateTime> startedAt;
  final Value<DateTime?> completedAt;
  final Value<int> uploadedCount;
  final Value<int> downloadedCount;
  final Value<int> conflictCount;
  final Value<int> failedCount;
  final Value<String> status;
  final Value<String?> safeError;
  final Value<int> rowid;
  const LocalSyncLogsCompanion({
    this.uuid = const Value.absent(),
    this.ownerUserUuid = const Value.absent(),
    this.startedAt = const Value.absent(),
    this.completedAt = const Value.absent(),
    this.uploadedCount = const Value.absent(),
    this.downloadedCount = const Value.absent(),
    this.conflictCount = const Value.absent(),
    this.failedCount = const Value.absent(),
    this.status = const Value.absent(),
    this.safeError = const Value.absent(),
    this.rowid = const Value.absent(),
  });
  LocalSyncLogsCompanion.insert({
    required String uuid,
    required String ownerUserUuid,
    required DateTime startedAt,
    this.completedAt = const Value.absent(),
    this.uploadedCount = const Value.absent(),
    this.downloadedCount = const Value.absent(),
    this.conflictCount = const Value.absent(),
    this.failedCount = const Value.absent(),
    required String status,
    this.safeError = const Value.absent(),
    this.rowid = const Value.absent(),
  }) : uuid = Value(uuid),
       ownerUserUuid = Value(ownerUserUuid),
       startedAt = Value(startedAt),
       status = Value(status);
  static Insertable<LocalSyncLog> custom({
    Expression<String>? uuid,
    Expression<String>? ownerUserUuid,
    Expression<DateTime>? startedAt,
    Expression<DateTime>? completedAt,
    Expression<int>? uploadedCount,
    Expression<int>? downloadedCount,
    Expression<int>? conflictCount,
    Expression<int>? failedCount,
    Expression<String>? status,
    Expression<String>? safeError,
    Expression<int>? rowid,
  }) {
    return RawValuesInsertable({
      if (uuid != null) 'uuid': uuid,
      if (ownerUserUuid != null) 'owner_user_uuid': ownerUserUuid,
      if (startedAt != null) 'started_at': startedAt,
      if (completedAt != null) 'completed_at': completedAt,
      if (uploadedCount != null) 'uploaded_count': uploadedCount,
      if (downloadedCount != null) 'downloaded_count': downloadedCount,
      if (conflictCount != null) 'conflict_count': conflictCount,
      if (failedCount != null) 'failed_count': failedCount,
      if (status != null) 'status': status,
      if (safeError != null) 'safe_error': safeError,
      if (rowid != null) 'rowid': rowid,
    });
  }

  LocalSyncLogsCompanion copyWith({
    Value<String>? uuid,
    Value<String>? ownerUserUuid,
    Value<DateTime>? startedAt,
    Value<DateTime?>? completedAt,
    Value<int>? uploadedCount,
    Value<int>? downloadedCount,
    Value<int>? conflictCount,
    Value<int>? failedCount,
    Value<String>? status,
    Value<String?>? safeError,
    Value<int>? rowid,
  }) {
    return LocalSyncLogsCompanion(
      uuid: uuid ?? this.uuid,
      ownerUserUuid: ownerUserUuid ?? this.ownerUserUuid,
      startedAt: startedAt ?? this.startedAt,
      completedAt: completedAt ?? this.completedAt,
      uploadedCount: uploadedCount ?? this.uploadedCount,
      downloadedCount: downloadedCount ?? this.downloadedCount,
      conflictCount: conflictCount ?? this.conflictCount,
      failedCount: failedCount ?? this.failedCount,
      status: status ?? this.status,
      safeError: safeError ?? this.safeError,
      rowid: rowid ?? this.rowid,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (uuid.present) {
      map['uuid'] = Variable<String>(uuid.value);
    }
    if (ownerUserUuid.present) {
      map['owner_user_uuid'] = Variable<String>(ownerUserUuid.value);
    }
    if (startedAt.present) {
      map['started_at'] = Variable<DateTime>(startedAt.value);
    }
    if (completedAt.present) {
      map['completed_at'] = Variable<DateTime>(completedAt.value);
    }
    if (uploadedCount.present) {
      map['uploaded_count'] = Variable<int>(uploadedCount.value);
    }
    if (downloadedCount.present) {
      map['downloaded_count'] = Variable<int>(downloadedCount.value);
    }
    if (conflictCount.present) {
      map['conflict_count'] = Variable<int>(conflictCount.value);
    }
    if (failedCount.present) {
      map['failed_count'] = Variable<int>(failedCount.value);
    }
    if (status.present) {
      map['status'] = Variable<String>(status.value);
    }
    if (safeError.present) {
      map['safe_error'] = Variable<String>(safeError.value);
    }
    if (rowid.present) {
      map['rowid'] = Variable<int>(rowid.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('LocalSyncLogsCompanion(')
          ..write('uuid: $uuid, ')
          ..write('ownerUserUuid: $ownerUserUuid, ')
          ..write('startedAt: $startedAt, ')
          ..write('completedAt: $completedAt, ')
          ..write('uploadedCount: $uploadedCount, ')
          ..write('downloadedCount: $downloadedCount, ')
          ..write('conflictCount: $conflictCount, ')
          ..write('failedCount: $failedCount, ')
          ..write('status: $status, ')
          ..write('safeError: $safeError, ')
          ..write('rowid: $rowid')
          ..write(')'))
        .toString();
  }
}

abstract class _$AppDatabase extends GeneratedDatabase {
  _$AppDatabase(QueryExecutor e) : super(e);
  $AppDatabaseManager get managers => $AppDatabaseManager(this);
  late final $CachedReferenceItemsTable cachedReferenceItems =
      $CachedReferenceItemsTable(this);
  late final $CachedMasterRecordsTable cachedMasterRecords =
      $CachedMasterRecordsTable(this);
  late final $DraftReportsTable draftReports = $DraftReportsTable(this);
  late final $OperationalRecordsTable operationalRecords =
      $OperationalRecordsTable(this);
  late final $PendingAttachmentsTable pendingAttachments =
      $PendingAttachmentsTable(this);
  late final $SyncMetadataEntriesTable syncMetadataEntries =
      $SyncMetadataEntriesTable(this);
  late final $ConflictRecordsTable conflictRecords = $ConflictRecordsTable(
    this,
  );
  late final $LocalSyncLogsTable localSyncLogs = $LocalSyncLogsTable(this);
  @override
  Iterable<TableInfo<Table, Object?>> get allTables =>
      allSchemaEntities.whereType<TableInfo<Table, Object?>>();
  @override
  List<DatabaseSchemaEntity> get allSchemaEntities => [
    cachedReferenceItems,
    cachedMasterRecords,
    draftReports,
    operationalRecords,
    pendingAttachments,
    syncMetadataEntries,
    conflictRecords,
    localSyncLogs,
  ];
}

typedef $$CachedReferenceItemsTableCreateCompanionBuilder =
    CachedReferenceItemsCompanion Function({
      required String ownerUserUuid,
      required String resourceType,
      required String serverUuid,
      required String payloadJson,
      Value<int> recordVersion,
      Value<DateTime?> serverUpdatedAt,
      required DateTime cachedAt,
      Value<int> rowid,
    });
typedef $$CachedReferenceItemsTableUpdateCompanionBuilder =
    CachedReferenceItemsCompanion Function({
      Value<String> ownerUserUuid,
      Value<String> resourceType,
      Value<String> serverUuid,
      Value<String> payloadJson,
      Value<int> recordVersion,
      Value<DateTime?> serverUpdatedAt,
      Value<DateTime> cachedAt,
      Value<int> rowid,
    });

class $$CachedReferenceItemsTableFilterComposer
    extends Composer<_$AppDatabase, $CachedReferenceItemsTable> {
  $$CachedReferenceItemsTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<String> get ownerUserUuid => $composableBuilder(
    column: $table.ownerUserUuid,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get resourceType => $composableBuilder(
    column: $table.resourceType,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get serverUuid => $composableBuilder(
    column: $table.serverUuid,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get payloadJson => $composableBuilder(
    column: $table.payloadJson,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<int> get recordVersion => $composableBuilder(
    column: $table.recordVersion,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<DateTime> get serverUpdatedAt => $composableBuilder(
    column: $table.serverUpdatedAt,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<DateTime> get cachedAt => $composableBuilder(
    column: $table.cachedAt,
    builder: (column) => ColumnFilters(column),
  );
}

class $$CachedReferenceItemsTableOrderingComposer
    extends Composer<_$AppDatabase, $CachedReferenceItemsTable> {
  $$CachedReferenceItemsTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<String> get ownerUserUuid => $composableBuilder(
    column: $table.ownerUserUuid,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get resourceType => $composableBuilder(
    column: $table.resourceType,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get serverUuid => $composableBuilder(
    column: $table.serverUuid,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get payloadJson => $composableBuilder(
    column: $table.payloadJson,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<int> get recordVersion => $composableBuilder(
    column: $table.recordVersion,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<DateTime> get serverUpdatedAt => $composableBuilder(
    column: $table.serverUpdatedAt,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<DateTime> get cachedAt => $composableBuilder(
    column: $table.cachedAt,
    builder: (column) => ColumnOrderings(column),
  );
}

class $$CachedReferenceItemsTableAnnotationComposer
    extends Composer<_$AppDatabase, $CachedReferenceItemsTable> {
  $$CachedReferenceItemsTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<String> get ownerUserUuid => $composableBuilder(
    column: $table.ownerUserUuid,
    builder: (column) => column,
  );

  GeneratedColumn<String> get resourceType => $composableBuilder(
    column: $table.resourceType,
    builder: (column) => column,
  );

  GeneratedColumn<String> get serverUuid => $composableBuilder(
    column: $table.serverUuid,
    builder: (column) => column,
  );

  GeneratedColumn<String> get payloadJson => $composableBuilder(
    column: $table.payloadJson,
    builder: (column) => column,
  );

  GeneratedColumn<int> get recordVersion => $composableBuilder(
    column: $table.recordVersion,
    builder: (column) => column,
  );

  GeneratedColumn<DateTime> get serverUpdatedAt => $composableBuilder(
    column: $table.serverUpdatedAt,
    builder: (column) => column,
  );

  GeneratedColumn<DateTime> get cachedAt =>
      $composableBuilder(column: $table.cachedAt, builder: (column) => column);
}

class $$CachedReferenceItemsTableTableManager
    extends
        RootTableManager<
          _$AppDatabase,
          $CachedReferenceItemsTable,
          CachedReferenceItem,
          $$CachedReferenceItemsTableFilterComposer,
          $$CachedReferenceItemsTableOrderingComposer,
          $$CachedReferenceItemsTableAnnotationComposer,
          $$CachedReferenceItemsTableCreateCompanionBuilder,
          $$CachedReferenceItemsTableUpdateCompanionBuilder,
          (
            CachedReferenceItem,
            BaseReferences<
              _$AppDatabase,
              $CachedReferenceItemsTable,
              CachedReferenceItem
            >,
          ),
          CachedReferenceItem,
          PrefetchHooks Function()
        > {
  $$CachedReferenceItemsTableTableManager(
    _$AppDatabase db,
    $CachedReferenceItemsTable table,
  ) : super(
        TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$CachedReferenceItemsTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$CachedReferenceItemsTableOrderingComposer(
                $db: db,
                $table: table,
              ),
          createComputedFieldComposer: () =>
              $$CachedReferenceItemsTableAnnotationComposer(
                $db: db,
                $table: table,
              ),
          updateCompanionCallback:
              ({
                Value<String> ownerUserUuid = const Value.absent(),
                Value<String> resourceType = const Value.absent(),
                Value<String> serverUuid = const Value.absent(),
                Value<String> payloadJson = const Value.absent(),
                Value<int> recordVersion = const Value.absent(),
                Value<DateTime?> serverUpdatedAt = const Value.absent(),
                Value<DateTime> cachedAt = const Value.absent(),
                Value<int> rowid = const Value.absent(),
              }) => CachedReferenceItemsCompanion(
                ownerUserUuid: ownerUserUuid,
                resourceType: resourceType,
                serverUuid: serverUuid,
                payloadJson: payloadJson,
                recordVersion: recordVersion,
                serverUpdatedAt: serverUpdatedAt,
                cachedAt: cachedAt,
                rowid: rowid,
              ),
          createCompanionCallback:
              ({
                required String ownerUserUuid,
                required String resourceType,
                required String serverUuid,
                required String payloadJson,
                Value<int> recordVersion = const Value.absent(),
                Value<DateTime?> serverUpdatedAt = const Value.absent(),
                required DateTime cachedAt,
                Value<int> rowid = const Value.absent(),
              }) => CachedReferenceItemsCompanion.insert(
                ownerUserUuid: ownerUserUuid,
                resourceType: resourceType,
                serverUuid: serverUuid,
                payloadJson: payloadJson,
                recordVersion: recordVersion,
                serverUpdatedAt: serverUpdatedAt,
                cachedAt: cachedAt,
                rowid: rowid,
              ),
          withReferenceMapper: (p0) => p0
              .map((e) => (e.readTable(table), BaseReferences(db, table, e)))
              .toList(),
          prefetchHooksCallback: null,
        ),
      );
}

typedef $$CachedReferenceItemsTableProcessedTableManager =
    ProcessedTableManager<
      _$AppDatabase,
      $CachedReferenceItemsTable,
      CachedReferenceItem,
      $$CachedReferenceItemsTableFilterComposer,
      $$CachedReferenceItemsTableOrderingComposer,
      $$CachedReferenceItemsTableAnnotationComposer,
      $$CachedReferenceItemsTableCreateCompanionBuilder,
      $$CachedReferenceItemsTableUpdateCompanionBuilder,
      (
        CachedReferenceItem,
        BaseReferences<
          _$AppDatabase,
          $CachedReferenceItemsTable,
          CachedReferenceItem
        >,
      ),
      CachedReferenceItem,
      PrefetchHooks Function()
    >;
typedef $$CachedMasterRecordsTableCreateCompanionBuilder =
    CachedMasterRecordsCompanion Function({
      required String ownerUserUuid,
      required String resourceType,
      required String serverUuid,
      Value<String?> villageUuid,
      Value<String> confidentialityLevel,
      required String payloadJson,
      required int recordVersion,
      required DateTime serverUpdatedAt,
      required DateTime cachedAt,
      Value<int> rowid,
    });
typedef $$CachedMasterRecordsTableUpdateCompanionBuilder =
    CachedMasterRecordsCompanion Function({
      Value<String> ownerUserUuid,
      Value<String> resourceType,
      Value<String> serverUuid,
      Value<String?> villageUuid,
      Value<String> confidentialityLevel,
      Value<String> payloadJson,
      Value<int> recordVersion,
      Value<DateTime> serverUpdatedAt,
      Value<DateTime> cachedAt,
      Value<int> rowid,
    });

class $$CachedMasterRecordsTableFilterComposer
    extends Composer<_$AppDatabase, $CachedMasterRecordsTable> {
  $$CachedMasterRecordsTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<String> get ownerUserUuid => $composableBuilder(
    column: $table.ownerUserUuid,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get resourceType => $composableBuilder(
    column: $table.resourceType,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get serverUuid => $composableBuilder(
    column: $table.serverUuid,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get villageUuid => $composableBuilder(
    column: $table.villageUuid,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get confidentialityLevel => $composableBuilder(
    column: $table.confidentialityLevel,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get payloadJson => $composableBuilder(
    column: $table.payloadJson,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<int> get recordVersion => $composableBuilder(
    column: $table.recordVersion,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<DateTime> get serverUpdatedAt => $composableBuilder(
    column: $table.serverUpdatedAt,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<DateTime> get cachedAt => $composableBuilder(
    column: $table.cachedAt,
    builder: (column) => ColumnFilters(column),
  );
}

class $$CachedMasterRecordsTableOrderingComposer
    extends Composer<_$AppDatabase, $CachedMasterRecordsTable> {
  $$CachedMasterRecordsTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<String> get ownerUserUuid => $composableBuilder(
    column: $table.ownerUserUuid,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get resourceType => $composableBuilder(
    column: $table.resourceType,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get serverUuid => $composableBuilder(
    column: $table.serverUuid,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get villageUuid => $composableBuilder(
    column: $table.villageUuid,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get confidentialityLevel => $composableBuilder(
    column: $table.confidentialityLevel,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get payloadJson => $composableBuilder(
    column: $table.payloadJson,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<int> get recordVersion => $composableBuilder(
    column: $table.recordVersion,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<DateTime> get serverUpdatedAt => $composableBuilder(
    column: $table.serverUpdatedAt,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<DateTime> get cachedAt => $composableBuilder(
    column: $table.cachedAt,
    builder: (column) => ColumnOrderings(column),
  );
}

class $$CachedMasterRecordsTableAnnotationComposer
    extends Composer<_$AppDatabase, $CachedMasterRecordsTable> {
  $$CachedMasterRecordsTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<String> get ownerUserUuid => $composableBuilder(
    column: $table.ownerUserUuid,
    builder: (column) => column,
  );

  GeneratedColumn<String> get resourceType => $composableBuilder(
    column: $table.resourceType,
    builder: (column) => column,
  );

  GeneratedColumn<String> get serverUuid => $composableBuilder(
    column: $table.serverUuid,
    builder: (column) => column,
  );

  GeneratedColumn<String> get villageUuid => $composableBuilder(
    column: $table.villageUuid,
    builder: (column) => column,
  );

  GeneratedColumn<String> get confidentialityLevel => $composableBuilder(
    column: $table.confidentialityLevel,
    builder: (column) => column,
  );

  GeneratedColumn<String> get payloadJson => $composableBuilder(
    column: $table.payloadJson,
    builder: (column) => column,
  );

  GeneratedColumn<int> get recordVersion => $composableBuilder(
    column: $table.recordVersion,
    builder: (column) => column,
  );

  GeneratedColumn<DateTime> get serverUpdatedAt => $composableBuilder(
    column: $table.serverUpdatedAt,
    builder: (column) => column,
  );

  GeneratedColumn<DateTime> get cachedAt =>
      $composableBuilder(column: $table.cachedAt, builder: (column) => column);
}

class $$CachedMasterRecordsTableTableManager
    extends
        RootTableManager<
          _$AppDatabase,
          $CachedMasterRecordsTable,
          CachedMasterRecord,
          $$CachedMasterRecordsTableFilterComposer,
          $$CachedMasterRecordsTableOrderingComposer,
          $$CachedMasterRecordsTableAnnotationComposer,
          $$CachedMasterRecordsTableCreateCompanionBuilder,
          $$CachedMasterRecordsTableUpdateCompanionBuilder,
          (
            CachedMasterRecord,
            BaseReferences<
              _$AppDatabase,
              $CachedMasterRecordsTable,
              CachedMasterRecord
            >,
          ),
          CachedMasterRecord,
          PrefetchHooks Function()
        > {
  $$CachedMasterRecordsTableTableManager(
    _$AppDatabase db,
    $CachedMasterRecordsTable table,
  ) : super(
        TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$CachedMasterRecordsTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$CachedMasterRecordsTableOrderingComposer(
                $db: db,
                $table: table,
              ),
          createComputedFieldComposer: () =>
              $$CachedMasterRecordsTableAnnotationComposer(
                $db: db,
                $table: table,
              ),
          updateCompanionCallback:
              ({
                Value<String> ownerUserUuid = const Value.absent(),
                Value<String> resourceType = const Value.absent(),
                Value<String> serverUuid = const Value.absent(),
                Value<String?> villageUuid = const Value.absent(),
                Value<String> confidentialityLevel = const Value.absent(),
                Value<String> payloadJson = const Value.absent(),
                Value<int> recordVersion = const Value.absent(),
                Value<DateTime> serverUpdatedAt = const Value.absent(),
                Value<DateTime> cachedAt = const Value.absent(),
                Value<int> rowid = const Value.absent(),
              }) => CachedMasterRecordsCompanion(
                ownerUserUuid: ownerUserUuid,
                resourceType: resourceType,
                serverUuid: serverUuid,
                villageUuid: villageUuid,
                confidentialityLevel: confidentialityLevel,
                payloadJson: payloadJson,
                recordVersion: recordVersion,
                serverUpdatedAt: serverUpdatedAt,
                cachedAt: cachedAt,
                rowid: rowid,
              ),
          createCompanionCallback:
              ({
                required String ownerUserUuid,
                required String resourceType,
                required String serverUuid,
                Value<String?> villageUuid = const Value.absent(),
                Value<String> confidentialityLevel = const Value.absent(),
                required String payloadJson,
                required int recordVersion,
                required DateTime serverUpdatedAt,
                required DateTime cachedAt,
                Value<int> rowid = const Value.absent(),
              }) => CachedMasterRecordsCompanion.insert(
                ownerUserUuid: ownerUserUuid,
                resourceType: resourceType,
                serverUuid: serverUuid,
                villageUuid: villageUuid,
                confidentialityLevel: confidentialityLevel,
                payloadJson: payloadJson,
                recordVersion: recordVersion,
                serverUpdatedAt: serverUpdatedAt,
                cachedAt: cachedAt,
                rowid: rowid,
              ),
          withReferenceMapper: (p0) => p0
              .map((e) => (e.readTable(table), BaseReferences(db, table, e)))
              .toList(),
          prefetchHooksCallback: null,
        ),
      );
}

typedef $$CachedMasterRecordsTableProcessedTableManager =
    ProcessedTableManager<
      _$AppDatabase,
      $CachedMasterRecordsTable,
      CachedMasterRecord,
      $$CachedMasterRecordsTableFilterComposer,
      $$CachedMasterRecordsTableOrderingComposer,
      $$CachedMasterRecordsTableAnnotationComposer,
      $$CachedMasterRecordsTableCreateCompanionBuilder,
      $$CachedMasterRecordsTableUpdateCompanionBuilder,
      (
        CachedMasterRecord,
        BaseReferences<
          _$AppDatabase,
          $CachedMasterRecordsTable,
          CachedMasterRecord
        >,
      ),
      CachedMasterRecord,
      PrefetchHooks Function()
    >;
typedef $$DraftReportsTableCreateCompanionBuilder =
    DraftReportsCompanion Function({
      required String localUuid,
      required String ownerUserUuid,
      Value<String?> serverUuid,
      required String villageUuid,
      required String reportingPeriodUuid,
      required String payloadJson,
      Value<int> recordVersion,
      required String syncStatus,
      required DateTime createdAt,
      required DateTime updatedAt,
      Value<DateTime?> lastSyncedAt,
      Value<DateTime?> serverUpdatedAt,
      Value<bool> deletedLocally,
      Value<String?> conflictStatus,
      Value<String?> syncError,
      Value<int> rowid,
    });
typedef $$DraftReportsTableUpdateCompanionBuilder =
    DraftReportsCompanion Function({
      Value<String> localUuid,
      Value<String> ownerUserUuid,
      Value<String?> serverUuid,
      Value<String> villageUuid,
      Value<String> reportingPeriodUuid,
      Value<String> payloadJson,
      Value<int> recordVersion,
      Value<String> syncStatus,
      Value<DateTime> createdAt,
      Value<DateTime> updatedAt,
      Value<DateTime?> lastSyncedAt,
      Value<DateTime?> serverUpdatedAt,
      Value<bool> deletedLocally,
      Value<String?> conflictStatus,
      Value<String?> syncError,
      Value<int> rowid,
    });

final class $$DraftReportsTableReferences
    extends BaseReferences<_$AppDatabase, $DraftReportsTable, DraftReport> {
  $$DraftReportsTableReferences(super.$_db, super.$_table, super.$_typedResult);

  static MultiTypedResultKey<$OperationalRecordsTable, List<OperationalRecord>>
  _operationalRecordsRefsTable(_$AppDatabase db) =>
      MultiTypedResultKey.fromTable(
        db.operationalRecords,
        aliasName:
            'draft_reports__local_uuid__operational_records__report_local_uuid',
      );

  $$OperationalRecordsTableProcessedTableManager get operationalRecordsRefs {
    final manager =
        $$OperationalRecordsTableTableManager(
          $_db,
          $_db.operationalRecords,
        ).filter(
          (f) => f.reportLocalUuid.localUuid.sqlEquals(
            $_itemColumn<String>('local_uuid')!,
          ),
        );

    final cache = $_typedResult.readTableOrNull(
      _operationalRecordsRefsTable($_db),
    );
    return ProcessedTableManager(
      manager.$state.copyWith(prefetchedData: cache),
    );
  }

  static MultiTypedResultKey<$PendingAttachmentsTable, List<PendingAttachment>>
  _pendingAttachmentsRefsTable(_$AppDatabase db) =>
      MultiTypedResultKey.fromTable(
        db.pendingAttachments,
        aliasName:
            'draft_reports__local_uuid__pending_attachments__report_local_uuid',
      );

  $$PendingAttachmentsTableProcessedTableManager get pendingAttachmentsRefs {
    final manager =
        $$PendingAttachmentsTableTableManager(
          $_db,
          $_db.pendingAttachments,
        ).filter(
          (f) => f.reportLocalUuid.localUuid.sqlEquals(
            $_itemColumn<String>('local_uuid')!,
          ),
        );

    final cache = $_typedResult.readTableOrNull(
      _pendingAttachmentsRefsTable($_db),
    );
    return ProcessedTableManager(
      manager.$state.copyWith(prefetchedData: cache),
    );
  }
}

class $$DraftReportsTableFilterComposer
    extends Composer<_$AppDatabase, $DraftReportsTable> {
  $$DraftReportsTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<String> get localUuid => $composableBuilder(
    column: $table.localUuid,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get ownerUserUuid => $composableBuilder(
    column: $table.ownerUserUuid,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get serverUuid => $composableBuilder(
    column: $table.serverUuid,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get villageUuid => $composableBuilder(
    column: $table.villageUuid,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get reportingPeriodUuid => $composableBuilder(
    column: $table.reportingPeriodUuid,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get payloadJson => $composableBuilder(
    column: $table.payloadJson,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<int> get recordVersion => $composableBuilder(
    column: $table.recordVersion,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get syncStatus => $composableBuilder(
    column: $table.syncStatus,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<DateTime> get createdAt => $composableBuilder(
    column: $table.createdAt,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<DateTime> get updatedAt => $composableBuilder(
    column: $table.updatedAt,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<DateTime> get lastSyncedAt => $composableBuilder(
    column: $table.lastSyncedAt,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<DateTime> get serverUpdatedAt => $composableBuilder(
    column: $table.serverUpdatedAt,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<bool> get deletedLocally => $composableBuilder(
    column: $table.deletedLocally,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get conflictStatus => $composableBuilder(
    column: $table.conflictStatus,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get syncError => $composableBuilder(
    column: $table.syncError,
    builder: (column) => ColumnFilters(column),
  );

  Expression<bool> operationalRecordsRefs(
    Expression<bool> Function($$OperationalRecordsTableFilterComposer f) f,
  ) {
    final $$OperationalRecordsTableFilterComposer composer = $composerBuilder(
      composer: this,
      getCurrentColumn: (t) => t.localUuid,
      referencedTable: $db.operationalRecords,
      getReferencedColumn: (t) => t.reportLocalUuid,
      builder:
          (
            joinBuilder, {
            $addJoinBuilderToRootComposer,
            $removeJoinBuilderFromRootComposer,
          }) => $$OperationalRecordsTableFilterComposer(
            $db: $db,
            $table: $db.operationalRecords,
            $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
            joinBuilder: joinBuilder,
            $removeJoinBuilderFromRootComposer:
                $removeJoinBuilderFromRootComposer,
          ),
    );
    return f(composer);
  }

  Expression<bool> pendingAttachmentsRefs(
    Expression<bool> Function($$PendingAttachmentsTableFilterComposer f) f,
  ) {
    final $$PendingAttachmentsTableFilterComposer composer = $composerBuilder(
      composer: this,
      getCurrentColumn: (t) => t.localUuid,
      referencedTable: $db.pendingAttachments,
      getReferencedColumn: (t) => t.reportLocalUuid,
      builder:
          (
            joinBuilder, {
            $addJoinBuilderToRootComposer,
            $removeJoinBuilderFromRootComposer,
          }) => $$PendingAttachmentsTableFilterComposer(
            $db: $db,
            $table: $db.pendingAttachments,
            $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
            joinBuilder: joinBuilder,
            $removeJoinBuilderFromRootComposer:
                $removeJoinBuilderFromRootComposer,
          ),
    );
    return f(composer);
  }
}

class $$DraftReportsTableOrderingComposer
    extends Composer<_$AppDatabase, $DraftReportsTable> {
  $$DraftReportsTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<String> get localUuid => $composableBuilder(
    column: $table.localUuid,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get ownerUserUuid => $composableBuilder(
    column: $table.ownerUserUuid,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get serverUuid => $composableBuilder(
    column: $table.serverUuid,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get villageUuid => $composableBuilder(
    column: $table.villageUuid,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get reportingPeriodUuid => $composableBuilder(
    column: $table.reportingPeriodUuid,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get payloadJson => $composableBuilder(
    column: $table.payloadJson,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<int> get recordVersion => $composableBuilder(
    column: $table.recordVersion,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get syncStatus => $composableBuilder(
    column: $table.syncStatus,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<DateTime> get createdAt => $composableBuilder(
    column: $table.createdAt,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<DateTime> get updatedAt => $composableBuilder(
    column: $table.updatedAt,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<DateTime> get lastSyncedAt => $composableBuilder(
    column: $table.lastSyncedAt,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<DateTime> get serverUpdatedAt => $composableBuilder(
    column: $table.serverUpdatedAt,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<bool> get deletedLocally => $composableBuilder(
    column: $table.deletedLocally,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get conflictStatus => $composableBuilder(
    column: $table.conflictStatus,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get syncError => $composableBuilder(
    column: $table.syncError,
    builder: (column) => ColumnOrderings(column),
  );
}

class $$DraftReportsTableAnnotationComposer
    extends Composer<_$AppDatabase, $DraftReportsTable> {
  $$DraftReportsTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<String> get localUuid =>
      $composableBuilder(column: $table.localUuid, builder: (column) => column);

  GeneratedColumn<String> get ownerUserUuid => $composableBuilder(
    column: $table.ownerUserUuid,
    builder: (column) => column,
  );

  GeneratedColumn<String> get serverUuid => $composableBuilder(
    column: $table.serverUuid,
    builder: (column) => column,
  );

  GeneratedColumn<String> get villageUuid => $composableBuilder(
    column: $table.villageUuid,
    builder: (column) => column,
  );

  GeneratedColumn<String> get reportingPeriodUuid => $composableBuilder(
    column: $table.reportingPeriodUuid,
    builder: (column) => column,
  );

  GeneratedColumn<String> get payloadJson => $composableBuilder(
    column: $table.payloadJson,
    builder: (column) => column,
  );

  GeneratedColumn<int> get recordVersion => $composableBuilder(
    column: $table.recordVersion,
    builder: (column) => column,
  );

  GeneratedColumn<String> get syncStatus => $composableBuilder(
    column: $table.syncStatus,
    builder: (column) => column,
  );

  GeneratedColumn<DateTime> get createdAt =>
      $composableBuilder(column: $table.createdAt, builder: (column) => column);

  GeneratedColumn<DateTime> get updatedAt =>
      $composableBuilder(column: $table.updatedAt, builder: (column) => column);

  GeneratedColumn<DateTime> get lastSyncedAt => $composableBuilder(
    column: $table.lastSyncedAt,
    builder: (column) => column,
  );

  GeneratedColumn<DateTime> get serverUpdatedAt => $composableBuilder(
    column: $table.serverUpdatedAt,
    builder: (column) => column,
  );

  GeneratedColumn<bool> get deletedLocally => $composableBuilder(
    column: $table.deletedLocally,
    builder: (column) => column,
  );

  GeneratedColumn<String> get conflictStatus => $composableBuilder(
    column: $table.conflictStatus,
    builder: (column) => column,
  );

  GeneratedColumn<String> get syncError =>
      $composableBuilder(column: $table.syncError, builder: (column) => column);

  Expression<T> operationalRecordsRefs<T extends Object>(
    Expression<T> Function($$OperationalRecordsTableAnnotationComposer a) f,
  ) {
    final $$OperationalRecordsTableAnnotationComposer composer =
        $composerBuilder(
          composer: this,
          getCurrentColumn: (t) => t.localUuid,
          referencedTable: $db.operationalRecords,
          getReferencedColumn: (t) => t.reportLocalUuid,
          builder:
              (
                joinBuilder, {
                $addJoinBuilderToRootComposer,
                $removeJoinBuilderFromRootComposer,
              }) => $$OperationalRecordsTableAnnotationComposer(
                $db: $db,
                $table: $db.operationalRecords,
                $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
                joinBuilder: joinBuilder,
                $removeJoinBuilderFromRootComposer:
                    $removeJoinBuilderFromRootComposer,
              ),
        );
    return f(composer);
  }

  Expression<T> pendingAttachmentsRefs<T extends Object>(
    Expression<T> Function($$PendingAttachmentsTableAnnotationComposer a) f,
  ) {
    final $$PendingAttachmentsTableAnnotationComposer composer =
        $composerBuilder(
          composer: this,
          getCurrentColumn: (t) => t.localUuid,
          referencedTable: $db.pendingAttachments,
          getReferencedColumn: (t) => t.reportLocalUuid,
          builder:
              (
                joinBuilder, {
                $addJoinBuilderToRootComposer,
                $removeJoinBuilderFromRootComposer,
              }) => $$PendingAttachmentsTableAnnotationComposer(
                $db: $db,
                $table: $db.pendingAttachments,
                $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
                joinBuilder: joinBuilder,
                $removeJoinBuilderFromRootComposer:
                    $removeJoinBuilderFromRootComposer,
              ),
        );
    return f(composer);
  }
}

class $$DraftReportsTableTableManager
    extends
        RootTableManager<
          _$AppDatabase,
          $DraftReportsTable,
          DraftReport,
          $$DraftReportsTableFilterComposer,
          $$DraftReportsTableOrderingComposer,
          $$DraftReportsTableAnnotationComposer,
          $$DraftReportsTableCreateCompanionBuilder,
          $$DraftReportsTableUpdateCompanionBuilder,
          (DraftReport, $$DraftReportsTableReferences),
          DraftReport,
          PrefetchHooks Function({
            bool operationalRecordsRefs,
            bool pendingAttachmentsRefs,
          })
        > {
  $$DraftReportsTableTableManager(_$AppDatabase db, $DraftReportsTable table)
    : super(
        TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$DraftReportsTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$DraftReportsTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$DraftReportsTableAnnotationComposer($db: db, $table: table),
          updateCompanionCallback:
              ({
                Value<String> localUuid = const Value.absent(),
                Value<String> ownerUserUuid = const Value.absent(),
                Value<String?> serverUuid = const Value.absent(),
                Value<String> villageUuid = const Value.absent(),
                Value<String> reportingPeriodUuid = const Value.absent(),
                Value<String> payloadJson = const Value.absent(),
                Value<int> recordVersion = const Value.absent(),
                Value<String> syncStatus = const Value.absent(),
                Value<DateTime> createdAt = const Value.absent(),
                Value<DateTime> updatedAt = const Value.absent(),
                Value<DateTime?> lastSyncedAt = const Value.absent(),
                Value<DateTime?> serverUpdatedAt = const Value.absent(),
                Value<bool> deletedLocally = const Value.absent(),
                Value<String?> conflictStatus = const Value.absent(),
                Value<String?> syncError = const Value.absent(),
                Value<int> rowid = const Value.absent(),
              }) => DraftReportsCompanion(
                localUuid: localUuid,
                ownerUserUuid: ownerUserUuid,
                serverUuid: serverUuid,
                villageUuid: villageUuid,
                reportingPeriodUuid: reportingPeriodUuid,
                payloadJson: payloadJson,
                recordVersion: recordVersion,
                syncStatus: syncStatus,
                createdAt: createdAt,
                updatedAt: updatedAt,
                lastSyncedAt: lastSyncedAt,
                serverUpdatedAt: serverUpdatedAt,
                deletedLocally: deletedLocally,
                conflictStatus: conflictStatus,
                syncError: syncError,
                rowid: rowid,
              ),
          createCompanionCallback:
              ({
                required String localUuid,
                required String ownerUserUuid,
                Value<String?> serverUuid = const Value.absent(),
                required String villageUuid,
                required String reportingPeriodUuid,
                required String payloadJson,
                Value<int> recordVersion = const Value.absent(),
                required String syncStatus,
                required DateTime createdAt,
                required DateTime updatedAt,
                Value<DateTime?> lastSyncedAt = const Value.absent(),
                Value<DateTime?> serverUpdatedAt = const Value.absent(),
                Value<bool> deletedLocally = const Value.absent(),
                Value<String?> conflictStatus = const Value.absent(),
                Value<String?> syncError = const Value.absent(),
                Value<int> rowid = const Value.absent(),
              }) => DraftReportsCompanion.insert(
                localUuid: localUuid,
                ownerUserUuid: ownerUserUuid,
                serverUuid: serverUuid,
                villageUuid: villageUuid,
                reportingPeriodUuid: reportingPeriodUuid,
                payloadJson: payloadJson,
                recordVersion: recordVersion,
                syncStatus: syncStatus,
                createdAt: createdAt,
                updatedAt: updatedAt,
                lastSyncedAt: lastSyncedAt,
                serverUpdatedAt: serverUpdatedAt,
                deletedLocally: deletedLocally,
                conflictStatus: conflictStatus,
                syncError: syncError,
                rowid: rowid,
              ),
          withReferenceMapper: (p0) => p0
              .map(
                (e) => (
                  e.readTable(table),
                  $$DraftReportsTableReferences(db, table, e),
                ),
              )
              .toList(),
          prefetchHooksCallback:
              ({
                operationalRecordsRefs = false,
                pendingAttachmentsRefs = false,
              }) {
                return PrefetchHooks(
                  db: db,
                  explicitlyWatchedTables: [
                    if (operationalRecordsRefs) db.operationalRecords,
                    if (pendingAttachmentsRefs) db.pendingAttachments,
                  ],
                  addJoins: null,
                  getPrefetchedDataCallback: (items) async {
                    return [
                      if (operationalRecordsRefs)
                        await $_getPrefetchedData<
                          DraftReport,
                          $DraftReportsTable,
                          OperationalRecord
                        >(
                          currentTable: table,
                          referencedTable: $$DraftReportsTableReferences
                              ._operationalRecordsRefsTable(db),
                          managerFromTypedResult: (p0) =>
                              $$DraftReportsTableReferences(
                                db,
                                table,
                                p0,
                              ).operationalRecordsRefs,
                          referencedItemsForCurrentItem:
                              (item, referencedItems) => referencedItems.where(
                                (e) => e.reportLocalUuid == item.localUuid,
                              ),
                          typedResults: items,
                        ),
                      if (pendingAttachmentsRefs)
                        await $_getPrefetchedData<
                          DraftReport,
                          $DraftReportsTable,
                          PendingAttachment
                        >(
                          currentTable: table,
                          referencedTable: $$DraftReportsTableReferences
                              ._pendingAttachmentsRefsTable(db),
                          managerFromTypedResult: (p0) =>
                              $$DraftReportsTableReferences(
                                db,
                                table,
                                p0,
                              ).pendingAttachmentsRefs,
                          referencedItemsForCurrentItem:
                              (item, referencedItems) => referencedItems.where(
                                (e) => e.reportLocalUuid == item.localUuid,
                              ),
                          typedResults: items,
                        ),
                    ];
                  },
                );
              },
        ),
      );
}

typedef $$DraftReportsTableProcessedTableManager =
    ProcessedTableManager<
      _$AppDatabase,
      $DraftReportsTable,
      DraftReport,
      $$DraftReportsTableFilterComposer,
      $$DraftReportsTableOrderingComposer,
      $$DraftReportsTableAnnotationComposer,
      $$DraftReportsTableCreateCompanionBuilder,
      $$DraftReportsTableUpdateCompanionBuilder,
      (DraftReport, $$DraftReportsTableReferences),
      DraftReport,
      PrefetchHooks Function({
        bool operationalRecordsRefs,
        bool pendingAttachmentsRefs,
      })
    >;
typedef $$OperationalRecordsTableCreateCompanionBuilder =
    OperationalRecordsCompanion Function({
      required String localUuid,
      required String ownerUserUuid,
      Value<String?> serverUuid,
      required String resourceType,
      required String reportLocalUuid,
      required String payloadJson,
      Value<int> recordVersion,
      required String syncStatus,
      required DateTime createdAt,
      required DateTime updatedAt,
      Value<DateTime?> lastSyncedAt,
      Value<DateTime?> serverUpdatedAt,
      Value<bool> deletedLocally,
      Value<String?> conflictStatus,
      Value<String?> syncError,
      Value<String?> idempotencyKey,
      Value<int> rowid,
    });
typedef $$OperationalRecordsTableUpdateCompanionBuilder =
    OperationalRecordsCompanion Function({
      Value<String> localUuid,
      Value<String> ownerUserUuid,
      Value<String?> serverUuid,
      Value<String> resourceType,
      Value<String> reportLocalUuid,
      Value<String> payloadJson,
      Value<int> recordVersion,
      Value<String> syncStatus,
      Value<DateTime> createdAt,
      Value<DateTime> updatedAt,
      Value<DateTime?> lastSyncedAt,
      Value<DateTime?> serverUpdatedAt,
      Value<bool> deletedLocally,
      Value<String?> conflictStatus,
      Value<String?> syncError,
      Value<String?> idempotencyKey,
      Value<int> rowid,
    });

final class $$OperationalRecordsTableReferences
    extends
        BaseReferences<
          _$AppDatabase,
          $OperationalRecordsTable,
          OperationalRecord
        > {
  $$OperationalRecordsTableReferences(
    super.$_db,
    super.$_table,
    super.$_typedResult,
  );

  static $DraftReportsTable _reportLocalUuidTable(_$AppDatabase db) =>
      db.draftReports.createAlias(
        'operational_records__report_local_uuid__draft_reports__local_uuid',
      );

  $$DraftReportsTableProcessedTableManager get reportLocalUuid {
    final $_column = $_itemColumn<String>('report_local_uuid')!;

    final manager = $$DraftReportsTableTableManager(
      $_db,
      $_db.draftReports,
    ).filter((f) => f.localUuid.sqlEquals($_column));
    final item = $_typedResult.readTableOrNull(_reportLocalUuidTable($_db));
    if (item == null) return manager;
    return ProcessedTableManager(
      manager.$state.copyWith(prefetchedData: [item]),
    );
  }
}

class $$OperationalRecordsTableFilterComposer
    extends Composer<_$AppDatabase, $OperationalRecordsTable> {
  $$OperationalRecordsTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<String> get localUuid => $composableBuilder(
    column: $table.localUuid,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get ownerUserUuid => $composableBuilder(
    column: $table.ownerUserUuid,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get serverUuid => $composableBuilder(
    column: $table.serverUuid,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get resourceType => $composableBuilder(
    column: $table.resourceType,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get payloadJson => $composableBuilder(
    column: $table.payloadJson,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<int> get recordVersion => $composableBuilder(
    column: $table.recordVersion,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get syncStatus => $composableBuilder(
    column: $table.syncStatus,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<DateTime> get createdAt => $composableBuilder(
    column: $table.createdAt,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<DateTime> get updatedAt => $composableBuilder(
    column: $table.updatedAt,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<DateTime> get lastSyncedAt => $composableBuilder(
    column: $table.lastSyncedAt,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<DateTime> get serverUpdatedAt => $composableBuilder(
    column: $table.serverUpdatedAt,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<bool> get deletedLocally => $composableBuilder(
    column: $table.deletedLocally,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get conflictStatus => $composableBuilder(
    column: $table.conflictStatus,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get syncError => $composableBuilder(
    column: $table.syncError,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get idempotencyKey => $composableBuilder(
    column: $table.idempotencyKey,
    builder: (column) => ColumnFilters(column),
  );

  $$DraftReportsTableFilterComposer get reportLocalUuid {
    final $$DraftReportsTableFilterComposer composer = $composerBuilder(
      composer: this,
      getCurrentColumn: (t) => t.reportLocalUuid,
      referencedTable: $db.draftReports,
      getReferencedColumn: (t) => t.localUuid,
      builder:
          (
            joinBuilder, {
            $addJoinBuilderToRootComposer,
            $removeJoinBuilderFromRootComposer,
          }) => $$DraftReportsTableFilterComposer(
            $db: $db,
            $table: $db.draftReports,
            $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
            joinBuilder: joinBuilder,
            $removeJoinBuilderFromRootComposer:
                $removeJoinBuilderFromRootComposer,
          ),
    );
    return composer;
  }
}

class $$OperationalRecordsTableOrderingComposer
    extends Composer<_$AppDatabase, $OperationalRecordsTable> {
  $$OperationalRecordsTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<String> get localUuid => $composableBuilder(
    column: $table.localUuid,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get ownerUserUuid => $composableBuilder(
    column: $table.ownerUserUuid,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get serverUuid => $composableBuilder(
    column: $table.serverUuid,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get resourceType => $composableBuilder(
    column: $table.resourceType,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get payloadJson => $composableBuilder(
    column: $table.payloadJson,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<int> get recordVersion => $composableBuilder(
    column: $table.recordVersion,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get syncStatus => $composableBuilder(
    column: $table.syncStatus,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<DateTime> get createdAt => $composableBuilder(
    column: $table.createdAt,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<DateTime> get updatedAt => $composableBuilder(
    column: $table.updatedAt,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<DateTime> get lastSyncedAt => $composableBuilder(
    column: $table.lastSyncedAt,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<DateTime> get serverUpdatedAt => $composableBuilder(
    column: $table.serverUpdatedAt,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<bool> get deletedLocally => $composableBuilder(
    column: $table.deletedLocally,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get conflictStatus => $composableBuilder(
    column: $table.conflictStatus,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get syncError => $composableBuilder(
    column: $table.syncError,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get idempotencyKey => $composableBuilder(
    column: $table.idempotencyKey,
    builder: (column) => ColumnOrderings(column),
  );

  $$DraftReportsTableOrderingComposer get reportLocalUuid {
    final $$DraftReportsTableOrderingComposer composer = $composerBuilder(
      composer: this,
      getCurrentColumn: (t) => t.reportLocalUuid,
      referencedTable: $db.draftReports,
      getReferencedColumn: (t) => t.localUuid,
      builder:
          (
            joinBuilder, {
            $addJoinBuilderToRootComposer,
            $removeJoinBuilderFromRootComposer,
          }) => $$DraftReportsTableOrderingComposer(
            $db: $db,
            $table: $db.draftReports,
            $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
            joinBuilder: joinBuilder,
            $removeJoinBuilderFromRootComposer:
                $removeJoinBuilderFromRootComposer,
          ),
    );
    return composer;
  }
}

class $$OperationalRecordsTableAnnotationComposer
    extends Composer<_$AppDatabase, $OperationalRecordsTable> {
  $$OperationalRecordsTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<String> get localUuid =>
      $composableBuilder(column: $table.localUuid, builder: (column) => column);

  GeneratedColumn<String> get ownerUserUuid => $composableBuilder(
    column: $table.ownerUserUuid,
    builder: (column) => column,
  );

  GeneratedColumn<String> get serverUuid => $composableBuilder(
    column: $table.serverUuid,
    builder: (column) => column,
  );

  GeneratedColumn<String> get resourceType => $composableBuilder(
    column: $table.resourceType,
    builder: (column) => column,
  );

  GeneratedColumn<String> get payloadJson => $composableBuilder(
    column: $table.payloadJson,
    builder: (column) => column,
  );

  GeneratedColumn<int> get recordVersion => $composableBuilder(
    column: $table.recordVersion,
    builder: (column) => column,
  );

  GeneratedColumn<String> get syncStatus => $composableBuilder(
    column: $table.syncStatus,
    builder: (column) => column,
  );

  GeneratedColumn<DateTime> get createdAt =>
      $composableBuilder(column: $table.createdAt, builder: (column) => column);

  GeneratedColumn<DateTime> get updatedAt =>
      $composableBuilder(column: $table.updatedAt, builder: (column) => column);

  GeneratedColumn<DateTime> get lastSyncedAt => $composableBuilder(
    column: $table.lastSyncedAt,
    builder: (column) => column,
  );

  GeneratedColumn<DateTime> get serverUpdatedAt => $composableBuilder(
    column: $table.serverUpdatedAt,
    builder: (column) => column,
  );

  GeneratedColumn<bool> get deletedLocally => $composableBuilder(
    column: $table.deletedLocally,
    builder: (column) => column,
  );

  GeneratedColumn<String> get conflictStatus => $composableBuilder(
    column: $table.conflictStatus,
    builder: (column) => column,
  );

  GeneratedColumn<String> get syncError =>
      $composableBuilder(column: $table.syncError, builder: (column) => column);

  GeneratedColumn<String> get idempotencyKey => $composableBuilder(
    column: $table.idempotencyKey,
    builder: (column) => column,
  );

  $$DraftReportsTableAnnotationComposer get reportLocalUuid {
    final $$DraftReportsTableAnnotationComposer composer = $composerBuilder(
      composer: this,
      getCurrentColumn: (t) => t.reportLocalUuid,
      referencedTable: $db.draftReports,
      getReferencedColumn: (t) => t.localUuid,
      builder:
          (
            joinBuilder, {
            $addJoinBuilderToRootComposer,
            $removeJoinBuilderFromRootComposer,
          }) => $$DraftReportsTableAnnotationComposer(
            $db: $db,
            $table: $db.draftReports,
            $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
            joinBuilder: joinBuilder,
            $removeJoinBuilderFromRootComposer:
                $removeJoinBuilderFromRootComposer,
          ),
    );
    return composer;
  }
}

class $$OperationalRecordsTableTableManager
    extends
        RootTableManager<
          _$AppDatabase,
          $OperationalRecordsTable,
          OperationalRecord,
          $$OperationalRecordsTableFilterComposer,
          $$OperationalRecordsTableOrderingComposer,
          $$OperationalRecordsTableAnnotationComposer,
          $$OperationalRecordsTableCreateCompanionBuilder,
          $$OperationalRecordsTableUpdateCompanionBuilder,
          (OperationalRecord, $$OperationalRecordsTableReferences),
          OperationalRecord,
          PrefetchHooks Function({bool reportLocalUuid})
        > {
  $$OperationalRecordsTableTableManager(
    _$AppDatabase db,
    $OperationalRecordsTable table,
  ) : super(
        TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$OperationalRecordsTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$OperationalRecordsTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$OperationalRecordsTableAnnotationComposer(
                $db: db,
                $table: table,
              ),
          updateCompanionCallback:
              ({
                Value<String> localUuid = const Value.absent(),
                Value<String> ownerUserUuid = const Value.absent(),
                Value<String?> serverUuid = const Value.absent(),
                Value<String> resourceType = const Value.absent(),
                Value<String> reportLocalUuid = const Value.absent(),
                Value<String> payloadJson = const Value.absent(),
                Value<int> recordVersion = const Value.absent(),
                Value<String> syncStatus = const Value.absent(),
                Value<DateTime> createdAt = const Value.absent(),
                Value<DateTime> updatedAt = const Value.absent(),
                Value<DateTime?> lastSyncedAt = const Value.absent(),
                Value<DateTime?> serverUpdatedAt = const Value.absent(),
                Value<bool> deletedLocally = const Value.absent(),
                Value<String?> conflictStatus = const Value.absent(),
                Value<String?> syncError = const Value.absent(),
                Value<String?> idempotencyKey = const Value.absent(),
                Value<int> rowid = const Value.absent(),
              }) => OperationalRecordsCompanion(
                localUuid: localUuid,
                ownerUserUuid: ownerUserUuid,
                serverUuid: serverUuid,
                resourceType: resourceType,
                reportLocalUuid: reportLocalUuid,
                payloadJson: payloadJson,
                recordVersion: recordVersion,
                syncStatus: syncStatus,
                createdAt: createdAt,
                updatedAt: updatedAt,
                lastSyncedAt: lastSyncedAt,
                serverUpdatedAt: serverUpdatedAt,
                deletedLocally: deletedLocally,
                conflictStatus: conflictStatus,
                syncError: syncError,
                idempotencyKey: idempotencyKey,
                rowid: rowid,
              ),
          createCompanionCallback:
              ({
                required String localUuid,
                required String ownerUserUuid,
                Value<String?> serverUuid = const Value.absent(),
                required String resourceType,
                required String reportLocalUuid,
                required String payloadJson,
                Value<int> recordVersion = const Value.absent(),
                required String syncStatus,
                required DateTime createdAt,
                required DateTime updatedAt,
                Value<DateTime?> lastSyncedAt = const Value.absent(),
                Value<DateTime?> serverUpdatedAt = const Value.absent(),
                Value<bool> deletedLocally = const Value.absent(),
                Value<String?> conflictStatus = const Value.absent(),
                Value<String?> syncError = const Value.absent(),
                Value<String?> idempotencyKey = const Value.absent(),
                Value<int> rowid = const Value.absent(),
              }) => OperationalRecordsCompanion.insert(
                localUuid: localUuid,
                ownerUserUuid: ownerUserUuid,
                serverUuid: serverUuid,
                resourceType: resourceType,
                reportLocalUuid: reportLocalUuid,
                payloadJson: payloadJson,
                recordVersion: recordVersion,
                syncStatus: syncStatus,
                createdAt: createdAt,
                updatedAt: updatedAt,
                lastSyncedAt: lastSyncedAt,
                serverUpdatedAt: serverUpdatedAt,
                deletedLocally: deletedLocally,
                conflictStatus: conflictStatus,
                syncError: syncError,
                idempotencyKey: idempotencyKey,
                rowid: rowid,
              ),
          withReferenceMapper: (p0) => p0
              .map(
                (e) => (
                  e.readTable(table),
                  $$OperationalRecordsTableReferences(db, table, e),
                ),
              )
              .toList(),
          prefetchHooksCallback: ({reportLocalUuid = false}) {
            return PrefetchHooks(
              db: db,
              explicitlyWatchedTables: [],
              addJoins:
                  <
                    T extends TableManagerState<
                      dynamic,
                      dynamic,
                      dynamic,
                      dynamic,
                      dynamic,
                      dynamic,
                      dynamic,
                      dynamic,
                      dynamic,
                      dynamic,
                      dynamic
                    >
                  >(state) {
                    if (reportLocalUuid) {
                      state =
                          state.withJoin(
                                currentTable: table,
                                currentColumn: table.reportLocalUuid,
                                referencedTable:
                                    $$OperationalRecordsTableReferences
                                        ._reportLocalUuidTable(db),
                                referencedColumn:
                                    $$OperationalRecordsTableReferences
                                        ._reportLocalUuidTable(db)
                                        .localUuid,
                              )
                              as T;
                    }

                    return state;
                  },
              getPrefetchedDataCallback: (items) async {
                return [];
              },
            );
          },
        ),
      );
}

typedef $$OperationalRecordsTableProcessedTableManager =
    ProcessedTableManager<
      _$AppDatabase,
      $OperationalRecordsTable,
      OperationalRecord,
      $$OperationalRecordsTableFilterComposer,
      $$OperationalRecordsTableOrderingComposer,
      $$OperationalRecordsTableAnnotationComposer,
      $$OperationalRecordsTableCreateCompanionBuilder,
      $$OperationalRecordsTableUpdateCompanionBuilder,
      (OperationalRecord, $$OperationalRecordsTableReferences),
      OperationalRecord,
      PrefetchHooks Function({bool reportLocalUuid})
    >;
typedef $$PendingAttachmentsTableCreateCompanionBuilder =
    PendingAttachmentsCompanion Function({
      required String localUuid,
      required String ownerUserUuid,
      Value<String?> serverUuid,
      required String reportLocalUuid,
      required String localPath,
      required String mediaType,
      required String checksumSha256,
      required int byteSize,
      required String syncStatus,
      Value<int> retryCount,
      required DateTime createdAt,
      required DateTime updatedAt,
      Value<String?> syncError,
      Value<String> metadataJson,
      Value<String?> idempotencyKey,
      Value<int> rowid,
    });
typedef $$PendingAttachmentsTableUpdateCompanionBuilder =
    PendingAttachmentsCompanion Function({
      Value<String> localUuid,
      Value<String> ownerUserUuid,
      Value<String?> serverUuid,
      Value<String> reportLocalUuid,
      Value<String> localPath,
      Value<String> mediaType,
      Value<String> checksumSha256,
      Value<int> byteSize,
      Value<String> syncStatus,
      Value<int> retryCount,
      Value<DateTime> createdAt,
      Value<DateTime> updatedAt,
      Value<String?> syncError,
      Value<String> metadataJson,
      Value<String?> idempotencyKey,
      Value<int> rowid,
    });

final class $$PendingAttachmentsTableReferences
    extends
        BaseReferences<
          _$AppDatabase,
          $PendingAttachmentsTable,
          PendingAttachment
        > {
  $$PendingAttachmentsTableReferences(
    super.$_db,
    super.$_table,
    super.$_typedResult,
  );

  static $DraftReportsTable _reportLocalUuidTable(_$AppDatabase db) =>
      db.draftReports.createAlias(
        'pending_attachments__report_local_uuid__draft_reports__local_uuid',
      );

  $$DraftReportsTableProcessedTableManager get reportLocalUuid {
    final $_column = $_itemColumn<String>('report_local_uuid')!;

    final manager = $$DraftReportsTableTableManager(
      $_db,
      $_db.draftReports,
    ).filter((f) => f.localUuid.sqlEquals($_column));
    final item = $_typedResult.readTableOrNull(_reportLocalUuidTable($_db));
    if (item == null) return manager;
    return ProcessedTableManager(
      manager.$state.copyWith(prefetchedData: [item]),
    );
  }
}

class $$PendingAttachmentsTableFilterComposer
    extends Composer<_$AppDatabase, $PendingAttachmentsTable> {
  $$PendingAttachmentsTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<String> get localUuid => $composableBuilder(
    column: $table.localUuid,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get ownerUserUuid => $composableBuilder(
    column: $table.ownerUserUuid,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get serverUuid => $composableBuilder(
    column: $table.serverUuid,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get localPath => $composableBuilder(
    column: $table.localPath,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get mediaType => $composableBuilder(
    column: $table.mediaType,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get checksumSha256 => $composableBuilder(
    column: $table.checksumSha256,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<int> get byteSize => $composableBuilder(
    column: $table.byteSize,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get syncStatus => $composableBuilder(
    column: $table.syncStatus,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<int> get retryCount => $composableBuilder(
    column: $table.retryCount,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<DateTime> get createdAt => $composableBuilder(
    column: $table.createdAt,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<DateTime> get updatedAt => $composableBuilder(
    column: $table.updatedAt,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get syncError => $composableBuilder(
    column: $table.syncError,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get metadataJson => $composableBuilder(
    column: $table.metadataJson,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get idempotencyKey => $composableBuilder(
    column: $table.idempotencyKey,
    builder: (column) => ColumnFilters(column),
  );

  $$DraftReportsTableFilterComposer get reportLocalUuid {
    final $$DraftReportsTableFilterComposer composer = $composerBuilder(
      composer: this,
      getCurrentColumn: (t) => t.reportLocalUuid,
      referencedTable: $db.draftReports,
      getReferencedColumn: (t) => t.localUuid,
      builder:
          (
            joinBuilder, {
            $addJoinBuilderToRootComposer,
            $removeJoinBuilderFromRootComposer,
          }) => $$DraftReportsTableFilterComposer(
            $db: $db,
            $table: $db.draftReports,
            $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
            joinBuilder: joinBuilder,
            $removeJoinBuilderFromRootComposer:
                $removeJoinBuilderFromRootComposer,
          ),
    );
    return composer;
  }
}

class $$PendingAttachmentsTableOrderingComposer
    extends Composer<_$AppDatabase, $PendingAttachmentsTable> {
  $$PendingAttachmentsTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<String> get localUuid => $composableBuilder(
    column: $table.localUuid,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get ownerUserUuid => $composableBuilder(
    column: $table.ownerUserUuid,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get serverUuid => $composableBuilder(
    column: $table.serverUuid,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get localPath => $composableBuilder(
    column: $table.localPath,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get mediaType => $composableBuilder(
    column: $table.mediaType,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get checksumSha256 => $composableBuilder(
    column: $table.checksumSha256,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<int> get byteSize => $composableBuilder(
    column: $table.byteSize,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get syncStatus => $composableBuilder(
    column: $table.syncStatus,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<int> get retryCount => $composableBuilder(
    column: $table.retryCount,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<DateTime> get createdAt => $composableBuilder(
    column: $table.createdAt,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<DateTime> get updatedAt => $composableBuilder(
    column: $table.updatedAt,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get syncError => $composableBuilder(
    column: $table.syncError,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get metadataJson => $composableBuilder(
    column: $table.metadataJson,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get idempotencyKey => $composableBuilder(
    column: $table.idempotencyKey,
    builder: (column) => ColumnOrderings(column),
  );

  $$DraftReportsTableOrderingComposer get reportLocalUuid {
    final $$DraftReportsTableOrderingComposer composer = $composerBuilder(
      composer: this,
      getCurrentColumn: (t) => t.reportLocalUuid,
      referencedTable: $db.draftReports,
      getReferencedColumn: (t) => t.localUuid,
      builder:
          (
            joinBuilder, {
            $addJoinBuilderToRootComposer,
            $removeJoinBuilderFromRootComposer,
          }) => $$DraftReportsTableOrderingComposer(
            $db: $db,
            $table: $db.draftReports,
            $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
            joinBuilder: joinBuilder,
            $removeJoinBuilderFromRootComposer:
                $removeJoinBuilderFromRootComposer,
          ),
    );
    return composer;
  }
}

class $$PendingAttachmentsTableAnnotationComposer
    extends Composer<_$AppDatabase, $PendingAttachmentsTable> {
  $$PendingAttachmentsTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<String> get localUuid =>
      $composableBuilder(column: $table.localUuid, builder: (column) => column);

  GeneratedColumn<String> get ownerUserUuid => $composableBuilder(
    column: $table.ownerUserUuid,
    builder: (column) => column,
  );

  GeneratedColumn<String> get serverUuid => $composableBuilder(
    column: $table.serverUuid,
    builder: (column) => column,
  );

  GeneratedColumn<String> get localPath =>
      $composableBuilder(column: $table.localPath, builder: (column) => column);

  GeneratedColumn<String> get mediaType =>
      $composableBuilder(column: $table.mediaType, builder: (column) => column);

  GeneratedColumn<String> get checksumSha256 => $composableBuilder(
    column: $table.checksumSha256,
    builder: (column) => column,
  );

  GeneratedColumn<int> get byteSize =>
      $composableBuilder(column: $table.byteSize, builder: (column) => column);

  GeneratedColumn<String> get syncStatus => $composableBuilder(
    column: $table.syncStatus,
    builder: (column) => column,
  );

  GeneratedColumn<int> get retryCount => $composableBuilder(
    column: $table.retryCount,
    builder: (column) => column,
  );

  GeneratedColumn<DateTime> get createdAt =>
      $composableBuilder(column: $table.createdAt, builder: (column) => column);

  GeneratedColumn<DateTime> get updatedAt =>
      $composableBuilder(column: $table.updatedAt, builder: (column) => column);

  GeneratedColumn<String> get syncError =>
      $composableBuilder(column: $table.syncError, builder: (column) => column);

  GeneratedColumn<String> get metadataJson => $composableBuilder(
    column: $table.metadataJson,
    builder: (column) => column,
  );

  GeneratedColumn<String> get idempotencyKey => $composableBuilder(
    column: $table.idempotencyKey,
    builder: (column) => column,
  );

  $$DraftReportsTableAnnotationComposer get reportLocalUuid {
    final $$DraftReportsTableAnnotationComposer composer = $composerBuilder(
      composer: this,
      getCurrentColumn: (t) => t.reportLocalUuid,
      referencedTable: $db.draftReports,
      getReferencedColumn: (t) => t.localUuid,
      builder:
          (
            joinBuilder, {
            $addJoinBuilderToRootComposer,
            $removeJoinBuilderFromRootComposer,
          }) => $$DraftReportsTableAnnotationComposer(
            $db: $db,
            $table: $db.draftReports,
            $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
            joinBuilder: joinBuilder,
            $removeJoinBuilderFromRootComposer:
                $removeJoinBuilderFromRootComposer,
          ),
    );
    return composer;
  }
}

class $$PendingAttachmentsTableTableManager
    extends
        RootTableManager<
          _$AppDatabase,
          $PendingAttachmentsTable,
          PendingAttachment,
          $$PendingAttachmentsTableFilterComposer,
          $$PendingAttachmentsTableOrderingComposer,
          $$PendingAttachmentsTableAnnotationComposer,
          $$PendingAttachmentsTableCreateCompanionBuilder,
          $$PendingAttachmentsTableUpdateCompanionBuilder,
          (PendingAttachment, $$PendingAttachmentsTableReferences),
          PendingAttachment,
          PrefetchHooks Function({bool reportLocalUuid})
        > {
  $$PendingAttachmentsTableTableManager(
    _$AppDatabase db,
    $PendingAttachmentsTable table,
  ) : super(
        TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$PendingAttachmentsTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$PendingAttachmentsTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$PendingAttachmentsTableAnnotationComposer(
                $db: db,
                $table: table,
              ),
          updateCompanionCallback:
              ({
                Value<String> localUuid = const Value.absent(),
                Value<String> ownerUserUuid = const Value.absent(),
                Value<String?> serverUuid = const Value.absent(),
                Value<String> reportLocalUuid = const Value.absent(),
                Value<String> localPath = const Value.absent(),
                Value<String> mediaType = const Value.absent(),
                Value<String> checksumSha256 = const Value.absent(),
                Value<int> byteSize = const Value.absent(),
                Value<String> syncStatus = const Value.absent(),
                Value<int> retryCount = const Value.absent(),
                Value<DateTime> createdAt = const Value.absent(),
                Value<DateTime> updatedAt = const Value.absent(),
                Value<String?> syncError = const Value.absent(),
                Value<String> metadataJson = const Value.absent(),
                Value<String?> idempotencyKey = const Value.absent(),
                Value<int> rowid = const Value.absent(),
              }) => PendingAttachmentsCompanion(
                localUuid: localUuid,
                ownerUserUuid: ownerUserUuid,
                serverUuid: serverUuid,
                reportLocalUuid: reportLocalUuid,
                localPath: localPath,
                mediaType: mediaType,
                checksumSha256: checksumSha256,
                byteSize: byteSize,
                syncStatus: syncStatus,
                retryCount: retryCount,
                createdAt: createdAt,
                updatedAt: updatedAt,
                syncError: syncError,
                metadataJson: metadataJson,
                idempotencyKey: idempotencyKey,
                rowid: rowid,
              ),
          createCompanionCallback:
              ({
                required String localUuid,
                required String ownerUserUuid,
                Value<String?> serverUuid = const Value.absent(),
                required String reportLocalUuid,
                required String localPath,
                required String mediaType,
                required String checksumSha256,
                required int byteSize,
                required String syncStatus,
                Value<int> retryCount = const Value.absent(),
                required DateTime createdAt,
                required DateTime updatedAt,
                Value<String?> syncError = const Value.absent(),
                Value<String> metadataJson = const Value.absent(),
                Value<String?> idempotencyKey = const Value.absent(),
                Value<int> rowid = const Value.absent(),
              }) => PendingAttachmentsCompanion.insert(
                localUuid: localUuid,
                ownerUserUuid: ownerUserUuid,
                serverUuid: serverUuid,
                reportLocalUuid: reportLocalUuid,
                localPath: localPath,
                mediaType: mediaType,
                checksumSha256: checksumSha256,
                byteSize: byteSize,
                syncStatus: syncStatus,
                retryCount: retryCount,
                createdAt: createdAt,
                updatedAt: updatedAt,
                syncError: syncError,
                metadataJson: metadataJson,
                idempotencyKey: idempotencyKey,
                rowid: rowid,
              ),
          withReferenceMapper: (p0) => p0
              .map(
                (e) => (
                  e.readTable(table),
                  $$PendingAttachmentsTableReferences(db, table, e),
                ),
              )
              .toList(),
          prefetchHooksCallback: ({reportLocalUuid = false}) {
            return PrefetchHooks(
              db: db,
              explicitlyWatchedTables: [],
              addJoins:
                  <
                    T extends TableManagerState<
                      dynamic,
                      dynamic,
                      dynamic,
                      dynamic,
                      dynamic,
                      dynamic,
                      dynamic,
                      dynamic,
                      dynamic,
                      dynamic,
                      dynamic
                    >
                  >(state) {
                    if (reportLocalUuid) {
                      state =
                          state.withJoin(
                                currentTable: table,
                                currentColumn: table.reportLocalUuid,
                                referencedTable:
                                    $$PendingAttachmentsTableReferences
                                        ._reportLocalUuidTable(db),
                                referencedColumn:
                                    $$PendingAttachmentsTableReferences
                                        ._reportLocalUuidTable(db)
                                        .localUuid,
                              )
                              as T;
                    }

                    return state;
                  },
              getPrefetchedDataCallback: (items) async {
                return [];
              },
            );
          },
        ),
      );
}

typedef $$PendingAttachmentsTableProcessedTableManager =
    ProcessedTableManager<
      _$AppDatabase,
      $PendingAttachmentsTable,
      PendingAttachment,
      $$PendingAttachmentsTableFilterComposer,
      $$PendingAttachmentsTableOrderingComposer,
      $$PendingAttachmentsTableAnnotationComposer,
      $$PendingAttachmentsTableCreateCompanionBuilder,
      $$PendingAttachmentsTableUpdateCompanionBuilder,
      (PendingAttachment, $$PendingAttachmentsTableReferences),
      PendingAttachment,
      PrefetchHooks Function({bool reportLocalUuid})
    >;
typedef $$SyncMetadataEntriesTableCreateCompanionBuilder =
    SyncMetadataEntriesCompanion Function({
      required String ownerUserUuid,
      required String key,
      Value<String?> value,
      required DateTime updatedAt,
      Value<int> rowid,
    });
typedef $$SyncMetadataEntriesTableUpdateCompanionBuilder =
    SyncMetadataEntriesCompanion Function({
      Value<String> ownerUserUuid,
      Value<String> key,
      Value<String?> value,
      Value<DateTime> updatedAt,
      Value<int> rowid,
    });

class $$SyncMetadataEntriesTableFilterComposer
    extends Composer<_$AppDatabase, $SyncMetadataEntriesTable> {
  $$SyncMetadataEntriesTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<String> get ownerUserUuid => $composableBuilder(
    column: $table.ownerUserUuid,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get key => $composableBuilder(
    column: $table.key,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get value => $composableBuilder(
    column: $table.value,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<DateTime> get updatedAt => $composableBuilder(
    column: $table.updatedAt,
    builder: (column) => ColumnFilters(column),
  );
}

class $$SyncMetadataEntriesTableOrderingComposer
    extends Composer<_$AppDatabase, $SyncMetadataEntriesTable> {
  $$SyncMetadataEntriesTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<String> get ownerUserUuid => $composableBuilder(
    column: $table.ownerUserUuid,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get key => $composableBuilder(
    column: $table.key,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get value => $composableBuilder(
    column: $table.value,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<DateTime> get updatedAt => $composableBuilder(
    column: $table.updatedAt,
    builder: (column) => ColumnOrderings(column),
  );
}

class $$SyncMetadataEntriesTableAnnotationComposer
    extends Composer<_$AppDatabase, $SyncMetadataEntriesTable> {
  $$SyncMetadataEntriesTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<String> get ownerUserUuid => $composableBuilder(
    column: $table.ownerUserUuid,
    builder: (column) => column,
  );

  GeneratedColumn<String> get key =>
      $composableBuilder(column: $table.key, builder: (column) => column);

  GeneratedColumn<String> get value =>
      $composableBuilder(column: $table.value, builder: (column) => column);

  GeneratedColumn<DateTime> get updatedAt =>
      $composableBuilder(column: $table.updatedAt, builder: (column) => column);
}

class $$SyncMetadataEntriesTableTableManager
    extends
        RootTableManager<
          _$AppDatabase,
          $SyncMetadataEntriesTable,
          SyncMetadataEntry,
          $$SyncMetadataEntriesTableFilterComposer,
          $$SyncMetadataEntriesTableOrderingComposer,
          $$SyncMetadataEntriesTableAnnotationComposer,
          $$SyncMetadataEntriesTableCreateCompanionBuilder,
          $$SyncMetadataEntriesTableUpdateCompanionBuilder,
          (
            SyncMetadataEntry,
            BaseReferences<
              _$AppDatabase,
              $SyncMetadataEntriesTable,
              SyncMetadataEntry
            >,
          ),
          SyncMetadataEntry,
          PrefetchHooks Function()
        > {
  $$SyncMetadataEntriesTableTableManager(
    _$AppDatabase db,
    $SyncMetadataEntriesTable table,
  ) : super(
        TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$SyncMetadataEntriesTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$SyncMetadataEntriesTableOrderingComposer(
                $db: db,
                $table: table,
              ),
          createComputedFieldComposer: () =>
              $$SyncMetadataEntriesTableAnnotationComposer(
                $db: db,
                $table: table,
              ),
          updateCompanionCallback:
              ({
                Value<String> ownerUserUuid = const Value.absent(),
                Value<String> key = const Value.absent(),
                Value<String?> value = const Value.absent(),
                Value<DateTime> updatedAt = const Value.absent(),
                Value<int> rowid = const Value.absent(),
              }) => SyncMetadataEntriesCompanion(
                ownerUserUuid: ownerUserUuid,
                key: key,
                value: value,
                updatedAt: updatedAt,
                rowid: rowid,
              ),
          createCompanionCallback:
              ({
                required String ownerUserUuid,
                required String key,
                Value<String?> value = const Value.absent(),
                required DateTime updatedAt,
                Value<int> rowid = const Value.absent(),
              }) => SyncMetadataEntriesCompanion.insert(
                ownerUserUuid: ownerUserUuid,
                key: key,
                value: value,
                updatedAt: updatedAt,
                rowid: rowid,
              ),
          withReferenceMapper: (p0) => p0
              .map((e) => (e.readTable(table), BaseReferences(db, table, e)))
              .toList(),
          prefetchHooksCallback: null,
        ),
      );
}

typedef $$SyncMetadataEntriesTableProcessedTableManager =
    ProcessedTableManager<
      _$AppDatabase,
      $SyncMetadataEntriesTable,
      SyncMetadataEntry,
      $$SyncMetadataEntriesTableFilterComposer,
      $$SyncMetadataEntriesTableOrderingComposer,
      $$SyncMetadataEntriesTableAnnotationComposer,
      $$SyncMetadataEntriesTableCreateCompanionBuilder,
      $$SyncMetadataEntriesTableUpdateCompanionBuilder,
      (
        SyncMetadataEntry,
        BaseReferences<
          _$AppDatabase,
          $SyncMetadataEntriesTable,
          SyncMetadataEntry
        >,
      ),
      SyncMetadataEntry,
      PrefetchHooks Function()
    >;
typedef $$ConflictRecordsTableCreateCompanionBuilder =
    ConflictRecordsCompanion Function({
      required String uuid,
      required String ownerUserUuid,
      required String resourceType,
      required String localUuid,
      Value<String?> serverUuid,
      required String localPayloadJson,
      required String serverPayloadJson,
      Value<String?> conflictingFieldsJson,
      required String status,
      Value<bool> serverValueRequired,
      required DateTime detectedAt,
      Value<DateTime?> resolvedAt,
      Value<int> rowid,
    });
typedef $$ConflictRecordsTableUpdateCompanionBuilder =
    ConflictRecordsCompanion Function({
      Value<String> uuid,
      Value<String> ownerUserUuid,
      Value<String> resourceType,
      Value<String> localUuid,
      Value<String?> serverUuid,
      Value<String> localPayloadJson,
      Value<String> serverPayloadJson,
      Value<String?> conflictingFieldsJson,
      Value<String> status,
      Value<bool> serverValueRequired,
      Value<DateTime> detectedAt,
      Value<DateTime?> resolvedAt,
      Value<int> rowid,
    });

class $$ConflictRecordsTableFilterComposer
    extends Composer<_$AppDatabase, $ConflictRecordsTable> {
  $$ConflictRecordsTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<String> get uuid => $composableBuilder(
    column: $table.uuid,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get ownerUserUuid => $composableBuilder(
    column: $table.ownerUserUuid,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get resourceType => $composableBuilder(
    column: $table.resourceType,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get localUuid => $composableBuilder(
    column: $table.localUuid,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get serverUuid => $composableBuilder(
    column: $table.serverUuid,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get localPayloadJson => $composableBuilder(
    column: $table.localPayloadJson,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get serverPayloadJson => $composableBuilder(
    column: $table.serverPayloadJson,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get conflictingFieldsJson => $composableBuilder(
    column: $table.conflictingFieldsJson,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get status => $composableBuilder(
    column: $table.status,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<bool> get serverValueRequired => $composableBuilder(
    column: $table.serverValueRequired,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<DateTime> get detectedAt => $composableBuilder(
    column: $table.detectedAt,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<DateTime> get resolvedAt => $composableBuilder(
    column: $table.resolvedAt,
    builder: (column) => ColumnFilters(column),
  );
}

class $$ConflictRecordsTableOrderingComposer
    extends Composer<_$AppDatabase, $ConflictRecordsTable> {
  $$ConflictRecordsTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<String> get uuid => $composableBuilder(
    column: $table.uuid,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get ownerUserUuid => $composableBuilder(
    column: $table.ownerUserUuid,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get resourceType => $composableBuilder(
    column: $table.resourceType,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get localUuid => $composableBuilder(
    column: $table.localUuid,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get serverUuid => $composableBuilder(
    column: $table.serverUuid,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get localPayloadJson => $composableBuilder(
    column: $table.localPayloadJson,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get serverPayloadJson => $composableBuilder(
    column: $table.serverPayloadJson,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get conflictingFieldsJson => $composableBuilder(
    column: $table.conflictingFieldsJson,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get status => $composableBuilder(
    column: $table.status,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<bool> get serverValueRequired => $composableBuilder(
    column: $table.serverValueRequired,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<DateTime> get detectedAt => $composableBuilder(
    column: $table.detectedAt,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<DateTime> get resolvedAt => $composableBuilder(
    column: $table.resolvedAt,
    builder: (column) => ColumnOrderings(column),
  );
}

class $$ConflictRecordsTableAnnotationComposer
    extends Composer<_$AppDatabase, $ConflictRecordsTable> {
  $$ConflictRecordsTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<String> get uuid =>
      $composableBuilder(column: $table.uuid, builder: (column) => column);

  GeneratedColumn<String> get ownerUserUuid => $composableBuilder(
    column: $table.ownerUserUuid,
    builder: (column) => column,
  );

  GeneratedColumn<String> get resourceType => $composableBuilder(
    column: $table.resourceType,
    builder: (column) => column,
  );

  GeneratedColumn<String> get localUuid =>
      $composableBuilder(column: $table.localUuid, builder: (column) => column);

  GeneratedColumn<String> get serverUuid => $composableBuilder(
    column: $table.serverUuid,
    builder: (column) => column,
  );

  GeneratedColumn<String> get localPayloadJson => $composableBuilder(
    column: $table.localPayloadJson,
    builder: (column) => column,
  );

  GeneratedColumn<String> get serverPayloadJson => $composableBuilder(
    column: $table.serverPayloadJson,
    builder: (column) => column,
  );

  GeneratedColumn<String> get conflictingFieldsJson => $composableBuilder(
    column: $table.conflictingFieldsJson,
    builder: (column) => column,
  );

  GeneratedColumn<String> get status =>
      $composableBuilder(column: $table.status, builder: (column) => column);

  GeneratedColumn<bool> get serverValueRequired => $composableBuilder(
    column: $table.serverValueRequired,
    builder: (column) => column,
  );

  GeneratedColumn<DateTime> get detectedAt => $composableBuilder(
    column: $table.detectedAt,
    builder: (column) => column,
  );

  GeneratedColumn<DateTime> get resolvedAt => $composableBuilder(
    column: $table.resolvedAt,
    builder: (column) => column,
  );
}

class $$ConflictRecordsTableTableManager
    extends
        RootTableManager<
          _$AppDatabase,
          $ConflictRecordsTable,
          ConflictRecord,
          $$ConflictRecordsTableFilterComposer,
          $$ConflictRecordsTableOrderingComposer,
          $$ConflictRecordsTableAnnotationComposer,
          $$ConflictRecordsTableCreateCompanionBuilder,
          $$ConflictRecordsTableUpdateCompanionBuilder,
          (
            ConflictRecord,
            BaseReferences<
              _$AppDatabase,
              $ConflictRecordsTable,
              ConflictRecord
            >,
          ),
          ConflictRecord,
          PrefetchHooks Function()
        > {
  $$ConflictRecordsTableTableManager(
    _$AppDatabase db,
    $ConflictRecordsTable table,
  ) : super(
        TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$ConflictRecordsTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$ConflictRecordsTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$ConflictRecordsTableAnnotationComposer($db: db, $table: table),
          updateCompanionCallback:
              ({
                Value<String> uuid = const Value.absent(),
                Value<String> ownerUserUuid = const Value.absent(),
                Value<String> resourceType = const Value.absent(),
                Value<String> localUuid = const Value.absent(),
                Value<String?> serverUuid = const Value.absent(),
                Value<String> localPayloadJson = const Value.absent(),
                Value<String> serverPayloadJson = const Value.absent(),
                Value<String?> conflictingFieldsJson = const Value.absent(),
                Value<String> status = const Value.absent(),
                Value<bool> serverValueRequired = const Value.absent(),
                Value<DateTime> detectedAt = const Value.absent(),
                Value<DateTime?> resolvedAt = const Value.absent(),
                Value<int> rowid = const Value.absent(),
              }) => ConflictRecordsCompanion(
                uuid: uuid,
                ownerUserUuid: ownerUserUuid,
                resourceType: resourceType,
                localUuid: localUuid,
                serverUuid: serverUuid,
                localPayloadJson: localPayloadJson,
                serverPayloadJson: serverPayloadJson,
                conflictingFieldsJson: conflictingFieldsJson,
                status: status,
                serverValueRequired: serverValueRequired,
                detectedAt: detectedAt,
                resolvedAt: resolvedAt,
                rowid: rowid,
              ),
          createCompanionCallback:
              ({
                required String uuid,
                required String ownerUserUuid,
                required String resourceType,
                required String localUuid,
                Value<String?> serverUuid = const Value.absent(),
                required String localPayloadJson,
                required String serverPayloadJson,
                Value<String?> conflictingFieldsJson = const Value.absent(),
                required String status,
                Value<bool> serverValueRequired = const Value.absent(),
                required DateTime detectedAt,
                Value<DateTime?> resolvedAt = const Value.absent(),
                Value<int> rowid = const Value.absent(),
              }) => ConflictRecordsCompanion.insert(
                uuid: uuid,
                ownerUserUuid: ownerUserUuid,
                resourceType: resourceType,
                localUuid: localUuid,
                serverUuid: serverUuid,
                localPayloadJson: localPayloadJson,
                serverPayloadJson: serverPayloadJson,
                conflictingFieldsJson: conflictingFieldsJson,
                status: status,
                serverValueRequired: serverValueRequired,
                detectedAt: detectedAt,
                resolvedAt: resolvedAt,
                rowid: rowid,
              ),
          withReferenceMapper: (p0) => p0
              .map((e) => (e.readTable(table), BaseReferences(db, table, e)))
              .toList(),
          prefetchHooksCallback: null,
        ),
      );
}

typedef $$ConflictRecordsTableProcessedTableManager =
    ProcessedTableManager<
      _$AppDatabase,
      $ConflictRecordsTable,
      ConflictRecord,
      $$ConflictRecordsTableFilterComposer,
      $$ConflictRecordsTableOrderingComposer,
      $$ConflictRecordsTableAnnotationComposer,
      $$ConflictRecordsTableCreateCompanionBuilder,
      $$ConflictRecordsTableUpdateCompanionBuilder,
      (
        ConflictRecord,
        BaseReferences<_$AppDatabase, $ConflictRecordsTable, ConflictRecord>,
      ),
      ConflictRecord,
      PrefetchHooks Function()
    >;
typedef $$LocalSyncLogsTableCreateCompanionBuilder =
    LocalSyncLogsCompanion Function({
      required String uuid,
      required String ownerUserUuid,
      required DateTime startedAt,
      Value<DateTime?> completedAt,
      Value<int> uploadedCount,
      Value<int> downloadedCount,
      Value<int> conflictCount,
      Value<int> failedCount,
      required String status,
      Value<String?> safeError,
      Value<int> rowid,
    });
typedef $$LocalSyncLogsTableUpdateCompanionBuilder =
    LocalSyncLogsCompanion Function({
      Value<String> uuid,
      Value<String> ownerUserUuid,
      Value<DateTime> startedAt,
      Value<DateTime?> completedAt,
      Value<int> uploadedCount,
      Value<int> downloadedCount,
      Value<int> conflictCount,
      Value<int> failedCount,
      Value<String> status,
      Value<String?> safeError,
      Value<int> rowid,
    });

class $$LocalSyncLogsTableFilterComposer
    extends Composer<_$AppDatabase, $LocalSyncLogsTable> {
  $$LocalSyncLogsTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<String> get uuid => $composableBuilder(
    column: $table.uuid,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get ownerUserUuid => $composableBuilder(
    column: $table.ownerUserUuid,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<DateTime> get startedAt => $composableBuilder(
    column: $table.startedAt,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<DateTime> get completedAt => $composableBuilder(
    column: $table.completedAt,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<int> get uploadedCount => $composableBuilder(
    column: $table.uploadedCount,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<int> get downloadedCount => $composableBuilder(
    column: $table.downloadedCount,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<int> get conflictCount => $composableBuilder(
    column: $table.conflictCount,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<int> get failedCount => $composableBuilder(
    column: $table.failedCount,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get status => $composableBuilder(
    column: $table.status,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get safeError => $composableBuilder(
    column: $table.safeError,
    builder: (column) => ColumnFilters(column),
  );
}

class $$LocalSyncLogsTableOrderingComposer
    extends Composer<_$AppDatabase, $LocalSyncLogsTable> {
  $$LocalSyncLogsTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<String> get uuid => $composableBuilder(
    column: $table.uuid,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get ownerUserUuid => $composableBuilder(
    column: $table.ownerUserUuid,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<DateTime> get startedAt => $composableBuilder(
    column: $table.startedAt,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<DateTime> get completedAt => $composableBuilder(
    column: $table.completedAt,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<int> get uploadedCount => $composableBuilder(
    column: $table.uploadedCount,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<int> get downloadedCount => $composableBuilder(
    column: $table.downloadedCount,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<int> get conflictCount => $composableBuilder(
    column: $table.conflictCount,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<int> get failedCount => $composableBuilder(
    column: $table.failedCount,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get status => $composableBuilder(
    column: $table.status,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get safeError => $composableBuilder(
    column: $table.safeError,
    builder: (column) => ColumnOrderings(column),
  );
}

class $$LocalSyncLogsTableAnnotationComposer
    extends Composer<_$AppDatabase, $LocalSyncLogsTable> {
  $$LocalSyncLogsTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<String> get uuid =>
      $composableBuilder(column: $table.uuid, builder: (column) => column);

  GeneratedColumn<String> get ownerUserUuid => $composableBuilder(
    column: $table.ownerUserUuid,
    builder: (column) => column,
  );

  GeneratedColumn<DateTime> get startedAt =>
      $composableBuilder(column: $table.startedAt, builder: (column) => column);

  GeneratedColumn<DateTime> get completedAt => $composableBuilder(
    column: $table.completedAt,
    builder: (column) => column,
  );

  GeneratedColumn<int> get uploadedCount => $composableBuilder(
    column: $table.uploadedCount,
    builder: (column) => column,
  );

  GeneratedColumn<int> get downloadedCount => $composableBuilder(
    column: $table.downloadedCount,
    builder: (column) => column,
  );

  GeneratedColumn<int> get conflictCount => $composableBuilder(
    column: $table.conflictCount,
    builder: (column) => column,
  );

  GeneratedColumn<int> get failedCount => $composableBuilder(
    column: $table.failedCount,
    builder: (column) => column,
  );

  GeneratedColumn<String> get status =>
      $composableBuilder(column: $table.status, builder: (column) => column);

  GeneratedColumn<String> get safeError =>
      $composableBuilder(column: $table.safeError, builder: (column) => column);
}

class $$LocalSyncLogsTableTableManager
    extends
        RootTableManager<
          _$AppDatabase,
          $LocalSyncLogsTable,
          LocalSyncLog,
          $$LocalSyncLogsTableFilterComposer,
          $$LocalSyncLogsTableOrderingComposer,
          $$LocalSyncLogsTableAnnotationComposer,
          $$LocalSyncLogsTableCreateCompanionBuilder,
          $$LocalSyncLogsTableUpdateCompanionBuilder,
          (
            LocalSyncLog,
            BaseReferences<_$AppDatabase, $LocalSyncLogsTable, LocalSyncLog>,
          ),
          LocalSyncLog,
          PrefetchHooks Function()
        > {
  $$LocalSyncLogsTableTableManager(_$AppDatabase db, $LocalSyncLogsTable table)
    : super(
        TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$LocalSyncLogsTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$LocalSyncLogsTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$LocalSyncLogsTableAnnotationComposer($db: db, $table: table),
          updateCompanionCallback:
              ({
                Value<String> uuid = const Value.absent(),
                Value<String> ownerUserUuid = const Value.absent(),
                Value<DateTime> startedAt = const Value.absent(),
                Value<DateTime?> completedAt = const Value.absent(),
                Value<int> uploadedCount = const Value.absent(),
                Value<int> downloadedCount = const Value.absent(),
                Value<int> conflictCount = const Value.absent(),
                Value<int> failedCount = const Value.absent(),
                Value<String> status = const Value.absent(),
                Value<String?> safeError = const Value.absent(),
                Value<int> rowid = const Value.absent(),
              }) => LocalSyncLogsCompanion(
                uuid: uuid,
                ownerUserUuid: ownerUserUuid,
                startedAt: startedAt,
                completedAt: completedAt,
                uploadedCount: uploadedCount,
                downloadedCount: downloadedCount,
                conflictCount: conflictCount,
                failedCount: failedCount,
                status: status,
                safeError: safeError,
                rowid: rowid,
              ),
          createCompanionCallback:
              ({
                required String uuid,
                required String ownerUserUuid,
                required DateTime startedAt,
                Value<DateTime?> completedAt = const Value.absent(),
                Value<int> uploadedCount = const Value.absent(),
                Value<int> downloadedCount = const Value.absent(),
                Value<int> conflictCount = const Value.absent(),
                Value<int> failedCount = const Value.absent(),
                required String status,
                Value<String?> safeError = const Value.absent(),
                Value<int> rowid = const Value.absent(),
              }) => LocalSyncLogsCompanion.insert(
                uuid: uuid,
                ownerUserUuid: ownerUserUuid,
                startedAt: startedAt,
                completedAt: completedAt,
                uploadedCount: uploadedCount,
                downloadedCount: downloadedCount,
                conflictCount: conflictCount,
                failedCount: failedCount,
                status: status,
                safeError: safeError,
                rowid: rowid,
              ),
          withReferenceMapper: (p0) => p0
              .map((e) => (e.readTable(table), BaseReferences(db, table, e)))
              .toList(),
          prefetchHooksCallback: null,
        ),
      );
}

typedef $$LocalSyncLogsTableProcessedTableManager =
    ProcessedTableManager<
      _$AppDatabase,
      $LocalSyncLogsTable,
      LocalSyncLog,
      $$LocalSyncLogsTableFilterComposer,
      $$LocalSyncLogsTableOrderingComposer,
      $$LocalSyncLogsTableAnnotationComposer,
      $$LocalSyncLogsTableCreateCompanionBuilder,
      $$LocalSyncLogsTableUpdateCompanionBuilder,
      (
        LocalSyncLog,
        BaseReferences<_$AppDatabase, $LocalSyncLogsTable, LocalSyncLog>,
      ),
      LocalSyncLog,
      PrefetchHooks Function()
    >;

class $AppDatabaseManager {
  final _$AppDatabase _db;
  $AppDatabaseManager(this._db);
  $$CachedReferenceItemsTableTableManager get cachedReferenceItems =>
      $$CachedReferenceItemsTableTableManager(_db, _db.cachedReferenceItems);
  $$CachedMasterRecordsTableTableManager get cachedMasterRecords =>
      $$CachedMasterRecordsTableTableManager(_db, _db.cachedMasterRecords);
  $$DraftReportsTableTableManager get draftReports =>
      $$DraftReportsTableTableManager(_db, _db.draftReports);
  $$OperationalRecordsTableTableManager get operationalRecords =>
      $$OperationalRecordsTableTableManager(_db, _db.operationalRecords);
  $$PendingAttachmentsTableTableManager get pendingAttachments =>
      $$PendingAttachmentsTableTableManager(_db, _db.pendingAttachments);
  $$SyncMetadataEntriesTableTableManager get syncMetadataEntries =>
      $$SyncMetadataEntriesTableTableManager(_db, _db.syncMetadataEntries);
  $$ConflictRecordsTableTableManager get conflictRecords =>
      $$ConflictRecordsTableTableManager(_db, _db.conflictRecords);
  $$LocalSyncLogsTableTableManager get localSyncLogs =>
      $$LocalSyncLogsTableTableManager(_db, _db.localSyncLogs);
}
