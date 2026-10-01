import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/auth/auth_models.dart';
import '../data/reporting_providers.dart';
import '../data/reporting_repository.dart';
import '../domain/reporting_models.dart';
import 'section_entries_screen.dart';
import 'data_type_style.dart';

class ReportSectionScreen extends ConsumerWidget {
  const ReportSectionScreen({
    required this.session,
    required this.report,
    super.key,
  });

  final AuthSession session;
  final LocalReportSummary report;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final repository = ref.watch(reportingRepositoryProvider);
    return Scaffold(
      appBar: AppBar(
        title: Text(
          report.periodLabel.isEmpty ? 'Report sections' : report.periodLabel,
        ),
      ),
      body: repository.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, stackTrace) =>
            const Center(child: Text('Report sections could not be opened.')),
        data: (repository) => FutureBuilder<(String, List<ReportSectionDefinition>)>(
          future: _load(repository),
          builder: (context, snapshot) {
            if (!snapshot.hasData) {
              return const Center(child: CircularProgressIndicator());
            }
            final (localReportUuid, sections) = snapshot.data!;
            return ListView.separated(
              padding: const EdgeInsets.all(16),
              itemCount: sections.length + 1,
              separatorBuilder: (_, _) => const SizedBox(height: 8),
              itemBuilder: (context, index) {
                if (index == 0) {
                  return Card(
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            report.villageName.isEmpty
                                ? 'Report'
                                : report.villageName,
                            style: Theme.of(context).textTheme.titleLarge,
                          ),
                          Text(
                            '${report.statusLabel.isEmpty ? report.status.replaceAll('_', ' ') : report.statusLabel} · ${report.completionPercentage}% complete',
                          ),
                          if (report.workflowHistory.isNotEmpty) ...[
                            const Divider(),
                            const Text('Workflow history'),
                            for (final item in report.workflowHistory)
                              Text(
                                '${item['status']} · ${item['reviewer']}${item['comment'].toString().isEmpty ? '' : ' — ${item['comment']}'}',
                              ),
                          ],
                        ],
                      ),
                    ),
                  );
                }
                final section = sections[index - 1];
                final state = report.sections
                    .where((value) => value.code == section.code)
                    .firstOrNull;
                final dataTypes = section.entries
                    .map((item) => item.dataType)
                    .toSet();
                final primaryType = dataTypes.contains('workflow')
                    ? 'workflow'
                    : dataTypes.contains('master')
                    ? 'master'
                    : dataTypes.contains('operational')
                    ? 'operational'
                    : dataTypes.contains('snapshot')
                    ? 'snapshot'
                    : 'workflow';
                return DataTypeCard(
                  dataType: primaryType,
                  child: ListTile(
                    minVerticalPadding: 14,
                    leading: CircleAvatar(child: Text('$index')),
                    title: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(section.label),
                        if (dataTypes.isNotEmpty) ...[
                          const SizedBox(height: 6),
                          Wrap(
                            spacing: 5,
                            runSpacing: 5,
                            children: [
                              for (final type in dataTypes) DataTypeLabel(type),
                            ],
                          ),
                        ],
                      ],
                    ),
                    subtitle: Text(
                      '${state?.status.replaceAll('_', ' ') ?? 'not started'} · '
                      '${state?.completion.toStringAsFixed(0) ?? '0'}% · '
                      '${state?.issueCount ?? 0} issue(s)\n'
                      'Updated ${state?.lastUpdatedAt == null ? 'not yet' : '${state!.lastUpdatedAt!.day}/${state.lastUpdatedAt!.month}/${state.lastUpdatedAt!.year}'}',
                    ),
                    trailing: report.isEditable
                        ? const Icon(Icons.chevron_right)
                        : const Icon(Icons.lock_outline),
                    onTap: () => Navigator.of(context).push(
                      MaterialPageRoute<void>(
                        builder: (_) => SectionEntriesScreen(
                          session: session,
                          reportLocalUuid: localReportUuid,
                          section: section,
                          editable: report.isEditable,
                        ),
                      ),
                    ),
                  ),
                );
              },
            );
          },
        ),
      ),
    );
  }

  Future<(String, List<ReportSectionDefinition>)> _load(
    ReportingRepository repository,
  ) async => (
    await repository.materializeReport(session.user.uuid, report),
    await repository.listSections(session.user.uuid),
  );
}
