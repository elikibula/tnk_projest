// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for Fijian (`fj`).
class AppLocalizationsFj extends AppLocalizations {
  AppLocalizationsFj([String locale = 'fj']) : super(locale);

  @override
  String get language => 'Vosa vakayagataki';

  @override
  String get english => 'English';

  @override
  String get itaukei => 'iTaukei/Fijian';

  @override
  String get signOut => 'Sign Out';

  @override
  String get reports => 'Ripote';

  @override
  String welcome(String name) {
    return 'Bula Vinaka, $name';
  }

  @override
  String get online => 'Online';

  @override
  String get offlineData => 'Offline data';

  @override
  String get noVillage => 'No village';

  @override
  String get currentReport => 'Current report';

  @override
  String get noCurrentReport => 'No current report';

  @override
  String get issues => 'Issues';

  @override
  String get pendingSync => 'Pending sync';

  @override
  String get lastSync => 'Last sync';

  @override
  String get indicators => 'Vakadikevi ni itukutuku';

  @override
  String get continueReport => 'Continue Report';

  @override
  String get startReport => 'Ripote Vou';

  @override
  String get reviewIssues => 'Review Issues';

  @override
  String get synchronise => 'Synchronise';

  @override
  String get viewPreviousReport => 'View Previous Report';

  @override
  String get viewVillageSummary => 'View Village Summary';

  @override
  String get viewReports => 'Raica na Ripote';

  @override
  String get villageSummary => 'Village summary';

  @override
  String get never => 'Never';
}
