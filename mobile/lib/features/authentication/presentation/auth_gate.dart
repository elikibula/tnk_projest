import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/auth/auth_failures.dart';
import '../../../core/auth/auth_providers.dart';
import 'authenticated_home_screen.dart';
import 'login_screen.dart';

class AuthGate extends ConsumerWidget {
  const AuthGate({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final auth = ref.watch(authControllerProvider);
    return auth.when(
      data: (session) => session == null
          ? const LoginScreen()
          : AuthenticatedHomeScreen(session: session),
      loading: () =>
          const Scaffold(body: Center(child: CircularProgressIndicator())),
      error: (error, stackTrace) => LoginScreen(
        initialError: error is AuthFailure
            ? error.message
            : const UnexpectedAuthFailure().message,
      ),
    );
  }
}
