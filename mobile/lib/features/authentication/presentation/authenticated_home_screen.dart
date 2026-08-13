import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/auth/auth_models.dart';
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
    if (bootstrap.isLoading || bootstrap.value == null) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }
    return DashboardScreen(session: widget.session);
  }
}
