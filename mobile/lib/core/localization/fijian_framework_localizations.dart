import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';

/// Flutter does not currently ship Material or Cupertino localizations for
/// Fijian. TNK strings still use the `fj` catalogue; framework-owned labels,
/// date controls, menus, and accessibility text fall back to English.
class FijianMaterialLocalizationsDelegate
    extends LocalizationsDelegate<MaterialLocalizations> {
  const FijianMaterialLocalizationsDelegate();

  @override
  bool isSupported(Locale locale) => locale.languageCode == 'fj';

  @override
  Future<MaterialLocalizations> load(Locale locale) =>
      GlobalMaterialLocalizations.delegate.load(const Locale('en'));

  @override
  bool shouldReload(FijianMaterialLocalizationsDelegate old) => false;
}

class FijianCupertinoLocalizationsDelegate
    extends LocalizationsDelegate<CupertinoLocalizations> {
  const FijianCupertinoLocalizationsDelegate();

  @override
  bool isSupported(Locale locale) => locale.languageCode == 'fj';

  @override
  Future<CupertinoLocalizations> load(Locale locale) =>
      GlobalCupertinoLocalizations.delegate.load(const Locale('en'));

  @override
  bool shouldReload(FijianCupertinoLocalizationsDelegate old) => false;
}
