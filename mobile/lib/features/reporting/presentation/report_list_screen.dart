import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/auth/auth_models.dart';
import '../data/reporting_providers.dart';
import '../domain/reporting_models.dart';
import 'report_section_screen.dart';

class ReportListScreen extends ConsumerWidget {
  const ReportListScreen({required this.session, super.key});
  final AuthSession session;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final repository = ref.watch(reportingRepositoryProvider);
    return Scaffold(
      appBar: AppBar(title: const Text('TNK reports')),
      body: repository.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, stackTrace) => const Center(
          child: Text('Reports could not be opened from this device.'),
        ),
        data: (repository) => FutureBuilder<List<LocalReportSummary>>(
          future: repository.listReports(session.user.uuid),
          builder: (context, snapshot) {
            if (!snapshot.hasData) {
              return const Center(child: CircularProgressIndicator());
            }
            final reports = snapshot.data!;
            if (reports.isEmpty) {
              return const Center(
                child: Padding(
                  padding: EdgeInsets.all(24),
                  child: Text(
                    'No authorised reports are available. Connect and refresh your offline data.',
                    textAlign: TextAlign.center,
                  ),
                ),
              );
            }
            return ListView.separated(
              padding: const EdgeInsets.all(16),
              itemCount: reports.length,
              separatorBuilder: (_, _) => const SizedBox(height: 8),
              itemBuilder: (context, index) {
                final report = reports[index];
                return Card(
                  child: ListTile(
                    minVerticalPadding: 16,
                    leading: const Icon(Icons.assignment_outlined),
                    title: Text('Report ${report.periodUuid}'),
                    subtitle: Text(
                      '${report.status.replaceAll('_', ' ')} · '
                      '${report.completionPercentage}% complete',
                    ),
                    trailing: const Icon(Icons.chevron_right),
                    onTap: () => Navigator.of(context).push(
                      MaterialPageRoute<void>(
                        builder: (_) => ReportSectionScreen(
                          session: session,
                          report: report,
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
}
