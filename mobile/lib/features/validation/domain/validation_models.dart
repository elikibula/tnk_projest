class QualityIssue {
  const QualityIssue({
    required this.uuid,
    required this.section,
    required this.fieldName,
    required this.severity,
    required this.message,
    required this.currentValue,
    required this.previousValue,
  });
  factory QualityIssue.fromJson(Map<String, dynamic> json) => QualityIssue(
    uuid: json['uuid'].toString(),
    section: json['section'].toString(),
    fieldName: json['field_name']?.toString() ?? '',
    severity: json['severity'].toString(),
    message: json['message'].toString(),
    currentValue: json['current_value']?.toString() ?? '',
    previousValue: json['previous_value']?.toString() ?? '',
  );
  final String uuid;
  final String section;
  final String fieldName;
  final String severity;
  final String message;
  final String currentValue;
  final String previousValue;
  bool get blocking => severity == 'critical';
}

class ValidationSnapshot {
  const ValidationSnapshot({required this.report, required this.issues});
  factory ValidationSnapshot.fromJson(Map<String, dynamic> json) =>
      ValidationSnapshot(
        report: Map<String, dynamic>.from(json['report'] as Map),
        issues: (json['issues'] as List<dynamic>? ?? const [])
            .map(
              (value) => QualityIssue.fromJson(
                Map<String, dynamic>.from(value as Map),
              ),
            )
            .toList(growable: false),
      );
  final Map<String, dynamic> report;
  final List<QualityIssue> issues;
}

class SubmissionNotConfirmed implements Exception {
  const SubmissionNotConfirmed([this.message = 'Submission not confirmed.']);
  final String message;
}
