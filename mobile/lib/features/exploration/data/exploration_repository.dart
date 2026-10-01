import 'package:dio/dio.dart';

class LocationItem {
  const LocationItem({
    required this.uuid,
    required this.name,
    required this.level,
  });
  factory LocationItem.fromJson(Map<String, dynamic> value) => LocationItem(
    uuid: value['uuid'].toString(),
    name: value['name'].toString(),
    level: value['level'].toString(),
  );
  final String uuid, name, level;
}

class ExplorationRepository {
  ExplorationRepository(this._dio);
  final Dio _dio;
  Future<Map<String, dynamic>> analytics({
    String? period,
    String? level,
    String? location,
    String? comparePeriod,
    String? page,
  }) async => (await _dio.get<Map<String, dynamic>>(
    'analytics/',
    queryParameters: {
      'period': ?period,
      'level': ?level,
      'location': ?location,
      'compare_period': ?comparePeriod,
      'page': ?page,
    },
  )).data!;
  Future<List<LocationItem>> locations({
    required String level,
    String? parent,
    String query = '',
    int page = 1,
  }) async {
    final output = <LocationItem>[];
    var current = page;
    while (true) {
      final data = (await _dio.get<Map<String, dynamic>>(
        'locations/',
        queryParameters: {
          'level': level,
          'parent': ?parent,
          if (query.isNotEmpty) 'q': query,
          'page': current,
          'page_size': 100,
        },
      )).data!;
      output.addAll(
        (data['results'] as List<dynamic>).map(
          (item) =>
              LocationItem.fromJson(Map<String, dynamic>.from(item as Map)),
        ),
      );
      if (data['next'] == null) break;
      current++;
    }
    return output;
  }
}
