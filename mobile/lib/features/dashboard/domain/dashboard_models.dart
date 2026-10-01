import '../../reporting/domain/reporting_models.dart';

class VillageIndicator {
  const VillageIndicator({
    required this.code,
    required this.nameEn,
    required this.nameFj,
    required this.value,
    required this.unit,
    required this.status,
    required this.qualityRating,
    required this.breakdown,
  });
  factory VillageIndicator.fromJson(Map<String, dynamic> json) =>
      VillageIndicator(
        code: json['code'].toString(),
        nameEn: (json['name_en'] ?? json['name'] ?? '').toString(),
        nameFj: json['name_fj']?.toString() ?? '',
        value: json['value']?.toString(),
        unit: json['unit'].toString(),
        status: json['status'].toString(),
        qualityRating: json['quality_rating'].toString(),
        breakdown: Map<String, dynamic>.from(
          json['breakdown'] as Map? ?? const {},
        ),
      );
  final String code;
  final String nameEn;
  final String nameFj;
  String nameFor(String languageCode) =>
      languageCode == 'fj' && nameFj.isNotEmpty ? nameFj : nameEn;
  final String? value;
  final String unit;
  final String status;
  final String qualityRating;
  final Map<String, dynamic> breakdown;
}

class DashboardSnapshot {
  const DashboardSnapshot({
    required this.report,
    required this.location,
    required this.periodLabel,
    required this.pendingIssues,
    required this.indicators,
    required this.pendingSync,
    required this.lastSuccessfulSync,
    required this.isOffline,
  });
  factory DashboardSnapshot.fromJson(
    Map<String, dynamic> json, {
    int pendingSync = 0,
    DateTime? lastSuccessfulSync,
    bool isOffline = false,
  }) => DashboardSnapshot(
    report: json['report'] == null
        ? null
        : LocalReportSummary.fromJson(
            Map<String, dynamic>.from(json['report'] as Map),
          ),
    location: Map<String, dynamic>.from(json['location'] as Map? ?? const {}),
    periodLabel:
        (json['reporting_period'] as Map?)?['label']?.toString() ??
        'No current reporting period',
    pendingIssues: json['pending_validation_issues'] as int? ?? 0,
    indicators: (json['indicators'] as List<dynamic>? ?? const [])
        .map(
          (value) => VillageIndicator.fromJson(
            Map<String, dynamic>.from(value as Map),
          ),
        )
        .toList(growable: false),
    pendingSync: pendingSync,
    lastSuccessfulSync: lastSuccessfulSync,
    isOffline: isOffline,
  );
  final LocalReportSummary? report;
  final Map<String, dynamic> location;
  final String periodLabel;
  final int pendingIssues;
  final List<VillageIndicator> indicators;
  final int pendingSync;
  final DateTime? lastSuccessfulSync;
  final bool isOffline;
}

class StartReportOption {
  const StartReportOption(
    this.uuid,
    this.label, {
    this.tikinaUuid = '',
    this.tikina = '',
    this.provinceUuid = '',
    this.province = '',
  });
  final String uuid, label, tikinaUuid, tikina, provinceUuid, province;
}
