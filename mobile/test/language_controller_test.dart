import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:tnk_insight_mobile/core/localization/fijian_framework_localizations.dart';
import 'package:tnk_insight_mobile/core/localization/language_controller.dart';
import 'package:tnk_insight_mobile/l10n/generated/app_localizations.dart';

void main() {
  test(
    'language selection persists and restores without a network session',
    () async {
      final store = MemoryLanguageStore();
      var container = ProviderContainer(
        overrides: [languageStoreProvider.overrideWithValue(store)],
      );
      addTearDown(container.dispose);

      expect(
        (await container.read(languageControllerProvider.future)).languageCode,
        'en',
      );
      await container
          .read(languageControllerProvider.notifier)
          .select('fj', null);
      expect(store.value, 'fj');
      container.dispose();

      container = ProviderContainer(
        overrides: [languageStoreProvider.overrideWithValue(store)],
      );
      expect(
        (await container.read(languageControllerProvider.future)).languageCode,
        'fj',
      );
    },
  );

  testWidgets(
    'persisted iTaukei locale supplies framework localizations to AppBar',
    (tester) async {
      final store = MemoryLanguageStore()..value = 'fj';

      await tester.pumpWidget(
        ProviderScope(
          overrides: [languageStoreProvider.overrideWithValue(store)],
          child: const _LocalizedAppBarHarness(),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.byType(AppBar), findsOneWidget);
      expect(find.text('Vosa vakayagataki'), findsOneWidget);
      expect(tester.takeException(), isNull);
    },
  );

  testWidgets('changing to iTaukei keeps the active AppBar localized', (
    tester,
  ) async {
    final store = MemoryLanguageStore();
    await tester.pumpWidget(
      ProviderScope(
        overrides: [languageStoreProvider.overrideWithValue(store)],
        child: const _LocalizedAppBarHarness(),
      ),
    );
    await tester.pumpAndSettle();

    await tester.tap(find.byIcon(Icons.language));
    await tester.pumpAndSettle();

    expect(store.value, 'fj');
    expect(find.text('Vosa vakayagataki'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  test(
    'English and reviewed iTaukei localization catalogues are available',
    () {
      expect(
        AppLocalizations.supportedLocales.map((locale) => locale.languageCode),
        containsAll(['en', 'fj']),
      );
      expect(lookupAppLocalizations(const Locale('en')).reports, 'Reports');
      expect(lookupAppLocalizations(const Locale('fj')).reports, 'Ripote');
      expect(
        lookupAppLocalizations(const Locale('fj')).welcome('Mere'),
        'Bula Vinaka, Mere',
      );
    },
  );
}

class _LocalizedAppBarHarness extends ConsumerWidget {
  const _LocalizedAppBarHarness();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return MaterialApp(
      locale: ref.watch(languageControllerProvider).value ?? const Locale('en'),
      supportedLocales: AppLocalizations.supportedLocales,
      localizationsDelegates: const [
        FijianMaterialLocalizationsDelegate(),
        FijianCupertinoLocalizationsDelegate(),
        ...AppLocalizations.localizationsDelegates,
      ],
      home: Builder(
        builder: (context) => Scaffold(
          appBar: AppBar(
            title: Text(AppLocalizations.of(context)!.language),
            actions: [
              IconButton(
                onPressed: () => ref
                    .read(languageControllerProvider.notifier)
                    .select('fj', null),
                icon: const Icon(Icons.language),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class MemoryLanguageStore implements LanguageStore {
  String? value;
  @override
  Future<String?> read() async => value;
  @override
  Future<void> write(String languageCode) async => value = languageCode;
}
