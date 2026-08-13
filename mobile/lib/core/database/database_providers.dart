import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../security/database_key_store.dart';
import 'app_database.dart';

final databaseKeyStoreProvider = Provider<DatabaseKeyStore>(
  (ref) => PlatformDatabaseKeyStore(),
);

final appDatabaseProvider = FutureProvider<AppDatabase>((ref) async {
  final key = await ref.watch(databaseKeyStoreProvider).getOrCreateKey();
  final database = AppDatabase.encrypted(await mobileDatabaseFile(), key);
  ref.onDispose(database.close);
  return database;
});
