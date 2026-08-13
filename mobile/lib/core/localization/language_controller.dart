import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

import '../api/api_client.dart';
import '../auth/auth_models.dart';

abstract interface class LanguageStore {
  Future<String?> read();
  Future<void> write(String languageCode);
}

class SecureLanguageStore implements LanguageStore {
  const SecureLanguageStore([this.storage = const FlutterSecureStorage()]);
  static const key = 'tnk.language.v1';
  final FlutterSecureStorage storage;
  @override
  Future<String?> read() => storage.read(key: key);
  @override
  Future<void> write(String languageCode) =>
      storage.write(key: key, value: languageCode);
}

final languageStoreProvider = Provider<LanguageStore>(
  (_) => const SecureLanguageStore(),
);

class LanguageController extends AsyncNotifier<Locale> {
  @override
  Future<Locale> build() async {
    final stored = await ref.watch(languageStoreProvider).read();
    return Locale(stored == 'fj' ? 'fj' : 'en');
  }

  Future<void> select(String languageCode, AuthSession? session) async {
    final code = languageCode == 'fj' ? 'fj' : 'en';
    await ref.read(languageStoreProvider).write(code);
    state = AsyncData(Locale(code));
    if (session != null && !session.isOffline) {
      try {
        await ref
            .read(dioProvider)
            .patch<dynamic>(
              '/api/v1/me/',
              data: {'preferred_language': code},
              options: Options(
                headers: {
                  'Authorization': 'Bearer ${session.tokens.accessToken}',
                },
              ),
            );
      } on DioException {
        // Local preference remains authoritative while the API is unavailable.
      }
    }
  }
}

final languageControllerProvider =
    AsyncNotifierProvider<LanguageController, Locale>(LanguageController.new);
