import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'router.dart';
import 'theme.dart';
import '../core/localization/language_controller.dart';
import '../core/localization/fijian_framework_localizations.dart';
import '../l10n/generated/app_localizations.dart';

class TnkInsightApp extends ConsumerWidget {
  const TnkInsightApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return MaterialApp.router(
      title: 'TNK Insight Mobile',
      debugShowCheckedModeBanner: false,
      theme: buildTnkTheme(),
      locale: ref.watch(languageControllerProvider).value ?? const Locale('en'),
      supportedLocales: AppLocalizations.supportedLocales,
      localizationsDelegates: const [
        FijianMaterialLocalizationsDelegate(),
        FijianCupertinoLocalizationsDelegate(),
        ...AppLocalizations.localizationsDelegates,
      ],
      routerConfig: ref.watch(appRouterProvider),
    );
  }
}
