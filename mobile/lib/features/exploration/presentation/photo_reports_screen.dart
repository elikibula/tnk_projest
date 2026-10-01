import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/exploration_providers.dart';

class PhotoReportsScreen extends ConsumerStatefulWidget {
  const PhotoReportsScreen({super.key});
  @override
  ConsumerState<PhotoReportsScreen> createState() => _PhotoReportsState();
}

class _PhotoReportsState extends ConsumerState<PhotoReportsScreen> {
  String province = '', tikina = '', village = '', year = '', quarter = '';
  int revision = 0;

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Photo Reports')),
    body: FutureBuilder<List<Map<String, dynamic>>>(
      key: ValueKey(revision),
      future: ref.read(photoReportsRepositoryProvider).reports(),
      builder: (context, snapshot) {
        if (snapshot.connectionState != ConnectionState.done) {
          return const Center(child: CircularProgressIndicator());
        }
        if (snapshot.hasError) {
          return _error(
            'Photo Reports could not be loaded. Check your connection and role.',
          );
        }
        final all = snapshot.data!;
        final provinces = _values(all, 'province_name');
        final tikinas = _values(
          all.where(
            (item) => province.isEmpty || item['province_name'] == province,
          ),
          'tikina_name',
        );
        final villages = _values(
          all.where(
            (item) =>
                (province.isEmpty || item['province_name'] == province) &&
                (tikina.isEmpty || item['tikina_name'] == tikina),
          ),
          'village_name',
        );
        final years =
            all
                .map((item) => _year(item['period_label']?.toString() ?? ''))
                .where((item) => item.isNotEmpty)
                .toSet()
                .toList()
              ..sort((a, b) => b.compareTo(a));
        final filtered = all.where((item) {
          final period = item['period_label']?.toString() ?? '';
          return (province.isEmpty || item['province_name'] == province) &&
              (tikina.isEmpty || item['tikina_name'] == tikina) &&
              (village.isEmpty || item['village_name'] == village) &&
              (year.isEmpty || period.contains(year)) &&
              (quarter.isEmpty || period.toUpperCase().contains('Q$quarter'));
        }).toList();
        return RefreshIndicator(
          onRefresh: () async => setState(() => revision++),
          child: ListView(
            padding: const EdgeInsets.all(16),
            children: [
              Text(
                'Visual report review',
                style: Theme.of(context).textTheme.headlineSmall,
              ),
              const Text(
                'Choose an authorised village report and review its protected images.',
              ),
              const SizedBox(height: 12),
              _dropdown(
                'Province',
                province,
                provinces,
                (value) => setState(() {
                  province = value;
                  tikina = '';
                  village = '';
                }),
              ),
              _dropdown(
                'Tikina',
                tikina,
                tikinas,
                (value) => setState(() {
                  tikina = value;
                  village = '';
                }),
              ),
              _dropdown(
                'Village',
                village,
                villages,
                (value) => setState(() => village = value),
              ),
              Row(
                children: [
                  Expanded(
                    child: _dropdown(
                      'Year',
                      year,
                      years,
                      (value) => setState(() => year = value),
                    ),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: _dropdown('Quarter', quarter, const [
                      '1',
                      '2',
                      '3',
                      '4',
                    ], (value) => setState(() => quarter = value)),
                  ),
                ],
              ),
              Align(
                alignment: Alignment.centerRight,
                child: TextButton(
                  onPressed: () => setState(() {
                    province = '';
                    tikina = '';
                    village = '';
                    year = '';
                    quarter = '';
                  }),
                  child: const Text('Clear filters'),
                ),
              ),
              Text(
                '${filtered.length} matching reports',
                style: Theme.of(context).textTheme.titleMedium,
              ),
              if (filtered.isEmpty)
                const Padding(
                  padding: EdgeInsets.all(32),
                  child: Text(
                    'No matching reports.',
                    textAlign: TextAlign.center,
                  ),
                ),
              for (final report in filtered)
                Card(
                  child: ListTile(
                    leading: const Icon(Icons.photo_library_outlined),
                    title: Text(
                      report['village_name']?.toString() ?? 'Village report',
                    ),
                    subtitle: Text(
                      '${report['province_name']} · ${report['tikina_name']}\n${report['period_label']} · ${report['status_label']}',
                    ),
                    trailing: const Icon(Icons.chevron_right),
                    onTap: () => Navigator.push(
                      context,
                      MaterialPageRoute<void>(
                        builder: (_) =>
                            PhotoReportGalleryScreen(report: report),
                      ),
                    ),
                  ),
                ),
            ],
          ),
        );
      },
    ),
  );

  List<String> _values(Iterable<Map<String, dynamic>> rows, String key) =>
      rows
          .map((item) => item[key]?.toString() ?? '')
          .where((item) => item.isNotEmpty)
          .toSet()
          .toList()
        ..sort();
  String _year(String label) =>
      RegExp(r'\b(20\d{2})\b').firstMatch(label)?.group(1) ?? '';
  Widget _dropdown(
    String label,
    String value,
    List<String> values,
    ValueChanged<String> changed,
  ) => Padding(
    padding: const EdgeInsets.only(bottom: 10),
    child: DropdownButtonFormField<String>(
      initialValue: value,
      decoration: InputDecoration(labelText: label),
      items: [
        const DropdownMenuItem(value: '', child: Text('All')),
        ...values.map(
          (item) => DropdownMenuItem(value: item, child: Text(item)),
        ),
      ],
      onChanged: (item) => changed(item ?? ''),
    ),
  );
  Widget _error(String text) => Center(
    child: Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(text, textAlign: TextAlign.center),
          FilledButton(
            onPressed: () => setState(() => revision++),
            child: const Text('Retry'),
          ),
        ],
      ),
    ),
  );
}

class PhotoReportGalleryScreen extends ConsumerStatefulWidget {
  const PhotoReportGalleryScreen({required this.report, super.key});
  final Map<String, dynamic> report;
  @override
  ConsumerState<PhotoReportGalleryScreen> createState() => _PhotoGalleryState();
}

class _PhotoGalleryState extends ConsumerState<PhotoReportGalleryScreen> {
  static const areas = <String, String>{
    'agriculture_food': 'Agriculture and food security',
    'ivdp_projects': 'IVDP projects',
    'housing_assets': 'Housing and village assets',
    'water': 'Water',
    'climate_disaster': 'Climate and disaster preparedness',
    'general': 'General report evidence',
  };
  String area = '', stage = '';
  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(
      title: Text(widget.report['village_name']?.toString() ?? 'Photo Report'),
    ),
    body: FutureBuilder<Map<String, dynamic>>(
      key: ValueKey((area, stage)),
      future: ref
          .read(photoReportsRepositoryProvider)
          .gallery(widget.report['uuid'].toString(), area: area, stage: stage),
      builder: (context, snapshot) {
        if (snapshot.connectionState != ConnectionState.done) {
          return const Center(child: CircularProgressIndicator());
        }
        if (snapshot.hasError) {
          return const Center(
            child: Text('The protected photo gallery could not be loaded.'),
          );
        }
        final rows = (snapshot.data!['results'] as List<dynamic>)
            .cast<Map<String, dynamic>>();
        return ListView(
          padding: const EdgeInsets.all(16),
          children: [
            Text(
              '${widget.report['period_label']} · ${snapshot.data!['total_photos']} total photos',
            ),
            const SizedBox(height: 12),
            DropdownButtonFormField<String>(
              initialValue: area,
              decoration: const InputDecoration(labelText: 'Area'),
              items: [
                const DropdownMenuItem(value: '', child: Text('All areas')),
                ...areas.entries.map(
                  (item) => DropdownMenuItem(
                    value: item.key,
                    child: Text(item.value),
                  ),
                ),
              ],
              onChanged: (value) => setState(() => area = value ?? ''),
            ),
            const SizedBox(height: 10),
            DropdownButtonFormField<String>(
              initialValue: stage,
              decoration: const InputDecoration(labelText: 'Progress stage'),
              items: const [
                DropdownMenuItem(value: '', child: Text('All stages')),
                DropdownMenuItem(
                  value: 'observation',
                  child: Text('Observation'),
                ),
                DropdownMenuItem(value: 'before', child: Text('Before')),
                DropdownMenuItem(value: 'progress', child: Text('Progress')),
                DropdownMenuItem(value: 'after', child: Text('After')),
                DropdownMenuItem(
                  value: 'unspecified',
                  child: Text('Not specified'),
                ),
              ],
              onChanged: (value) => setState(() => stage = value ?? ''),
            ),
            const SizedBox(height: 12),
            Text(
              '${rows.length} matching photos',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            for (final row in rows) _photo(row),
            if (rows.isEmpty)
              const Padding(
                padding: EdgeInsets.all(32),
                child: Text(
                  'No photos match these filters.',
                  textAlign: TextAlign.center,
                ),
              ),
          ],
        );
      },
    ),
  );

  Widget _photo(Map<String, dynamic> row) => Card(
    margin: const EdgeInsets.only(top: 12),
    clipBehavior: Clip.antiAlias,
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _ProtectedImage(url: row['image_url'].toString()),
        Padding(
          padding: const EdgeInsets.all(12),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Wrap(
                spacing: 8,
                children: [
                  Chip(label: Text(row['area_label'].toString())),
                  Chip(label: Text(row['stage_label'].toString())),
                ],
              ),
              Text(
                row['title'].toString(),
                style: Theme.of(context).textTheme.titleMedium,
              ),
              if ((row['description'] ?? '').toString().isNotEmpty)
                Text(row['description'].toString()),
              Text('Captured: ${_date(row['captured_at'])}'),
              Text('Confidentiality: ${row['confidentiality_level']}'),
              if (row['latitude'] != null)
                Text(
                  'GPS: ${row['latitude']}, ${row['longitude']}${row['location_accuracy_metres'] == null ? '' : ' (±${row['location_accuracy_metres']} m)'}',
                ),
              Text(
                '${row['record_label']}${(row['record_identifier'] ?? '').toString().isEmpty ? '' : ' · Record ${row['record_identifier']}'}',
              ),
            ],
          ),
        ),
      ],
    ),
  );
  String _date(Object? value) {
    final parsed = DateTime.tryParse(value?.toString() ?? '');
    return parsed == null
        ? 'Not recorded'
        : '${parsed.toLocal().day}/${parsed.toLocal().month}/${parsed.toLocal().year} ${parsed.toLocal().hour.toString().padLeft(2, '0')}:${parsed.toLocal().minute.toString().padLeft(2, '0')}';
  }
}

class _ProtectedImage extends ConsumerWidget {
  const _ProtectedImage({required this.url});
  final String url;
  @override
  Widget build(BuildContext context, WidgetRef ref) => FutureBuilder<Uint8List>(
    future: ref.read(photoReportsRepositoryProvider).image(url),
    builder: (context, snapshot) {
      if (!snapshot.hasData) {
        return const AspectRatio(
          aspectRatio: 16 / 9,
          child: Center(child: CircularProgressIndicator()),
        );
      }
      final image = Image.memory(
        snapshot.data!,
        fit: BoxFit.cover,
        width: double.infinity,
        errorBuilder: (_, _, _) => const SizedBox(
          height: 180,
          child: Center(child: Icon(Icons.broken_image_outlined)),
        ),
      );
      return GestureDetector(
        onTap: () => showDialog<void>(
          context: context,
          builder: (_) => Dialog(
            child: InteractiveViewer(child: Image.memory(snapshot.data!)),
          ),
        ),
        child: SizedBox(height: 220, width: double.infinity, child: image),
      );
    },
  );
}
