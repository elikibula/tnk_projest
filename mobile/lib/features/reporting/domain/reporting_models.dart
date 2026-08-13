import 'dart:convert';

class LocalReportSummary {
  const LocalReportSummary({
    required this.uuid,
    required this.villageUuid,
    required this.periodUuid,
    required this.status,
    required this.completionPercentage,
    required this.recordVersion,
    this.dataQualityScore,
    this.previousReportUuid,
    this.sections = const [],
  });

  factory LocalReportSummary.fromJson(Map<String, dynamic> json) =>
      LocalReportSummary(
        uuid: json['uuid'].toString(),
        villageUuid: json['village_uuid'].toString(),
        periodUuid: json['reporting_period_uuid'].toString(),
        status: json['status']?.toString() ?? 'draft',
        completionPercentage: _decimal(json['completeness_percentage']).toInt(),
        recordVersion: (json['record_version'] as int?) ?? 0,
        dataQualityScore: json['data_quality_score'] == null
            ? null
            : _decimal(json['data_quality_score']),
        previousReportUuid: json['previous_report_uuid']?.toString(),
        sections: (json['sections'] as List<dynamic>? ?? const [])
            .map(
              (value) => LocalSectionStatus.fromJson(
                Map<String, dynamic>.from(value as Map),
              ),
            )
            .toList(growable: false),
      );

  final String uuid;
  final String villageUuid;
  final String periodUuid;
  final String status;
  final int completionPercentage;
  final int recordVersion;
  final double? dataQualityScore;
  final String? previousReportUuid;
  final List<LocalSectionStatus> sections;

  bool get isEditable => status == 'draft' || status == 'returned_to_village';
}

class LocalSectionStatus {
  const LocalSectionStatus({
    required this.code,
    required this.status,
    required this.completion,
    required this.issueCount,
    required this.lastUpdatedAt,
  });
  factory LocalSectionStatus.fromJson(Map<String, dynamic> json) =>
      LocalSectionStatus(
        code: json['section_code'].toString(),
        status: json['status'].toString(),
        completion: _decimal(json['completion_percentage']),
        issueCount: json['issue_count'] as int? ?? 0,
        lastUpdatedAt: DateTime.tryParse(
          json['last_updated_at']?.toString() ?? '',
        ),
      );
  final String code;
  final String status;
  final double completion;
  final int issueCount;
  final DateTime? lastUpdatedAt;
}

double _decimal(Object? value) {
  if (value is num) return value.toDouble();
  return double.tryParse(value?.toString() ?? '') ?? 0;
}

class ReportSectionDefinition {
  const ReportSectionDefinition({
    required this.code,
    required this.label,
    required this.entries,
  });

  factory ReportSectionDefinition.fromJson(Map<String, dynamic> json) =>
      ReportSectionDefinition(
        code: json['code'].toString(),
        label: json['label'].toString(),
        entries: (json['entry_types'] as List<dynamic>? ?? const [])
            .map(
              (value) => ReportEntryDefinition.fromJson(
                Map<String, dynamic>.from(value as Map),
              ),
            )
            .toList(growable: false),
      );

  final String code;
  final String label;
  final List<ReportEntryDefinition> entries;
}

class ReportEntryDefinition {
  const ReportEntryDefinition({
    required this.key,
    required this.label,
    required this.fields,
    required this.allowCreate,
    required this.allowDelete,
  });

  factory ReportEntryDefinition.fromJson(Map<String, dynamic> json) {
    final definitions = json['field_definitions'] as List<dynamic>?;
    final fields = definitions != null
        ? definitions
              .map(
                (value) => ReportFieldDefinition.fromJson(
                  Map<String, dynamic>.from(value as Map),
                ),
              )
              .toList(growable: false)
        : (json['fields'] as List<dynamic>? ?? const [])
              .map(
                (value) => ReportFieldDefinition(
                  name: value.toString(),
                  label: value.toString().replaceAll('_', ' '),
                  type: ReportFieldType.text,
                  required: false,
                  choices: const [],
                ),
              )
              .toList(growable: false);
    return ReportEntryDefinition(
      key: json['key'].toString(),
      label: json['label'].toString(),
      fields: fields,
      allowCreate: json['allow_create'] as bool? ?? true,
      allowDelete: json['allow_delete'] as bool? ?? true,
    );
  }

  final String key;
  final String label;
  final List<ReportFieldDefinition> fields;
  final bool allowCreate;
  final bool allowDelete;
}

enum ReportFieldType {
  text,
  integer,
  decimal,
  boolean,
  date,
  datetime,
  choice,
  relation,
}

class ReportFieldDefinition {
  const ReportFieldDefinition({
    required this.name,
    required this.label,
    required this.type,
    required this.required,
    required this.choices,
    this.maxLength,
  });

  factory ReportFieldDefinition.fromJson(Map<String, dynamic> json) =>
      ReportFieldDefinition(
        name: json['name'].toString(),
        label: json['label'].toString(),
        type: ReportFieldType.values.firstWhere(
          (value) => value.name == json['type'],
          orElse: () => ReportFieldType.text,
        ),
        required: json['required'] as bool? ?? false,
        maxLength: json['max_length'] as int?,
        choices: (json['choices'] as List<dynamic>? ?? const [])
            .map(
              (value) => ReportFieldChoice.fromJson(
                Map<String, dynamic>.from(value as Map),
              ),
            )
            .toList(growable: false),
      );

  final String name;
  final String label;
  final ReportFieldType type;
  final bool required;
  final int? maxLength;
  final List<ReportFieldChoice> choices;
}

class ReportFieldChoice {
  const ReportFieldChoice({required this.value, required this.label});
  factory ReportFieldChoice.fromJson(Map<String, dynamic> json) =>
      ReportFieldChoice(
        value: json['value'].toString(),
        label: json['label'].toString(),
      );
  final String value;
  final String label;
}

class LocalReportEntry {
  const LocalReportEntry({
    required this.localUuid,
    required this.sectionCode,
    required this.entryType,
    required this.values,
    required this.syncStatus,
    required this.updatedAt,
  });

  factory LocalReportEntry.fromStored({
    required String localUuid,
    required String resourceType,
    required String payloadJson,
    required String syncStatus,
    required DateTime updatedAt,
  }) {
    final payload = jsonDecode(payloadJson) as Map<String, dynamic>;
    return LocalReportEntry(
      localUuid: localUuid,
      sectionCode: payload['section_code'].toString(),
      entryType: resourceType,
      values: Map<String, dynamic>.from(payload['values'] as Map? ?? const {}),
      syncStatus: syncStatus,
      updatedAt: updatedAt,
    );
  }

  final String localUuid;
  final String sectionCode;
  final String entryType;
  final Map<String, dynamic> values;
  final String syncStatus;
  final DateTime updatedAt;
}
