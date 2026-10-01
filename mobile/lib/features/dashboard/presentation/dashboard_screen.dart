import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/auth/auth_models.dart';
import '../../../core/auth/auth_providers.dart';
import '../../../core/sync/sync_providers.dart';
import '../../../core/localization/language_controller.dart';
import '../../../l10n/generated/app_localizations.dart';
import '../../reporting/data/reporting_providers.dart';
import '../../reporting/domain/reporting_models.dart';
import '../../reporting/presentation/report_list_screen.dart';
import '../../reporting/presentation/report_section_screen.dart';
import '../../validation/presentation/validation_workflow_screen.dart';
import '../../exploration/presentation/analytics_screen.dart';
import '../../exploration/presentation/location_directory_screen.dart';
import '../../exploration/presentation/profile_screen.dart';
import '../../exploration/presentation/photo_reports_screen.dart';
import '../data/dashboard_providers.dart';
import '../domain/dashboard_models.dart';

class DashboardScreen extends ConsumerStatefulWidget {
  const DashboardScreen({required this.session, super.key});
  final AuthSession session;
  @override
  ConsumerState<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends ConsumerState<DashboardScreen> {
  int revision = 0;
  @override
  Widget build(BuildContext context) {
    final strings = AppLocalizations.of(context)!;
    final connected =
        ref.watch(connectivityProvider).value ?? !widget.session.isOffline;
    return Scaffold(
      appBar: AppBar(
        title: const Text('TNK Insight'),
        actions: [
          PopupMenuButton<String>(
            tooltip: strings.language,
            icon: const Icon(Icons.language),
            onSelected: (code) => ref
                .read(languageControllerProvider.notifier)
                .select(code, widget.session),
            itemBuilder: (_) => [
              PopupMenuItem(value: 'en', child: Text(strings.english)),
              PopupMenuItem(value: 'fj', child: Text(strings.itaukei)),
            ],
          ),
          IconButton(
            tooltip: strings.signOut,
            onPressed: () => ref.read(authControllerProvider.notifier).logout(),
            icon: const Icon(Icons.logout),
          ),
        ],
      ),
      body: FutureBuilder<DashboardSnapshot>(
        key: ValueKey(revision),
        future: ref
            .read(dashboardRepositoryProvider.future)
            .then((repository) => repository.load(widget.session)),
        builder: (context, snapshot) {
          if (snapshot.connectionState != ConnectionState.done) {
            return const Center(child: CircularProgressIndicator());
          }
          if (!snapshot.hasData) {
            return Center(
              child: FilledButton.icon(
                onPressed: refresh,
                icon: const Icon(Icons.refresh),
                label: const Text('Retry dashboard'),
              ),
            );
          }
          return content(snapshot.data!, connected);
        },
      ),
    );
  }

  Widget content(DashboardSnapshot value, bool connected) {
    final strings = AppLocalizations.of(context)!;
    final report = value.report;
    final name = widget.session.user.fullName.isEmpty
        ? widget.session.user.username
        : widget.session.user.fullName;
    return RefreshIndicator(
      onRefresh: () async => refresh(),
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Text(
            strings.welcome(name),
            style: Theme.of(context).textTheme.headlineSmall,
          ),
          Text(
            widget.session.user.roles
                .map((role) => role.replaceAll('_', ' '))
                .join(', '),
          ),
          const SizedBox(height: 12),
          Card(
            child: ListTile(
              leading: Icon(
                connected && !value.isOffline
                    ? Icons.cloud_done_outlined
                    : Icons.cloud_off_outlined,
              ),
              title: Text(
                connected && !value.isOffline
                    ? strings.online
                    : strings.offlineData,
              ),
              subtitle: Text(
                '${value.location['village'] ?? 'No village'} · ${value.location['tikina'] ?? 'No Tikina'} · ${value.location['province'] ?? 'No province'}\n${value.periodLabel}',
              ),
            ),
          ),
          if (report != null)
            reportCard(report)
          else
            Card(
              child: ListTile(
                leading: const Icon(Icons.note_add_outlined),
                title: Text(strings.noCurrentReport),
              ),
            ),
          if (report != null) metricGrid(value),
          const SizedBox(height: 8),
          action(
            strings.continueReport,
            Icons.edit_note_outlined,
            report == null ? null : () => openReport(report),
          ),
          action(
            strings.startReport,
            Icons.add_circle_outline,
            connected ? startReport : null,
          ),
          action(
            strings.reviewIssues,
            Icons.fact_check_outlined,
            report == null ? null : () => reviewIssues(report),
          ),
          action(
            strings.synchronise,
            Icons.sync,
            connected ? synchronize : null,
          ),
          action(
            strings.viewPreviousReport,
            Icons.history,
            report?.previousReportUuid == null
                ? null
                : () => openPrevious(report!.previousReportUuid!),
          ),
          action(
            strings.viewVillageSummary,
            Icons.insights_outlined,
            value.indicators.isEmpty
                ? null
                : () => showIndicators(value.indicators),
          ),
          if (widget.session.user.can('analytics'))
            action(
              'Analytics',
              Icons.analytics_outlined,
              () => Navigator.push(
                context,
                MaterialPageRoute<void>(
                  builder: (_) => const AnalyticsScreen(),
                ),
              ),
            ),
          if (widget.session.user.can('locations'))
            action(
              'Location directory',
              Icons.account_tree_outlined,
              () => Navigator.push(
                context,
                MaterialPageRoute<void>(
                  builder: (_) => const LocationDirectoryScreen(),
                ),
              ),
            ),
          if (widget.session.user.can('photo_reports'))
            action(
              'Photo Reports',
              Icons.photo_library_outlined,
              () => Navigator.push(
                context,
                MaterialPageRoute<void>(
                  builder: (_) => const PhotoReportsScreen(),
                ),
              ),
            ),
          action(
            'Profile',
            Icons.person_outline,
            () => Navigator.push(
              context,
              MaterialPageRoute<void>(
                builder: (_) => ProfileScreen(session: widget.session),
              ),
            ),
          ),
          TextButton(
            onPressed: () => Navigator.of(context).push(
              MaterialPageRoute<void>(
                builder: (_) => ReportListScreen(session: widget.session),
              ),
            ),
            child: Text(strings.viewReports),
          ),
        ],
      ),
    );
  }

  Widget reportCard(LocalReportSummary report) => Card(
    child: Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                AppLocalizations.of(context)!.currentReport,
                style: Theme.of(context).textTheme.titleLarge,
              ),
              Chip(label: Text(report.status.replaceAll('_', ' '))),
            ],
          ),
          LinearProgressIndicator(value: report.completionPercentage / 100),
          const SizedBox(height: 8),
          Text(
            '${report.completionPercentage}% complete · Data quality ${report.dataQualityScore?.toStringAsFixed(0) ?? 'not scored'}',
          ),
        ],
      ),
    ),
  );

  Widget metricGrid(DashboardSnapshot value) => GridView.count(
    shrinkWrap: true,
    physics: const NeverScrollableScrollPhysics(),
    crossAxisCount:
        MediaQuery.sizeOf(context).width < 520 ||
            MediaQuery.textScalerOf(context).scale(1) > 1.3
        ? 1
        : 2,
    childAspectRatio:
        MediaQuery.sizeOf(context).width < 520 ||
            MediaQuery.textScalerOf(context).scale(1) > 1.3
        ? 3
        : 1.55,
    children: [
      metric('Issues', '${value.pendingIssues}', Icons.warning_amber_outlined),
      metric(
        'Pending sync',
        '${value.pendingSync}',
        Icons.sync_problem_outlined,
      ),
      metric(
        'Last sync',
        value.lastSuccessfulSync == null
            ? 'Never'
            : shortDate(value.lastSuccessfulSync!),
        Icons.schedule,
      ),
      metric(
        'Indicators',
        '${value.indicators.length}',
        Icons.analytics_outlined,
      ),
    ],
  );
  Widget metric(String label, String value, IconData icon) => Card(
    child: Padding(
      padding: const EdgeInsets.all(8),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(icon),
          Text(value, style: Theme.of(context).textTheme.titleLarge),
          Text(label),
        ],
      ),
    ),
  );
  Widget action(String label, IconData icon, VoidCallback? callback) => Padding(
    padding: const EdgeInsets.only(bottom: 8),
    child: SizedBox(
      height: 56,
      child: FilledButton.tonalIcon(
        onPressed: callback,
        icon: Icon(icon),
        label: Align(alignment: Alignment.centerLeft, child: Text(label)),
      ),
    ),
  );

  Future<void> openReport(LocalReportSummary report) async {
    await Navigator.of(context).push(
      MaterialPageRoute<void>(
        builder: (_) =>
            ReportSectionScreen(session: widget.session, report: report),
      ),
    );
    refresh();
  }

  Future<void> reviewIssues(LocalReportSummary report) async {
    final repository = await ref.read(reportingRepositoryProvider.future);
    final local = await repository.materializeReport(
      widget.session.user.uuid,
      report,
    );
    if (!mounted) return;
    await Navigator.of(context).push(
      MaterialPageRoute<void>(
        builder: (_) => ValidationWorkflowScreen(
          session: widget.session,
          reportUuid: report.uuid,
          reportLocalUuid: local,
        ),
      ),
    );
    refresh();
  }

  Future<void> openPrevious(String uuid) async {
    final repository = await ref.read(dashboardRepositoryProvider.future);
    final result = await repository.load(
      await freshSession(),
      reportUuid: uuid,
    );
    if (mounted && result.report != null) await openReport(result.report!);
  }

  Future<void> synchronize() async {
    await ref.read(syncControllerProvider.notifier).synchronize();
    refresh();
  }

  Future<AuthSession> freshSession() =>
      ref.read(authControllerProvider.notifier).ensureFreshSession();

  Future<void> startReport() async {
    final languageCode = Localizations.localeOf(context).languageCode;
    final repository = await ref.read(dashboardRepositoryProvider.future);
    final villages = await repository.villages(
      widget.session.user.uuid,
      languageCode: languageCode,
    );
    final periods = await repository.periods(widget.session.user.uuid);
    if (!mounted || villages.isEmpty || periods.isEmpty) return;
    var village = villages.first.uuid;
    var period = periods.first.uuid;
    var province = villages.first.provinceUuid;
    var tikina = villages.first.tikinaUuid;
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => StatefulBuilder(
        builder: (context, update) => AlertDialog(
          title: const Text('Start quarterly report'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              DropdownButtonFormField<String>(
                initialValue: province,
                decoration: const InputDecoration(labelText: 'Province'),
                items:
                    {
                          for (final item in villages)
                            item.provinceUuid: item.province,
                        }.entries
                        .map(
                          (item) => DropdownMenuItem(
                            value: item.key,
                            child: Text(item.value),
                          ),
                        )
                        .toList(),
                onChanged: (value) => update(() {
                  province = value!;
                  final selected = villages.firstWhere(
                    (item) => item.provinceUuid == province,
                  );
                  tikina = selected.tikinaUuid;
                  village = selected.uuid;
                }),
              ),
              const SizedBox(height: 12),
              DropdownButtonFormField<String>(
                key: ValueKey(province),
                initialValue: tikina,
                decoration: const InputDecoration(labelText: 'Tikina'),
                items:
                    {
                          for (final item in villages.where(
                            (item) => item.provinceUuid == province,
                          ))
                            item.tikinaUuid: item.tikina,
                        }.entries
                        .map(
                          (item) => DropdownMenuItem(
                            value: item.key,
                            child: Text(item.value),
                          ),
                        )
                        .toList(),
                onChanged: (value) => update(() {
                  tikina = value!;
                  village = villages
                      .firstWhere((item) => item.tikinaUuid == tikina)
                      .uuid;
                }),
              ),
              const SizedBox(height: 12),
              DropdownButtonFormField<String>(
                key: ValueKey(tikina),
                initialValue: village,
                decoration: const InputDecoration(labelText: 'Village'),
                items: villages
                    .where((item) => item.tikinaUuid == tikina)
                    .map(
                      (item) => DropdownMenuItem(
                        value: item.uuid,
                        child: Text(item.label),
                      ),
                    )
                    .toList(),
                onChanged: (value) => update(() => village = value!),
              ),
              const SizedBox(height: 12),
              DropdownButtonFormField<String>(
                initialValue: period,
                decoration: const InputDecoration(
                  labelText: 'Reporting period',
                ),
                items: periods
                    .map(
                      (item) => DropdownMenuItem(
                        value: item.uuid,
                        child: Text(item.label),
                      ),
                    )
                    .toList(),
                onChanged: (value) => update(() => period = value!),
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context, false),
              child: const Text('Cancel'),
            ),
            FilledButton(
              onPressed: () => Navigator.pop(context, true),
              child: const Text('Start'),
            ),
          ],
        ),
      ),
    );
    if (confirmed != true) return;
    try {
      await repository.startReport(await freshSession(), village, period);
      await ref.read(syncControllerProvider.notifier).synchronize();
      refresh();
    } on Object {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text(
              'The report could not be started. It may already exist.',
            ),
          ),
        );
      }
    }
  }

  void showIndicators(
    List<VillageIndicator> indicators,
  ) => showModalBottomSheet<void>(
    context: context,
    isScrollControlled: true,
    builder: (context) => DraggableScrollableSheet(
      expand: false,
      builder: (context, controller) => ListView(
        controller: controller,
        padding: const EdgeInsets.all(16),
        children: [
          Text(
            AppLocalizations.of(context)!.villageSummary,
            style: Theme.of(context).textTheme.headlineSmall,
          ),
          for (final item in indicators)
            ListTile(
              title: Text(
                item.nameFor(Localizations.localeOf(context).languageCode),
              ),
              subtitle: Text(
                '${item.status.replaceAll('_', ' ')} · Quality ${item.qualityRating}',
              ),
              trailing: Text(
                item.value == null ? 'No data' : '${item.value} ${item.unit}',
                textAlign: TextAlign.end,
              ),
            ),
        ],
      ),
    ),
  );
  String shortDate(DateTime value) =>
      '${value.day}/${value.month}/${value.year}';
  void refresh() {
    if (mounted) setState(() => revision++);
  }
}
