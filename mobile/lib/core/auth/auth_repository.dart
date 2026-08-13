import 'auth_failures.dart';
import 'auth_models.dart';
import 'auth_remote_data_source.dart';
import 'installation_identity.dart';
import 'secure_session_store.dart';

class AuthRepository {
  AuthRepository(
    this._remote,
    this._store,
    this._identity,
    this._offlineSessionDuration, {
    DateTime Function()? clock,
  }) : _clock = clock ?? DateTime.now;

  final AuthRemoteDataSource _remote;
  final SecureSessionStore _store;
  final InstallationIdentity _identity;
  final Duration _offlineSessionDuration;
  final DateTime Function() _clock;

  Future<AuthSession> login(String username, String password) async {
    final result = await _remote.login(
      username: username.trim(),
      password: password,
      installationId: await _identity.getOrCreate(),
    );
    final now = _clock().toUtc();
    final session = AuthSession(
      user: result.user,
      tokens: result.tokens,
      establishedAt: now,
      offlineValidUntil: now.add(_offlineSessionDuration),
    );
    await _store.writeSession(session);
    return session;
  }

  Future<AuthSession?> restore() async {
    final session = await _store.readSession();
    if (session == null) return null;
    final now = _clock().toUtc();
    if (!now.isBefore(session.offlineValidUntil.toUtc())) {
      await _store.clearSession();
      return null;
    }
    final expiry = session.tokens.accessExpiresAt;
    if (expiry != null &&
        now.isBefore(expiry.subtract(const Duration(seconds: 30)))) {
      return session.copyWith(isOffline: false);
    }
    try {
      final tokens = await _remote.refresh(session.tokens);
      final refreshed = session.copyWith(tokens: tokens, isOffline: false);
      await _store.writeSession(refreshed);
      return refreshed;
    } on AuthNetworkFailure {
      return session.copyWith(isOffline: true);
    } on DeviceRevokedFailure {
      await _store.clearSession();
      rethrow;
    } on SessionExpiredFailure {
      await _store.clearSession();
      rethrow;
    }
  }

  Future<AuthSession> ensureFreshSession(AuthSession session) async {
    final now = _clock().toUtc();
    if (!now.isBefore(session.offlineValidUntil.toUtc())) {
      await _store.clearSession();
      throw const SessionExpiredFailure();
    }
    final expiry = session.tokens.accessExpiresAt;
    if (!session.isOffline &&
        expiry != null &&
        now.isBefore(expiry.subtract(const Duration(seconds: 30)))) {
      return session;
    }
    try {
      final tokens = await _remote.refresh(session.tokens);
      final refreshed = session.copyWith(tokens: tokens, isOffline: false);
      await _store.writeSession(refreshed);
      return refreshed;
    } on AuthNetworkFailure {
      return session.copyWith(isOffline: true);
    } on DeviceRevokedFailure {
      await _store.clearSession();
      rethrow;
    } on SessionExpiredFailure {
      await _store.clearSession();
      rethrow;
    }
  }

  Future<void> logout(AuthSession session) async {
    try {
      await _remote.logout(session.tokens);
    } on AuthFailure {
      // Local credentials are removed even when the server cannot be reached.
    } finally {
      await _store.clearSession();
    }
  }

  Future<void> clearLocalSession() => _store.clearSession();
}
