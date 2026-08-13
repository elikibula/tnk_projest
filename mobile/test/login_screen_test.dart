import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:tnk_insight_mobile/core/auth/auth_models.dart';
import 'package:tnk_insight_mobile/core/auth/auth_providers.dart';
import 'package:tnk_insight_mobile/core/auth/auth_remote_data_source.dart';
import 'package:tnk_insight_mobile/core/auth/auth_repository.dart';
import 'package:tnk_insight_mobile/core/auth/installation_identity.dart';
import 'package:tnk_insight_mobile/features/authentication/presentation/login_screen.dart';

import 'auth_repository_test.dart' show MemoryStore;

void main() {
  testWidgets(
    'successful login may dispose LoginScreen before submit completes',
    (tester) async {
      final store = MemoryStore();
      final remote = ControlledLoginRemote();
      final repository = AuthRepository(
        remote,
        store,
        InstallationIdentity(store),
        const Duration(hours: 72),
      );

      await tester.pumpWidget(
        ProviderScope(
          overrides: [authRepositoryProvider.overrideWithValue(repository)],
          child: const _AuthStateReplacementHarness(),
        ),
      );
      await tester.pumpAndSettle();

      await tester.enterText(
        find.widgetWithText(TextFormField, 'Username'),
        'field-user',
      );
      await tester.enterText(
        find.widgetWithText(TextFormField, 'Password'),
        'field-password',
      );
      await tester.tap(find.widgetWithText(FilledButton, 'Sign in'));
      await tester.pump();

      expect(find.byType(LoginScreen), findsNothing);
      expect(find.byKey(const Key('auth-replacement')), findsOneWidget);

      remote.completeSuccess();
      await tester.pumpAndSettle();

      expect(remote.username, 'field-user');
      expect(remote.password, 'field-password');
      expect(find.byType(LoginScreen), findsNothing);
      expect(tester.takeException(), isNull);
    },
  );
}

class _AuthStateReplacementHarness extends ConsumerWidget {
  const _AuthStateReplacementHarness();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final auth = ref.watch(authControllerProvider);
    final showLogin = !auth.isLoading && auth.hasValue && auth.value == null;
    return MaterialApp(
      home: showLogin
          ? const LoginScreen()
          : const Scaffold(
              key: Key('auth-replacement'),
              body: SizedBox.shrink(),
            ),
    );
  }
}

class ControlledLoginRemote implements AuthRemoteDataSource {
  final _result = Completer<LoginResult>();
  String? username;
  String? password;

  void completeSuccess() {
    _result.complete(
      const LoginResult(
        user: AuthUser(
          uuid: 'user-1',
          username: 'field-user',
          fullName: 'Field User',
          preferredLanguage: 'en',
          roles: ['turaga_ni_koro'],
        ),
        tokens: AuthTokens(
          accessToken: 'access-token',
          refreshToken: 'refresh-token',
          deviceUuid: 'device-1',
        ),
      ),
    );
  }

  @override
  Future<LoginResult> login({
    required String username,
    required String password,
    required String installationId,
  }) {
    this.username = username;
    this.password = password;
    return _result.future;
  }

  @override
  Future<void> logout(AuthTokens current) async {}

  @override
  Future<AuthTokens> refresh(AuthTokens current) async => current;
}
