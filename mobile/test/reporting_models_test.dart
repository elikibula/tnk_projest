import 'package:flutter_test/flutter_test.dart';
import 'package:tnk_insight_mobile/features/reporting/domain/reporting_models.dart';

void main() {
  test('DRF decimal strings parse in report and section summaries', () {
    final report = LocalReportSummary.fromJson({
      'uuid': 'report-1',
      'village_uuid': 'village-1',
      'reporting_period_uuid': 'period-1',
      'status': 'draft',
      'completeness_percentage': '62.50',
      'data_quality_score': '87.25',
      'record_version': 1,
      'sections': [
        {
          'section_code': 'water',
          'status': 'in_progress',
          'completion_percentage': '40.50',
          'issue_count': 0,
        },
      ],
    });
    expect(report.completionPercentage, 62);
    expect(report.dataQualityScore, 87.25);
    expect(report.sections.single.completion, 40.5);
  });
}
