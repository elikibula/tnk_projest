import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:tnk_insight_mobile/core/security/database_key_store.dart';
import 'package:tnk_insight_mobile/features/evidence/data/evidence_cipher.dart';

void main() {
  test(
    'queued evidence is encrypted and can be decrypted for upload',
    () async {
      final directory = await Directory.systemTemp.createTemp(
        'tnk-evidence-test-',
      );
      addTearDown(() => directory.delete(recursive: true));
      final target = File(
        '${directory.path}${Platform.pathSeparator}photo.enc',
      );
      final clear = List<int>.generate(128, (index) => index);
      final cipher = EvidenceCipher(storage: MemorySecureStore());

      await cipher.encryptToFile(clear, target);

      expect(await target.readAsBytes(), isNot(clear));
      expect(await cipher.decryptFile(target), clear);
    },
  );
}

class MemorySecureStore implements SecureValueStore {
  final values = <String, String>{};
  @override
  Future<String?> read(String key) async => values[key];
  @override
  Future<void> write(String key, String value) async => values[key] = value;
}
