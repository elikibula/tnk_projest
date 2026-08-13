enum SyncStatus {
  localOnly('local_only'),
  pendingCreate('pending_create'),
  pendingUpdate('pending_update'),
  pendingDelete('pending_delete'),
  uploading('uploading'),
  synced('synced'),
  conflict('conflict'),
  failed('failed');

  const SyncStatus(this.value);
  final String value;
}

enum ConflictStatus {
  unresolved('unresolved'),
  keepServer('keep_server'),
  useLocal('use_local'),
  manuallyResolved('manually_resolved'),
  serverRequired('server_required');

  const ConflictStatus(this.value);
  final String value;
}
