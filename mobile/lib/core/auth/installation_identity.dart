import 'package:uuid/uuid.dart';

import 'secure_session_store.dart';

class InstallationIdentity {
  InstallationIdentity(this._store, {Uuid? uuid})
    : _uuid = uuid ?? const Uuid();

  final SecureSessionStore _store;
  final Uuid _uuid;

  Future<String> getOrCreate() async {
    final existing = await _store.readInstallationId();
    if (existing != null && Uuid.isValidUUID(fromString: existing)) {
      return existing;
    }
    final created = _uuid.v4();
    await _store.writeInstallationId(created);
    return created;
  }
}
