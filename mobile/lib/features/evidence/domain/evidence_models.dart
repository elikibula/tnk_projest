class EvidenceLocation {
  const EvidenceLocation({
    required this.latitude,
    required this.longitude,
    required this.accuracyMetres,
    required this.capturedAt,
  });
  final double latitude;
  final double longitude;
  final double accuracyMetres;
  final DateTime capturedAt;

  Map<String, dynamic> toJson() => {
    'latitude': latitude,
    'longitude': longitude,
    'location_accuracy_metres': accuracyMetres,
    'captured_at': capturedAt.toUtc().toIso8601String(),
  };
}

class EvidenceMetadata {
  const EvidenceMetadata({
    required this.title,
    required this.documentType,
    this.description = '',
    this.confidentialityLevel = 'restricted',
    this.location,
    this.capturedAt,
    this.sectionCode,
    this.entryKey,
    this.recordIdentifier,
    this.stage,
  });
  final String title;
  final String documentType;
  final String description;
  final String confidentialityLevel;
  final EvidenceLocation? location;
  final DateTime? capturedAt;
  final String? sectionCode;
  final String? entryKey;
  final String? recordIdentifier;
  final String? stage;

  Map<String, dynamic> toJson() => {
    'title': title,
    'document_type': documentType,
    'description': description,
    'confidentiality_level': confidentialityLevel,
    if (location != null) ...location!.toJson(),
    if (location == null && capturedAt != null)
      'captured_at': capturedAt!.toUtc().toIso8601String(),
    if (sectionCode != null) 'section_code': sectionCode,
    if (entryKey != null) 'entry_key': entryKey,
    if (recordIdentifier != null) 'record_identifier': recordIdentifier,
    if (stage != null) 'stage': stage,
  };
}
