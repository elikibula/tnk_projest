import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/exploration_providers.dart';

class AnalyticsScreen extends ConsumerStatefulWidget {
  const AnalyticsScreen({
    super.key,
    this.level,
    this.location,
    this.title = 'Analytics',
  });
  final String? level, location;
  final String title;
  @override
  ConsumerState<AnalyticsScreen> createState() => _State();
}

class _State extends ConsumerState<AnalyticsScreen> {
  String? period;
  String? comparePeriod;
  int revision = 0;
  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: Text(widget.title)),
    body: SafeArea(
      child: FutureBuilder<Map<String, dynamic>>(
        key: ValueKey((period, comparePeriod, revision)),
        future: ref
            .read(explorationRepositoryProvider)
            .analytics(
              period: period,
              level: widget.level,
              location: widget.location,
              comparePeriod: comparePeriod,
            ),
        builder: (context, snapshot) {
          if (snapshot.connectionState != ConnectionState.done) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return _empty(
              'Analytics could not be loaded. Check your connection and permissions.',
            );
          }
          final data = snapshot.data!;
          if (data['summary'] == null) {
            return _empty('No analytics data is available.');
          }
          final periods = (data['periods'] as List<dynamic>);
          final current = Map<String, dynamic>.from(data['period'] as Map);
          final summary = Map<String, dynamic>.from(data['summary'] as Map);
          final reporting = Map<String, dynamic>.from(
            summary['reporting'] as Map,
          );
          final indicators = Map<String, dynamic>.from(
            summary['indicators'] as Map,
          );
          return RefreshIndicator(
            onRefresh: () async => setState(() => revision++),
            child: ListView(
              padding: const EdgeInsets.all(16),
              children: [
                Text(
                  (data['scope'] as Map)['name'].toString(),
                  style: Theme.of(context).textTheme.headlineSmall,
                ),
                DropdownButtonFormField<String>(
                  initialValue: period ?? current['uuid'].toString(),
                  decoration: const InputDecoration(
                    labelText: 'Reporting period',
                  ),
                  items: periods.map((raw) {
                    final item = raw as Map;
                    return DropdownMenuItem(
                      value: item['uuid'].toString(),
                      child: Text('${item['year']} Q${item['quarter']}'),
                    );
                  }).toList(),
                  onChanged: (value) => setState(() => period = value),
                ),
                const SizedBox(height: 10),
                DropdownButtonFormField<String>(
                  initialValue: comparePeriod,
                  decoration: const InputDecoration(
                    labelText: 'Compare with period',
                  ),
                  items: [
                    const DropdownMenuItem<String>(
                      value: null,
                      child: Text('Previous period'),
                    ),
                    ...periods.map((raw) {
                      final item = raw as Map;
                      return DropdownMenuItem(
                        value: item['uuid'].toString(),
                        child: Text('${item['year']} Q${item['quarter']}'),
                      );
                    }),
                  ],
                  onChanged: (value) => setState(() => comparePeriod = value),
                ),
                const SizedBox(height: 16),
                LayoutBuilder(
                  builder: (context, size) => GridView.count(
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    crossAxisCount: size.maxWidth < 560 ? 2 : 4,
                    childAspectRatio: 1.25,
                    children: [
                      _metric(
                        'Completion',
                        '${reporting['completion']}%',
                        Icons.task_alt,
                      ),
                      _metric(
                        'Received',
                        '${reporting['received']} / ${reporting['expected']}',
                        Icons.assignment_turned_in_outlined,
                      ),
                      _metric(
                        'Approved',
                        '${reporting['official']}',
                        Icons.verified_outlined,
                      ),
                      _metric(
                        'Missing',
                        '${reporting['missing']}',
                        Icons.warning_amber_outlined,
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 12),
                Text(
                  'Key indicators',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
                for (final entry in indicators.entries)
                  Card(
                    child: ListTile(
                      title: Text((entry.value as Map)['label'].toString()),
                      trailing: Text(
                        (entry.value as Map)['has_data'] == true
                            ? '${(entry.value as Map)['value']} ${(entry.value as Map)['unit']}'
                            : 'No data',
                      ),
                    ),
                  ),
                if (data['comparison'] != null) ...[
                  Text(
                    'Period comparison',
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                  _comparisonCard(
                    Map<String, dynamic>.from(data['comparison'] as Map),
                    reporting,
                    indicators,
                  ),
                ],
                Text(
                  'Attention areas',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
                for (final raw in data['insights'] as List<dynamic>)
                  Card(
                    child: ListTile(
                      leading: const Icon(Icons.lightbulb_outline),
                      title: Text((raw as Map)['title'].toString()),
                      subtitle: Text(raw['text'].toString()),
                    ),
                  ),
                if ((data['children'] as List).isNotEmpty) ...[
                  Text(
                    'Drill down',
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                  for (final raw in data['children'] as List<dynamic>)
                    ListTile(
                      title: Text(
                        ((raw as Map)['location'] as Map)['name'].toString(),
                      ),
                      trailing: const Icon(Icons.chevron_right),
                      onTap: () => Navigator.push(
                        context,
                        MaterialPageRoute<void>(
                          builder: (_) => AnalyticsScreen(
                            level: (raw['location'] as Map)['level'].toString(),
                            location: (raw['location'] as Map)['uuid']
                                .toString(),
                            title: (raw['location'] as Map)['name'].toString(),
                          ),
                        ),
                      ),
                    ),
                ],
                if ((data['trends'] as List).isNotEmpty) ...[
                  Text(
                    'Reporting trends',
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                  for (final raw in data['trends'] as List<dynamic>)
                    ListTile(
                      leading: const Icon(Icons.show_chart),
                      title: Text((raw as Map)['period'].toString()),
                      subtitle: LinearProgressIndicator(
                        value: ((raw['completion'] as num).toDouble() / 100)
                            .clamp(0, 1),
                      ),
                      trailing: Text('${raw['completion']}%'),
                    ),
                ],
                if ((data['missing_reports'] as List).isNotEmpty) ...[
                  Text(
                    'Missing reports',
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                  for (final raw in data['missing_reports'] as List<dynamic>)
                    ListTile(
                      leading: const Icon(Icons.warning_amber_outlined),
                      title: Text(
                        ((raw as Map)['village'] as Map)['name'].toString(),
                      ),
                      subtitle: Text(
                        raw['last_period'] == null
                            ? 'No previous received report'
                            : 'Last received: ${raw['last_period']}',
                      ),
                    ),
                ],
                const SizedBox(height: 8),
                Text(
                  data['data_scope'].toString(),
                  style: Theme.of(context).textTheme.bodySmall,
                ),
              ],
            ),
          );
        },
      ),
    ),
  );
  Widget _metric(String label, String value, IconData icon) => Card(
    child: Padding(
      padding: const EdgeInsets.all(10),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(icon),
          Text(value, style: Theme.of(context).textTheme.titleLarge),
          Text(label, textAlign: TextAlign.center),
        ],
      ),
    ),
  );
  Widget _comparisonCard(
    Map<String, dynamic> comparison,
    Map<String, dynamic> currentReporting,
    Map<String, dynamic> currentIndicators,
  ) {
    final oldReporting = Map<String, dynamic>.from(
      comparison['reporting'] as Map,
    );
    final oldIndicators = Map<String, dynamic>.from(
      comparison['indicators'] as Map,
    );
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Completion: ${oldReporting['completion']}% → ${currentReporting['completion']}%',
            ),
            for (final key in currentIndicators.keys)
              Text(
                '${(currentIndicators[key] as Map)['label']}: ${_value(oldIndicators[key])} → ${_value(currentIndicators[key])}',
              ),
          ],
        ),
      ),
    );
  }

  String _value(Object? raw) {
    final item = Map<String, dynamic>.from(raw as Map);
    return item['has_data'] == true
        ? '${item['value']} ${item['unit']}'
        : 'No data';
  }

  Widget _empty(String value) => Center(
    child: Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(value, textAlign: TextAlign.center),
          const SizedBox(height: 12),
          FilledButton.icon(
            onPressed: () => setState(() => revision++),
            icon: const Icon(Icons.refresh),
            label: const Text('Retry'),
          ),
        ],
      ),
    ),
  );
}
