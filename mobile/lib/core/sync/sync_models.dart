class SyncResult {
  const SyncResult({
    required this.uploaded,
    required this.downloaded,
    required this.conflicts,
    required this.failed,
  });
  final int uploaded;
  final int downloaded;
  final int conflicts;
  final int failed;
}

class SyncNetworkFailure implements Exception {
  const SyncNetworkFailure();
  String get message => 'Synchronization could not reach the TNK service.';
}

class SyncUnexpectedFailure implements Exception {
  const SyncUnexpectedFailure();
  String get message => 'Synchronization could not be completed safely.';
}
