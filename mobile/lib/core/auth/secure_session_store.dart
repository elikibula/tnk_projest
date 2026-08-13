import 'dart:convert';

import 'package:flutter_secure_storage/flutter_secure_storage.dart';

import 'auth_models.dart';

abstract interface class SecureSessionStore {
  Future<AuthSession?> readSession();
  Future<void> writeSession(AuthSession session);
  Future<void> clearSession();
  Future<String?> readInstallationId();
  Future<void> writeInstallationId(String value);
}

class PlatformSecureSessionStore implements SecureSessionStore {
  PlatformSecureSessionStore({FlutterSecureStorage? storage})
    : _storage = storage ?? const FlutterSecureStorage();

  static const _sessionKey = 'tnk.auth.session.v1';
  static const _installationKey = 'tnk.installation.id.v1';
  final FlutterSecureStorage _storage;

  @override
  Future<AuthSession?> readSession() async {
    final value = await _storage.read(key: _sessionKey);
    if (value == null) return null;
    try {
      return AuthSession.fromJson(jsonDecode(value) as Map<String, dynamic>);
    } on Object {
      await clearSession();
      return null;
    }
  }

  @override
  Future<void> writeSession(AuthSession session) =>
      _storage.write(key: _sessionKey, value: jsonEncode(session.toJson()));

  @override
  Future<void> clearSession() => _storage.delete(key: _sessionKey);

  @override
  Future<String?> readInstallationId() => _storage.read(key: _installationKey);

  @override
  Future<void> writeInstallationId(String value) =>
      _storage.write(key: _installationKey, value: value);
}
