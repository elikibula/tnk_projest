import 'dart:convert';
import 'dart:math';

import 'package:flutter_secure_storage/flutter_secure_storage.dart';

abstract interface class DatabaseKeyStore {
  Future<String> getOrCreateKey();
}

abstract interface class SecureValueStore {
  Future<String?> read(String key);
  Future<void> write(String key, String value);
}

class FlutterSecureValueStore implements SecureValueStore {
  FlutterSecureValueStore([FlutterSecureStorage? storage])
    : _storage = storage ?? const FlutterSecureStorage();

  final FlutterSecureStorage _storage;

  @override
  Future<String?> read(String key) => _storage.read(key: key);

  @override
  Future<void> write(String key, String value) =>
      _storage.write(key: key, value: value);
}

class PlatformDatabaseKeyStore implements DatabaseKeyStore {
  PlatformDatabaseKeyStore({SecureValueStore? storage, Random? random})
    : _storage = storage ?? FlutterSecureValueStore(),
      _random = random ?? Random.secure();

  static const _keyName = 'tnk.database.key.v1';
  final SecureValueStore _storage;
  final Random _random;

  @override
  Future<String> getOrCreateKey() async {
    final existing = await _storage.read(_keyName);
    if (existing != null && _isValid(existing)) return existing;

    final bytes = List<int>.generate(32, (_) => _random.nextInt(256));
    final created = base64UrlEncode(bytes);
    await _storage.write(_keyName, created);
    return created;
  }

  bool _isValid(String value) {
    try {
      return base64Url.decode(value).length == 32;
    } on FormatException {
      return false;
    }
  }
}
