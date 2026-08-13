import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:tnk_insight_mobile/app/app.dart';
import 'package:tnk_insight_mobile/core/config/app_environment.dart';
import 'package:tnk_insight_mobile/core/auth/auth_providers.dart';

import 'auth_repository_test.dart' show MemoryStore;

void main() {
  testWidgets('unauthenticated app presents secure online login', (
    tester,
  ) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          appEnvironmentProvider.overrideWithValue(AppEnvironment.staging),
          secureSessionStoreProvider.overrideWithValue(MemoryStore()),
        ],
        child: const TnkInsightApp(),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('TNK Insight Mobile'), findsOneWidget);
    expect(find.text('Sign in'), findsOneWidget);
    expect(find.text('Username'), findsOneWidget);
    expect(find.text('Password'), findsOneWidget);
    expect(find.byIcon(Icons.shield_outlined), findsOneWidget);
  });
}
