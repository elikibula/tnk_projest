import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/auth/auth_models.dart';
import '../data/reporting_providers.dart';
import '../domain/reporting_models.dart';
import 'report_section_screen.dart';

class ReportListScreen extends ConsumerStatefulWidget {
  const ReportListScreen({
    required this.session,
    super.key,
    this.villageUuid,
    this.title = 'TNK reports',
  });
  final AuthSession session;
  final String? villageUuid;
  final String title;
  @override
  ConsumerState<ReportListScreen> createState() => _ReportListState();
}

class _ReportListState extends ConsumerState<ReportListScreen> {
  static const _filters = <String, String>{
    'all': 'All',
    'draft': 'Draft',
    'submitted': 'Submitted',
    'returned_to_village': 'Returned',
    'approved': 'Approved',
    'rejected': 'Rejected',
  };
  String status = 'all';
  int revision = 0;

  @override
  Widget build(BuildContext context) {
    final repository = ref.watch(reportingRepositoryProvider);
    return Scaffold(
      appBar: AppBar(title: Text(widget.title)),
      body: repository.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, stackTrace) => const Center(
          child: Text('Reports could not be opened from this device.'),
        ),
        data: (repository) => FutureBuilder<List<LocalReportSummary>>(
          key: ValueKey(revision),
          future: repository.listReports(widget.session.user.uuid),
          builder: (context, snapshot) {
            if (!snapshot.hasData) {
              return const Center(child: CircularProgressIndicator());
            }
            final allReports = snapshot.data!
                .where(
                  (item) =>
                      widget.villageUuid == null ||
                      item.villageUuid == widget.villageUuid,
                )
                .toList();
            final reports = status == 'all'
                ? allReports
                : allReports.where((item) => item.status == status).toList();
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
            return RefreshIndicator(
              onRefresh: () async => setState(() => revision++),
              child: ListView.separated(
                padding: const EdgeInsets.all(16),
                itemCount: reports.length + 1,
                separatorBuilder: (_, _) => const SizedBox(height: 8),
                itemBuilder: (context, index) {
                  if (index == 0) {
                    return SingleChildScrollView(
                      scrollDirection: Axis.horizontal,
                      child: Row(
                        children: [
                          for (final item in _filters.entries)
                            Padding(
                              padding: const EdgeInsets.only(right: 8),
                              child: FilterChip(
                                selected: status == item.key,
                                label: Text(item.value),
                                onSelected: (_) =>
                                    setState(() => status = item.key),
                              ),
                            ),
                        ],
                      ),
                    );
                  }
                  final report = reports[index - 1];
                  return Card(
                    child: ListTile(
                      minVerticalPadding: 16,
                      leading: const Icon(Icons.assignment_outlined),
                      title: Text(
                        report.periodLabel.isEmpty
                            ? 'TNK report'
                            : report.periodLabel,
                      ),
                      subtitle: Text(
                        '${report.villageName.isEmpty ? report.villageUuid : report.villageName}${report.tikinaName.isEmpty ? '' : ' · ${report.tikinaName}'}\n'
                        '${report.statusLabel.isEmpty ? report.status.replaceAll('_', ' ') : report.statusLabel} · ${report.completionPercentage}% complete'
                        '${report.updatedAt == null ? '' : '\nUpdated ${report.updatedAt!.toLocal().day}/${report.updatedAt!.toLocal().month}/${report.updatedAt!.toLocal().year}'}',
                      ),
                      trailing: const Icon(Icons.chevron_right),
                      onTap: () => Navigator.of(context).push(
                        MaterialPageRoute<void>(
                          builder: (_) => ReportSectionScreen(
                            session: widget.session,
                            report: report,
                          ),
                        ),
                      ),
                    ),
                  );
                },
              ),
            );
          },
        ),
      ),
    );
  }
}
