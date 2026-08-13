import 'dart:convert';
import 'dart:math';

import 'package:flutter_test/flutter_test.dart';
import 'package:tnk_insight_mobile/core/security/database_key_store.dart';

void main() {
  test('database key is 256-bit and remains stable', () async {
    final values = MemorySecureValueStore();
    final store = PlatformDatabaseKeyStore(storage: values, random: Random(42));

    final first = await store.getOrCreateKey();
    final second = await store.getOrCreateKey();

    expect(base64Url.decode(first), hasLength(32));
    expect(second, first);
    expect(values.values, hasLength(1));
  });

  test('invalid stored key is replaced', () async {
    final values = MemorySecureValueStore()
      ..values['tnk.database.key.v1'] = 'bad';
    final store = PlatformDatabaseKeyStore(storage: values, random: Random(42));

    final key = await store.getOrCreateKey();

    expect(base64Url.decode(key), hasLength(32));
    expect(key, isNot('bad'));
  });
}

class MemorySecureValueStore implements SecureValueStore {
  final values = <String, String>{};

  @override
  Future<String?> read(String key) async => values[key];

  @override
  Future<void> write(String key, String value) async => values[key] = value;
}
