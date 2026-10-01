import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/auth/auth_models.dart';
import '../data/reporting_providers.dart';
import '../domain/reporting_models.dart';
import 'report_entry_form_screen.dart';
import '../../evidence/presentation/evidence_capture_screen.dart';
import '../../validation/presentation/validation_workflow_screen.dart';
import 'data_type_style.dart';

class SectionEntriesScreen extends ConsumerStatefulWidget {
  const SectionEntriesScreen({
    required this.session,
    required this.reportLocalUuid,
    required this.section,
    required this.editable,
    super.key,
  });

  final AuthSession session;
  final String reportLocalUuid;
  final ReportSectionDefinition section;
  final bool editable;

  @override
  ConsumerState<SectionEntriesScreen> createState() =>
      _SectionEntriesScreenState();
}

class _SectionEntriesScreenState extends ConsumerState<SectionEntriesScreen> {
  int _revision = 0;

  @override
  Widget build(BuildContext context) {
    final repository = ref.watch(reportingRepositoryProvider);
    return Scaffold(
      appBar: AppBar(title: Text(widget.section.label)),
      body: repository.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, stackTrace) =>
            const Center(child: Text('Entries could not be opened.')),
        data: (repository) => FutureBuilder<List<LocalReportEntry>>(
          key: ValueKey(_revision),
          future: repository.listEntries(
            widget.session.user.uuid,
            widget.reportLocalUuid,
            widget.section.code,
          ),
          builder: (context, snapshot) {
            if (!snapshot.hasData) {
              return const Center(child: CircularProgressIndicator());
            }
            final entries = snapshot.data!;
            return ListView(
              padding: const EdgeInsets.all(16),
              children: [
                if (widget.section.code == 'evidence_declarations')
                  Card(
                    child: ListTile(
                      leading: const Icon(Icons.add_a_photo_outlined),
                      title: const Text('Capture or attach evidence'),
                      subtitle: const Text(
                        'Photos, documents, and optional GPS',
                      ),
                      trailing: const Icon(Icons.chevron_right),
                      onTap: () => Navigator.of(context).push(
                        MaterialPageRoute<void>(
                          builder: (_) => EvidenceCaptureScreen(
                            session: widget.session,
                            reportLocalUuid: widget.reportLocalUuid,
                            editable: widget.editable,
                          ),
                        ),
                      ),
                    ),
                  ),
                if (widget.section.code == 'validation_submission')
                  Card(
                    child: ListTile(
                      leading: const Icon(Icons.fact_check_outlined),
                      title: const Text('Validate and submit report'),
                      subtitle: const Text(
                        'Server issues, declaration, and confirmed submission',
                      ),
                      trailing: const Icon(Icons.chevron_right),
                      onTap: () async {
                        final report = await repository.reportByLocalUuid(
                          widget.session.user.uuid,
                          widget.reportLocalUuid,
                        );
                        if (!context.mounted || report?.serverUuid == null) {
                          return;
                        }
                        await Navigator.of(context).push(
                          MaterialPageRoute<void>(
                            builder: (_) => ValidationWorkflowScreen(
                              session: widget.session,
                              reportUuid: report!.serverUuid!,
                              reportLocalUuid: widget.reportLocalUuid,
                            ),
                          ),
                        );
                      },
                    ),
                  ),
                if (!widget.editable)
                  const Card(
                    child: ListTile(
                      leading: Icon(Icons.lock_outline),
                      title: Text('Read only'),
                      subtitle: Text(
                        'Only draft or returned reports can be edited.',
                      ),
                    ),
                  ),
                for (final definition in widget.section.entries) ...[
                  Padding(
                    padding: const EdgeInsets.fromLTRB(4, 20, 4, 8),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              DataTypeLabel(definition.dataType),
                              const SizedBox(height: 7),
                              Text(
                                definition.label,
                                style: Theme.of(context).textTheme.titleMedium,
                              ),
                            ],
                          ),
                        ),
                        if (widget.editable && definition.allowCreate)
                          IconButton(
                            tooltip: 'Add ${definition.label}',
                            onPressed: () => _openForm(definition, null),
                            icon: const Icon(Icons.add_circle_outline),
                          ),
                      ],
                    ),
                  ),
                  for (final entry in entries.where(
                    (value) => value.entryType == definition.key,
                  ))
                    DataTypeCard(
                      dataType: definition.dataType,
                      child: ListTile(
                        leading: const Icon(Icons.edit_note_outlined),
                        title: Text(_entryTitle(definition, entry)),
                        subtitle: Text(
                          '${entry.syncStatus.replaceAll('_', ' ')} · Saved on device',
                        ),
                        trailing: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            if (definition.supportsPhotos &&
                                entry.serverUuid != null)
                              IconButton(
                                tooltip: 'Photo evidence',
                                icon: const Icon(Icons.add_a_photo_outlined),
                                onPressed: () => Navigator.push(
                                  context,
                                  MaterialPageRoute<void>(
                                    builder: (_) => EvidenceCaptureScreen(
                                      session: widget.session,
                                      reportLocalUuid: widget.reportLocalUuid,
                                      editable: widget.editable,
                                      sectionCode: widget.section.code,
                                      entryKey: definition.key,
                                      recordIdentifier: entry.serverUuid,
                                    ),
                                  ),
                                ),
                              ),
                            const Icon(Icons.chevron_right),
                          ],
                        ),
                        onTap: () => _openForm(definition, entry),
                      ),
                    ),
                ],
              ],
            );
          },
        ),
      ),
    );
  }

  String _entryTitle(ReportEntryDefinition definition, LocalReportEntry entry) {
    final first = definition.fields
        .map((field) => entry.values[field.name])
        .where((value) => value != null && value.toString().isNotEmpty)
        .firstOrNull;
    return first?.toString() ?? definition.label;
  }

  Future<void> _openForm(
    ReportEntryDefinition definition,
    LocalReportEntry? entry,
  ) async {
    await Navigator.of(context).push(
      MaterialPageRoute<void>(
        builder: (_) => ReportEntryFormScreen(
          session: widget.session,
          reportLocalUuid: widget.reportLocalUuid,
          sectionCode: widget.section.code,
          definition: definition,
          entry: entry,
          editable: widget.editable,
        ),
      ),
    );
    if (mounted) setState(() => _revision++);
  }
}
