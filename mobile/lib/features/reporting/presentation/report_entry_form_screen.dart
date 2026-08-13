import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/auth/auth_models.dart';
import '../data/reporting_providers.dart';
import '../domain/reporting_models.dart';

class ReportEntryFormScreen extends ConsumerStatefulWidget {
  const ReportEntryFormScreen({
    required this.session,
    required this.reportLocalUuid,
    required this.sectionCode,
    required this.definition,
    required this.editable,
    this.entry,
    super.key,
  });

  final AuthSession session;
  final String reportLocalUuid;
  final String sectionCode;
  final ReportEntryDefinition definition;
  final LocalReportEntry? entry;
  final bool editable;

  @override
  ConsumerState<ReportEntryFormScreen> createState() =>
      _ReportEntryFormScreenState();
}

class _ReportEntryFormScreenState extends ConsumerState<ReportEntryFormScreen> {
  final _formKey = GlobalKey<FormState>();
  final _controllers = <String, TextEditingController>{};
  final _values = <String, dynamic>{};
  Timer? _autosaveTimer;
  String? _localUuid;
  bool _saving = false;
  DateTime? _savedAt;

  @override
  void initState() {
    super.initState();
    _localUuid = widget.entry?.localUuid;
    _values.addAll(widget.entry?.values ?? const {});
    for (final field in widget.definition.fields) {
      if (field.type case ReportFieldType.boolean || ReportFieldType.choice) {
        continue;
      }
      final controller = TextEditingController(
        text: _values[field.name]?.toString() ?? '',
      );
      controller.addListener(() {
        _values[field.name] = _typedValue(field, controller.text);
        _scheduleAutosave();
      });
      _controllers[field.name] = controller;
    }
  }

  @override
  void dispose() {
    _autosaveTimer?.cancel();
    for (final controller in _controllers.values) {
      controller.dispose();
    }
    super.dispose();
  }

  dynamic _typedValue(ReportFieldDefinition field, String value) {
    if (value.isEmpty) return null;
    return switch (field.type) {
      ReportFieldType.integer => int.tryParse(value) ?? value,
      ReportFieldType.decimal => double.tryParse(value) ?? value,
      _ => value,
    };
  }

  void _scheduleAutosave() {
    if (!widget.editable) return;
    _autosaveTimer?.cancel();
    _autosaveTimer = Timer(const Duration(milliseconds: 700), _saveDraft);
    if (mounted) setState(() => _savedAt = null);
  }

  Future<void> _saveDraft() async {
    if (!widget.editable || _saving) return;
    setState(() => _saving = true);
    try {
      final repository = await ref.read(reportingRepositoryProvider.future);
      _localUuid = await repository.saveEntry(
        owner: widget.session.user.uuid,
        reportLocalUuid: widget.reportLocalUuid,
        sectionCode: widget.sectionCode,
        entryType: widget.definition.key,
        values: Map<String, dynamic>.from(_values),
        localUuid: _localUuid,
      );
      if (mounted) setState(() => _savedAt = DateTime.now());
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  Future<void> _saveAndClose() async {
    if (!_formKey.currentState!.validate()) return;
    _autosaveTimer?.cancel();
    await _saveDraft();
    if (mounted) Navigator.of(context).pop();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(widget.definition.label)),
      body: SafeArea(
        child: Form(
          key: _formKey,
          child: ListView(
            padding: const EdgeInsets.all(16),
            children: [
              Semantics(
                liveRegion: true,
                child: ListTile(
                  contentPadding: EdgeInsets.zero,
                  leading: Icon(_saving ? Icons.sync : Icons.save_outlined),
                  title: Text(
                    _saving
                        ? 'Saving on device…'
                        : _savedAt == null
                        ? 'Changes save automatically'
                        : 'Saved on device',
                  ),
                ),
              ),
              for (final field in widget.definition.fields) ...[
                const SizedBox(height: 12),
                _field(field),
              ],
              const SizedBox(height: 24),
              if (widget.editable)
                FilledButton.icon(
                  onPressed: _saving ? null : _saveAndClose,
                  icon: const Icon(Icons.save_outlined),
                  label: const Text('Save and close'),
                ),
              if (widget.editable &&
                  widget.entry != null &&
                  widget.definition.allowDelete) ...[
                const SizedBox(height: 12),
                OutlinedButton.icon(
                  onPressed: _saving ? null : _delete,
                  icon: const Icon(Icons.delete_outline),
                  label: const Text('Delete entry'),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _field(ReportFieldDefinition field) {
    if (field.type == ReportFieldType.boolean) {
      return SwitchListTile(
        contentPadding: EdgeInsets.zero,
        title: Text(field.label),
        value: _values[field.name] as bool? ?? false,
        onChanged: widget.editable
            ? (value) {
                setState(() => _values[field.name] = value);
                _scheduleAutosave();
              }
            : null,
      );
    }
    if (field.type == ReportFieldType.choice) {
      return DropdownButtonFormField<String>(
        initialValue: _values[field.name]?.toString(),
        decoration: InputDecoration(labelText: field.label),
        items: field.choices
            .map(
              (choice) => DropdownMenuItem(
                value: choice.value,
                child: Text(choice.label),
              ),
            )
            .toList(growable: false),
        onChanged: widget.editable
            ? (value) {
                setState(() => _values[field.name] = value);
                _scheduleAutosave();
              }
            : null,
        validator: (value) => field.required && value == null
            ? '${field.label} is required.'
            : null,
      );
    }
    final isDate =
        field.type == ReportFieldType.date ||
        field.type == ReportFieldType.datetime;
    return TextFormField(
      controller: _controllers[field.name],
      enabled: widget.editable,
      readOnly: isDate,
      maxLength: field.maxLength,
      keyboardType: switch (field.type) {
        ReportFieldType.integer => TextInputType.number,
        ReportFieldType.decimal => const TextInputType.numberWithOptions(
          decimal: true,
        ),
        _ => TextInputType.text,
      },
      inputFormatters: switch (field.type) {
        ReportFieldType.integer => [
          FilteringTextInputFormatter.allow(RegExp(r'^-?\d*')),
        ],
        ReportFieldType.decimal => [
          FilteringTextInputFormatter.allow(RegExp(r'^-?\d*\.?\d*')),
        ],
        _ => null,
      },
      minLines: field.type == ReportFieldType.text ? 1 : null,
      maxLines: field.type == ReportFieldType.text ? 3 : 1,
      decoration: InputDecoration(
        labelText: field.label,
        suffixIcon: isDate ? const Icon(Icons.calendar_today_outlined) : null,
      ),
      onTap: isDate && widget.editable ? () => _pickDate(field) : null,
      validator: (value) {
        if (field.required && (value == null || value.trim().isEmpty)) {
          return '${field.label} is required.';
        }
        if (field.type == ReportFieldType.integer &&
            value!.isNotEmpty &&
            int.tryParse(value) == null) {
          return 'Enter a whole number.';
        }
        if (field.type == ReportFieldType.decimal &&
            value!.isNotEmpty &&
            double.tryParse(value) == null) {
          return 'Enter a number.';
        }
        return null;
      },
    );
  }

  Future<void> _pickDate(ReportFieldDefinition field) async {
    final current = DateTime.tryParse(_controllers[field.name]!.text);
    final chosen = await showDatePicker(
      context: context,
      initialDate: current ?? DateTime.now(),
      firstDate: DateTime(1900),
      lastDate: DateTime.now().add(const Duration(days: 3650)),
    );
    if (chosen != null) {
      _controllers[field.name]!.text = chosen
          .toIso8601String()
          .split('T')
          .first;
    }
  }

  Future<void> _delete() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete this entry?'),
        content: const Text('The change will be saved on this device.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Cancel'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('Delete'),
          ),
        ],
      ),
    );
    if (confirmed != true) return;
    final repository = await ref.read(reportingRepositoryProvider.future);
    await repository.deleteEntry(
      owner: widget.session.user.uuid,
      reportLocalUuid: widget.reportLocalUuid,
      localUuid: widget.entry!.localUuid,
    );
    if (mounted) Navigator.pop(context);
  }
}
