import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/exploration_providers.dart';
import '../data/exploration_repository.dart';
import '../../reporting/presentation/report_list_screen.dart';
import '../../../core/auth/auth_providers.dart';
import 'analytics_screen.dart';

class LocationDirectoryScreen extends ConsumerStatefulWidget {
  const LocationDirectoryScreen({
    super.key,
    this.level = 'province',
    this.parent,
    this.title = 'Locations',
  });
  final String level, title;
  final String? parent;
  @override
  ConsumerState<LocationDirectoryScreen> createState() => _State();
}

class _State extends ConsumerState<LocationDirectoryScreen> {
  final search = TextEditingController();
  int revision = 0;
  @override
  void dispose() {
    search.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: Text(widget.title)),
    body: SafeArea(
      child: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(12),
            child: SearchBar(
              controller: search,
              hintText: 'Search ${widget.level}',
              leading: const Icon(Icons.search),
              onSubmitted: (_) => setState(() => revision++),
              trailing: [
                IconButton(
                  onPressed: () => setState(() => revision++),
                  icon: const Icon(Icons.arrow_forward),
                ),
              ],
            ),
          ),
          Expanded(
            child: FutureBuilder<List<LocationItem>>(
              key: ValueKey(revision),
              future: ref
                  .read(explorationRepositoryProvider)
                  .locations(
                    level: widget.level,
                    parent: widget.parent,
                    query: search.text,
                  ),
              builder: (context, snapshot) {
                if (snapshot.connectionState != ConnectionState.done) {
                  return const Center(child: CircularProgressIndicator());
                }
                if (snapshot.hasError) {
                  return const Center(
                    child: Text(
                      'Locations could not be loaded. Check your connection and retry.',
                    ),
                  );
                }
                final items = snapshot.data ?? const [];
                if (items.isEmpty) {
                  return const Center(
                    child: Text('No locations match your search.'),
                  );
                }
                return RefreshIndicator(
                  onRefresh: () async => setState(() => revision++),
                  child: ListView.builder(
                    itemCount: items.length,
                    itemBuilder: (context, index) {
                      final item = items[index];
                      final next = item.level == 'province'
                          ? 'tikina'
                          : item.level == 'tikina'
                          ? 'village'
                          : null;
                      return ListTile(
                        leading: const Icon(Icons.location_on_outlined),
                        title: Text(item.name),
                        trailing: next == null
                            ? null
                            : const Icon(Icons.chevron_right),
                        onTap: next == null
                            ? () => Navigator.push(
                                context,
                                MaterialPageRoute<void>(
                                  builder: (_) => _VillageOverview(item: item),
                                ),
                              )
                            : () => Navigator.push(
                                context,
                                MaterialPageRoute<void>(
                                  builder: (_) => LocationDirectoryScreen(
                                    level: next,
                                    parent: item.uuid,
                                    title: item.name,
                                  ),
                                ),
                              ),
                      );
                    },
                  ),
                );
              },
            ),
          ),
        ],
      ),
    ),
  );
}

class _VillageOverview extends ConsumerWidget {
  const _VillageOverview({required this.item});
  final LocationItem item;
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final session = ref.watch(authControllerProvider).value;
    return Scaffold(
      appBar: AppBar(title: Text(item.name)),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Card(
            child: ListTile(
              leading: const Icon(Icons.analytics_outlined),
              title: const Text('Village analytics'),
              subtitle: const Text(
                'Reporting, official indicators, trends and attention areas',
              ),
              trailing: const Icon(Icons.chevron_right),
              onTap: () => Navigator.push(
                context,
                MaterialPageRoute<void>(
                  builder: (_) => AnalyticsScreen(
                    level: 'village',
                    location: item.uuid,
                    title: item.name,
                  ),
                ),
              ),
            ),
          ),
          if (session != null)
            Card(
              child: ListTile(
                leading: const Icon(Icons.assignment_outlined),
                title: const Text('Village reports'),
                subtitle: const Text(
                  'All reporting periods available on this device',
                ),
                trailing: const Icon(Icons.chevron_right),
                onTap: () => Navigator.push(
                  context,
                  MaterialPageRoute<void>(
                    builder: (_) => ReportListScreen(
                      session: session,
                      villageUuid: item.uuid,
                      title: '${item.name} reports',
                    ),
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }
}
