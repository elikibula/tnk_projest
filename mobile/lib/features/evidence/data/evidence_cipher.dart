import 'dart:convert';
import 'dart:io';
import 'dart:math';

import 'package:cryptography/cryptography.dart';

import '../../../core/security/database_key_store.dart';

class EvidenceCipher {
  EvidenceCipher({SecureValueStore? storage, Random? random})
    : _storage = storage ?? FlutterSecureValueStore(),
      _random = random ?? Random.secure();

  static const _keyName = 'tnk.evidence.key.v1';
  final SecureValueStore _storage;
  final Random _random;
  final Cipher _cipher = AesGcm.with256bits();

  Future<void> encryptToFile(List<int> clearBytes, File target) async {
    final nonce = List<int>.generate(12, (_) => _random.nextInt(256));
    final box = await _cipher.encrypt(
      clearBytes,
      secretKey: await _key(),
      nonce: nonce,
    );
    await target.writeAsBytes([
      ...nonce,
      ...box.mac.bytes,
      ...box.cipherText,
    ], flush: true);
  }

  Future<List<int>> decryptFile(File source) async {
    final bytes = await source.readAsBytes();
    if (bytes.length < 28) {
      throw StateError('The protected evidence file is invalid.');
    }
    return _cipher.decrypt(
      SecretBox(
        bytes.sublist(28),
        nonce: bytes.sublist(0, 12),
        mac: Mac(bytes.sublist(12, 28)),
      ),
      secretKey: await _key(),
    );
  }

  Future<SecretKey> _key() async {
    final existing = await _storage.read(_keyName);
    if (existing != null) return SecretKey(base64Url.decode(existing));
    final bytes = List<int>.generate(32, (_) => _random.nextInt(256));
    await _storage.write(_keyName, base64UrlEncode(bytes));
    return SecretKey(bytes);
  }
}
