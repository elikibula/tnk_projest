import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/auth/auth_models.dart';
import '../../../core/auth/auth_providers.dart';
import '../../../core/sync/sync_providers.dart';
import '../data/validation_providers.dart';
import '../domain/validation_models.dart';

class ValidationWorkflowScreen extends ConsumerStatefulWidget {
  const ValidationWorkflowScreen({
    required this.session,
    required this.reportUuid,
    required this.reportLocalUuid,
    super.key,
  });
  final AuthSession session;
  final String reportUuid;
  final String reportLocalUuid;

  @override
  ConsumerState<ValidationWorkflowScreen> createState() =>
      _ValidationWorkflowScreenState();
}

class _ValidationWorkflowScreenState
    extends ConsumerState<ValidationWorkflowScreen> {
  ValidationSnapshot? _snapshot;
  bool _declared = false;
  bool _busy = false;
  String? _safeError;

  @override
  void initState() {
    super.initState();
    Future.microtask(_load);
  }

  @override
  Widget build(BuildContext context) {
    final report = _snapshot?.report;
    final returned = report?['returned_review'] as Map?;
    return Scaffold(
      appBar: AppBar(title: const Text('Validation and submission')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          if (returned != null)
            Card(
              color: Theme.of(context).colorScheme.errorContainer,
              child: ListTile(
                leading: const Icon(Icons.assignment_return_outlined),
                title: const Text('Returned for Correction'),
                subtitle: Text(
                  '${returned['comment']}\nReviewer: ${returned['reviewer']}\nReturned: ${returned['returned_at']}',
                ),
              ),
            ),
          if (_snapshot == null && _safeError == null)
            const Center(
              child: Padding(
                padding: EdgeInsets.all(32),
                child: CircularProgressIndicator(),
              ),
            ),
          if (_safeError != null)
            Card(
              child: ListTile(
                leading: const Icon(Icons.info_outline),
                title: Text(_safeError!),
              ),
            ),
          if (_snapshot != null) ...[
            Text(
              '${_snapshot!.issues.length} unresolved issue(s)',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 8),
            if (_snapshot!.issues.isEmpty)
              const Card(
                child: ListTile(
                  leading: Icon(Icons.check_circle_outline),
                  title: Text('No unresolved server issues'),
                ),
              ),
            for (final issue in _snapshot!.issues)
              Card(
                child: ListTile(
                  leading: Icon(
                    issue.blocking
                        ? Icons.block_outlined
                        : Icons.warning_amber_outlined,
                  ),
                  title: Text(issue.message),
                  subtitle: Text(
                    '${issue.severity.toUpperCase()} · ${issue.section}${issue.fieldName.isEmpty ? '' : ' · ${issue.fieldName}'}',
                  ),
                ),
              ),
            CheckboxListTile(
              contentPadding: EdgeInsets.zero,
              value: _declared,
              onChanged: _busy
                  ? null
                  : (value) => setState(() => _declared = value ?? false),
              title: const Text('Final declaration'),
              subtitle: const Text(
                'I declare this report complete and accurate to the best of my knowledge.',
              ),
            ),
            const SizedBox(height: 8),
            FilledButton.tonalIcon(
              onPressed: _busy ? null : _validate,
              icon: const Icon(Icons.fact_check_outlined),
              label: const Text('Run server validation'),
            ),
            const SizedBox(height: 8),
            FilledButton.icon(
              onPressed:
                  _busy ||
                      !_declared ||
                      _snapshot!.issues.any((issue) => issue.blocking)
                  ? null
                  : _submit,
              icon: const Icon(Icons.send_outlined),
              label: Text(_busy ? 'Working…' : 'Synchronize and submit'),
            ),
            const Padding(
              padding: EdgeInsets.only(top: 12),
              child: Text(
                'Submission requires a connection. The report remains unsubmitted until the server confirms its status.',
              ),
            ),
          ],
        ],
      ),
    );
  }

  Future<AuthSession> _freshSession() =>
      ref.read(authControllerProvider.notifier).ensureFreshSession();

  Future<void> _load() async {
    try {
      final repository = await ref.read(validationRepositoryProvider.future);
      final result = await repository.load(
        await _freshSession(),
        widget.reportUuid,
      );
      if (mounted) {
        setState(() {
          _snapshot = result;
          _safeError = null;
        });
      }
    } on Object {
      if (mounted) {
        setState(
          () => _safeError =
              'Connect to refresh authoritative validation results.',
        );
      }
    }
  }

  Future<void> _validate() async {
    setState(() {
      _busy = true;
      _safeError = null;
    });
    try {
      final repository = await ref.read(validationRepositoryProvider.future);
      final result = await repository.validate(
        await _freshSession(),
        widget.reportUuid,
      );
      if (mounted) {
        setState(() => _snapshot = result);
      }
    } on Object {
      if (mounted) {
        setState(
          () => _safeError = 'Server validation could not be confirmed.',
        );
      }
    } finally {
      if (mounted) {
        setState(() => _busy = false);
      }
    }
  }

  Future<void> _submit() async {
    setState(() {
      _busy = true;
      _safeError = null;
    });
    try {
      await ref.read(syncControllerProvider.notifier).synchronize();
      if (ref.read(syncControllerProvider).hasError) {
        throw const SubmissionNotConfirmed();
      }
      final session = await _freshSession();
      final repository = await ref.read(validationRepositoryProvider.future);
      if (await repository.unsyncedAttachments(
            session.user.uuid,
            widget.reportLocalUuid,
          ) >
          0) {
        throw const SubmissionNotConfirmed(
          'Evidence is still waiting for upload. Submission not confirmed.',
        );
      }
      final report = await repository.submit(session, widget.reportUuid);
      if (report['status'] != 'submitted') {
        final refreshed = await repository.validate(session, widget.reportUuid);
        if (mounted) {
          setState(() {
            _snapshot = refreshed;
            _safeError =
                'Resolve the critical server issues before submission.';
          });
        }
        return;
      }
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Submitted and confirmed by TNK Insight.'),
          ),
        );
        Navigator.pop(context);
      }
    } on SubmissionNotConfirmed catch (error) {
      if (mounted) {
        setState(() => _safeError = error.message);
      }
    } on Object {
      if (mounted) {
        setState(() => _safeError = 'Submission not confirmed.');
      }
    } finally {
      if (mounted) {
        setState(() => _busy = false);
      }
    }
  }
}
