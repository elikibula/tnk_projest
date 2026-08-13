class BootstrapBundle {
  const BootstrapBundle({
    required this.schemaVersion,
    required this.serverTime,
    required this.syncCursor,
    required this.user,
    required this.device,
    required this.villages,
    required this.reportingPeriods,
    required this.reports,
    required this.sectionDefinitions,
    required this.workflowCapabilities,
  });

  factory BootstrapBundle.fromJson(Map<String, dynamic> json) {
    Map<String, dynamic> object(String key) =>
        Map<String, dynamic>.from(json[key] as Map);
    List<Map<String, dynamic>> objects(String key) => (json[key] as List)
        .map((value) => Map<String, dynamic>.from(value as Map))
        .toList(growable: false);

    return BootstrapBundle(
      schemaVersion: json['schema_version'] as int,
      serverTime: DateTime.parse(json['server_time'] as String).toUtc(),
      syncCursor: json['sync_cursor'] as String?,
      user: object('user'),
      device: object('device'),
      villages: objects('villages'),
      reportingPeriods: objects('reporting_periods'),
      reports: objects('reports'),
      sectionDefinitions: objects('section_definitions'),
      workflowCapabilities: object('workflow_capabilities'),
    );
  }

  final int schemaVersion;
  final DateTime serverTime;
  final String? syncCursor;
  final Map<String, dynamic> user;
  final Map<String, dynamic> device;
  final List<Map<String, dynamic>> villages;
  final List<Map<String, dynamic>> reportingPeriods;
  final List<Map<String, dynamic>> reports;
  final List<Map<String, dynamic>> sectionDefinitions;
  final Map<String, dynamic> workflowCapabilities;
}

class BootstrapSnapshot {
  const BootstrapSnapshot({
    required this.ownerUserUuid,
    required this.cachedAt,
    required this.villageCount,
    required this.reportingPeriodCount,
    required this.reportCount,
    required this.sectionCount,
    required this.isOffline,
  });

  final String ownerUserUuid;
  final DateTime cachedAt;
  final int villageCount;
  final int reportingPeriodCount;
  final int reportCount;
  final int sectionCount;
  final bool isOffline;

  BootstrapSnapshot copyWith({bool? isOffline}) => BootstrapSnapshot(
    ownerUserUuid: ownerUserUuid,
    cachedAt: cachedAt,
    villageCount: villageCount,
    reportingPeriodCount: reportingPeriodCount,
    reportCount: reportCount,
    sectionCount: sectionCount,
    isOffline: isOffline ?? this.isOffline,
  );
}
