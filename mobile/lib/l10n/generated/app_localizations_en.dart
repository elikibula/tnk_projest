// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for English (`en`).
class AppLocalizationsEn extends AppLocalizations {
  AppLocalizationsEn([String locale = 'en']) : super(locale);

  @override
  String get language => 'Language';

  @override
  String get english => 'English';

  @override
  String get itaukei => 'iTaukei/Fijian';

  @override
  String get signOut => 'Sign Out';

  @override
  String get reports => 'Reports';

  @override
  String welcome(String name) {
    return 'Welcome, $name';
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
  String get indicators => 'Indicators';

  @override
  String get continueReport => 'Continue Report';

  @override
  String get startReport => 'Start Report';

  @override
  String get reviewIssues => 'Review Issues';

  @override
  String get synchronise => 'Synchronise';

  @override
  String get viewPreviousReport => 'View Previous Report';

  @override
  String get viewVillageSummary => 'View Village Summary';

  @override
  String get viewReports => 'View Reports';

  @override
  String get villageSummary => 'Village summary';

  @override
  String get never => 'Never';
}
