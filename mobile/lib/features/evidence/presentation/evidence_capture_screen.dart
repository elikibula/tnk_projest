import 'dart:io';

import 'package:file_selector/file_selector.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:geolocator/geolocator.dart';
import 'package:image_picker/image_picker.dart';

import '../../../core/auth/auth_models.dart';
import '../data/evidence_providers.dart';
import '../domain/evidence_models.dart';

class EvidenceCaptureScreen extends ConsumerStatefulWidget {
  const EvidenceCaptureScreen({
    required this.session,
    required this.reportLocalUuid,
    required this.editable,
    super.key,
  });
  final AuthSession session;
  final String reportLocalUuid;
  final bool editable;

  @override
  ConsumerState<EvidenceCaptureScreen> createState() =>
      _EvidenceCaptureScreenState();
}

class _EvidenceCaptureScreenState extends ConsumerState<EvidenceCaptureScreen> {
  final _title = TextEditingController();
  final _description = TextEditingController();
  File? _file;
  String _mediaType = 'image/jpeg';
  bool _compress = true;
  EvidenceLocation? _location;
  bool _busy = false;

  @override
  void dispose() {
    _title.dispose();
    _description.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Evidence')),
    body: ListView(
      padding: const EdgeInsets.all(16),
      children: [
        if (!widget.editable)
          const Card(
            child: ListTile(
              leading: Icon(Icons.lock_outline),
              title: Text('Evidence is read only for this report.'),
            ),
          ),
        TextField(
          controller: _title,
          enabled: widget.editable,
          decoration: const InputDecoration(labelText: 'Evidence title'),
        ),
        const SizedBox(height: 12),
        TextField(
          controller: _description,
          enabled: widget.editable,
          maxLines: 3,
          decoration: const InputDecoration(
            labelText: 'Description (optional)',
          ),
        ),
        const SizedBox(height: 16),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: [
            FilledButton.tonalIcon(
              onPressed: widget.editable
                  ? () => _pickImage(ImageSource.camera)
                  : null,
              icon: const Icon(Icons.camera_alt_outlined),
              label: const Text('Camera'),
            ),
            FilledButton.tonalIcon(
              onPressed: widget.editable
                  ? () => _pickImage(ImageSource.gallery)
                  : null,
              icon: const Icon(Icons.photo_library_outlined),
              label: const Text('Gallery'),
            ),
            FilledButton.tonalIcon(
              onPressed: widget.editable ? _pickDocument : null,
              icon: const Icon(Icons.attach_file),
              label: const Text('Document'),
            ),
          ],
        ),
        if (_file != null)
          SwitchListTile(
            contentPadding: EdgeInsets.zero,
            title: Text(_file!.path.split(Platform.pathSeparator).last),
            subtitle: const Text(
              'Large photos are reduced to 2048 px at 85% quality.',
            ),
            value: _compress,
            onChanged: _mediaType.startsWith('image/')
                ? (value) => setState(() => _compress = value)
                : null,
          ),
        const Divider(height: 32),
        ListTile(
          contentPadding: EdgeInsets.zero,
          leading: const Icon(Icons.location_on_outlined),
          title: Text(
            _location == null
                ? 'No GPS attached'
                : '${_location!.latitude.toStringAsFixed(6)}, ${_location!.longitude.toStringAsFixed(6)}',
          ),
          subtitle: Text(
            _location == null
                ? 'Optional. Location is requested only when you tap Capture GPS.'
                : 'Accuracy ${_location!.accuracyMetres.toStringAsFixed(1)} m',
          ),
          trailing: TextButton(
            onPressed: widget.editable ? _captureLocation : null,
            child: const Text('Capture GPS'),
          ),
        ),
        const SizedBox(height: 20),
        FilledButton.icon(
          onPressed: widget.editable && !_busy ? _queue : null,
          icon: const Icon(Icons.lock_outline),
          label: Text(_busy ? 'Protecting…' : 'Save to encrypted upload queue'),
        ),
        const Padding(
          padding: EdgeInsets.only(top: 12),
          child: Text(
            'The protected copy stays on this device until a confirmed upload. Failed uploads can be retried without affecting the report.',
          ),
        ),
      ],
    ),
  );

  Future<void> _pickImage(ImageSource source) async {
    final picked = await ImagePicker().pickImage(source: source);
    if (picked != null) {
      setState(() {
        _file = File(picked.path);
        _mediaType = picked.mimeType ?? 'image/jpeg';
        _compress = true;
      });
    }
  }

  Future<void> _pickDocument() async {
    const group = XTypeGroup(
      label: 'TNK evidence documents',
      extensions: ['pdf', 'docx', 'xlsx'],
    );
    final result = await openFile(acceptedTypeGroups: const [group]);
    final path = result?.path;
    if (path == null) return;
    final extension = path.split('.').last.toLowerCase();
    setState(() {
      _file = File(path);
      _compress = false;
      _mediaType =
          {
            'pdf': 'application/pdf',
            'docx':
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'xlsx':
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
          }[extension] ??
          'application/octet-stream';
    });
  }

  Future<void> _captureLocation() async {
    if (!await Geolocator.isLocationServiceEnabled()) {
      _message('Location services are off. You can continue without GPS.');
      return;
    }
    var permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
    }
    if (permission == LocationPermission.denied ||
        permission == LocationPermission.deniedForever) {
      _message(
        'Location permission was not granted. You can continue without GPS.',
      );
      return;
    }
    final value = await Geolocator.getCurrentPosition(
      locationSettings: const LocationSettings(
        accuracy: LocationAccuracy.high,
        timeLimit: Duration(seconds: 20),
      ),
    );
    setState(
      () => _location = EvidenceLocation(
        latitude: value.latitude,
        longitude: value.longitude,
        accuracyMetres: value.accuracy,
        capturedAt: value.timestamp,
      ),
    );
  }

  Future<void> _queue() async {
    if (_file == null || _title.text.trim().isEmpty) {
      _message('Choose a file and enter a title.');
      return;
    }
    setState(() => _busy = true);
    try {
      final repository = await ref.read(evidenceRepositoryProvider.future);
      await repository.queue(
        ownerUuid: widget.session.user.uuid,
        reportLocalUuid: widget.reportLocalUuid,
        source: _file!,
        mediaType: _mediaType,
        compressImage: _compress,
        metadata: EvidenceMetadata(
          title: _title.text.trim(),
          documentType: _mediaType.startsWith('image/') ? 'photo' : 'document',
          description: _description.text.trim(),
          location: _location,
        ),
      );
      if (mounted) {
        _message('Evidence saved securely and queued for upload.');
        Navigator.pop(context);
      }
    } on Object {
      if (mounted) _message('Evidence could not be protected on this device.');
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  void _message(String value) => ScaffoldMessenger.of(
    context,
  ).showSnackBar(SnackBar(content: Text(value)));
}
