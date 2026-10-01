import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/auth/auth_models.dart';
import '../../../core/auth/auth_providers.dart';
import '../../../core/bootstrap/bootstrap_providers.dart';
import '../../dashboard/presentation/dashboard_screen.dart';

class AuthenticatedHomeScreen extends ConsumerStatefulWidget {
  const AuthenticatedHomeScreen({required this.session, super.key});
  final AuthSession session;
  @override
  ConsumerState<AuthenticatedHomeScreen> createState() =>
      _AuthenticatedHomeScreenState();
}

class _AuthenticatedHomeScreenState
    extends ConsumerState<AuthenticatedHomeScreen> {
  @override
  void initState() {
    super.initState();
    Future.microtask(() {
      if (mounted && ref.read(bootstrapControllerProvider).value == null) {
        ref.read(bootstrapControllerProvider.notifier).load();
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final bootstrap = ref.watch(bootstrapControllerProvider);
    if (bootstrap.hasError) {
      return Scaffold(
        body: SafeArea(
          child: Center(
            child: Padding(
              padding: const EdgeInsets.all(24),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Text(
                    'TNK data could not be prepared. Check your connection and retry.',
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 12),
                  FilledButton.icon(
                    onPressed: () =>
                        ref.read(bootstrapControllerProvider.notifier).load(),
                    icon: const Icon(Icons.refresh),
                    label: const Text('Retry'),
                  ),
                  TextButton(
                    onPressed: () =>
                        ref.read(authControllerProvider.notifier).logout(),
                    child: const Text('Sign out'),
                  ),
                ],
              ),
            ),
          ),
        ),
      );
    }
    if (bootstrap.isLoading || bootstrap.value == null) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }
    return DashboardScreen(session: widget.session);
  }
}
