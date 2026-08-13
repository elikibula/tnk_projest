import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:tnk_insight_mobile/core/auth/auth_failures.dart';
import 'package:tnk_insight_mobile/core/auth/auth_models.dart';
import 'package:tnk_insight_mobile/core/auth/auth_remote_data_source.dart';
import 'package:tnk_insight_mobile/core/auth/auth_repository.dart';
import 'package:tnk_insight_mobile/core/auth/installation_identity.dart';
import 'package:tnk_insight_mobile/core/auth/secure_session_store.dart';

void main() {
  late MemoryStore store;
  late FakeRemote remote;
  late DateTime now;
  late AuthRepository repository;

  setUp(() {
    store = MemoryStore();
    remote = FakeRemote();
    now = DateTime.utc(2026, 8, 11, 10);
    repository = AuthRepository(
      remote,
      store,
      InstallationIdentity(store),
      const Duration(hours: 72),
      clock: () => now,
    );
  });

  test('online login establishes a secure local session', () async {
    final session = await repository.login(' user ', 'secret');

    expect(remote.username, 'user');
    expect(remote.password, 'secret');
    expect(store.session, same(session));
    expect(store.installationId, isNotNull);
    expect(session.offlineValidUntil, now.add(const Duration(hours: 72)));
  });

  test('expired access token refreshes and persists rotated tokens', () async {
    store.session = _session(
      now,
      accessExpiry: now.subtract(const Duration(minutes: 1)),
    );

    final restored = await repository.restore();

    expect(remote.refreshCalls, 1);
    expect(restored!.tokens.accessToken, remote.refreshed.accessToken);
    expect(store.session!.tokens.refreshToken, remote.refreshed.refreshToken);
    expect(restored.isOffline, isFalse);
  });

  test('network failure permits bounded offline continuation', () async {
    store.session = _session(
      now,
      accessExpiry: now.subtract(const Duration(minutes: 1)),
    );
    remote.refreshError = const AuthNetworkFailure();

    final restored = await repository.restore();

    expect(restored!.isOffline, isTrue);
    expect(store.session, isNotNull);
  });

  test('expired offline window clears credentials', () async {
    store.session = _session(
      now,
      accessExpiry: now.subtract(const Duration(minutes: 1)),
      offlineUntil: now,
    );

    expect(await repository.restore(), isNull);
    expect(store.session, isNull);
    expect(remote.refreshCalls, 0);
  });

  test('revoked device clears credentials', () async {
    store.session = _session(
      now,
      accessExpiry: now.subtract(const Duration(minutes: 1)),
    );
    remote.refreshError = const DeviceRevokedFailure();

    await expectLater(
      repository.restore(),
      throwsA(isA<DeviceRevokedFailure>()),
    );
    expect(store.session, isNull);
  });

  test('logout clears local credentials when API is unavailable', () async {
    final session = _session(
      now,
      accessExpiry: now.add(const Duration(minutes: 5)),
    );
    store.session = session;
    remote.logoutError = const AuthNetworkFailure();

    await repository.logout(session);

    expect(store.session, isNull);
  });

  test('active session refreshes when an API call needs a new token', () async {
    final session = _session(
      now,
      accessExpiry: now.subtract(const Duration(seconds: 1)),
    );

    final refreshed = await repository.ensureFreshSession(session);

    expect(remote.refreshCalls, 1);
    expect(refreshed.tokens.refreshToken, 'refresh-new');
    expect(store.session, same(refreshed));
  });
}

AuthSession _session(
  DateTime now, {
  required DateTime accessExpiry,
  DateTime? offlineUntil,
}) => AuthSession(
  user: const AuthUser(
    uuid: 'user-1',
    username: 'user',
    fullName: 'Test User',
    preferredLanguage: 'en',
    roles: ['turaga_ni_koro'],
  ),
  tokens: AuthTokens(
    accessToken: _jwt(accessExpiry),
    refreshToken: 'refresh-old',
    deviceUuid: 'device-1',
  ),
  establishedAt: now.subtract(const Duration(hours: 1)),
  offlineValidUntil: offlineUntil ?? now.add(const Duration(hours: 71)),
);

String _jwt(DateTime expiry) {
  String part(Object value) =>
      base64Url.encode(utf8.encode(jsonEncode(value))).replaceAll('=', '');
  return '${part({'alg': 'none'})}.${part({'exp': expiry.millisecondsSinceEpoch ~/ 1000})}.signature';
}

class MemoryStore implements SecureSessionStore {
  AuthSession? session;
  String? installationId;

  @override
  Future<void> clearSession() async => session = null;
  @override
  Future<String?> readInstallationId() async => installationId;
  @override
  Future<AuthSession?> readSession() async => session;
  @override
  Future<void> writeInstallationId(String value) async =>
      installationId = value;
  @override
  Future<void> writeSession(AuthSession value) async => session = value;
}

class FakeRemote implements AuthRemoteDataSource {
  String? username;
  String? password;
  int refreshCalls = 0;
  AuthFailure? refreshError;
  AuthFailure? logoutError;
  final refreshed = AuthTokens(
    accessToken: _jwt(DateTime.utc(2030)),
    refreshToken: 'refresh-new',
    deviceUuid: 'device-1',
  );

  @override
  Future<LoginResult> login({
    required String username,
    required String password,
    required String installationId,
  }) async {
    this.username = username;
    this.password = password;
    return LoginResult(
      user: const AuthUser(
        uuid: 'user-1',
        username: 'user',
        fullName: 'Test User',
        preferredLanguage: 'en',
        roles: ['turaga_ni_koro'],
      ),
      tokens: refreshed,
    );
  }

  @override
  Future<AuthTokens> refresh(AuthTokens current) async {
    refreshCalls++;
    if (refreshError case final error?) throw error;
    return refreshed;
  }

  @override
  Future<void> logout(AuthTokens current) async {
    if (logoutError case final error?) throw error;
  }
}
