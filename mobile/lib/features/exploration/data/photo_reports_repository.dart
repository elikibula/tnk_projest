import 'dart:typed_data';

import 'package:dio/dio.dart';

class PhotoReportsRepository {
  PhotoReportsRepository(this._dio);
  final Dio _dio;

  Future<List<Map<String, dynamic>>> reports() async {
    final output = <Map<String, dynamic>>[];
    var page = 1;
    while (true) {
      final data = (await _dio.get<Map<String, dynamic>>(
        'photo-reports/',
        queryParameters: {'page': page, 'page_size': 100},
      )).data!;
      output.addAll(
        (data['results'] as List<dynamic>).map(
          (item) => Map<String, dynamic>.from(item as Map),
        ),
      );
      if (data['next'] == null) break;
      page++;
    }
    return output;
  }

  Future<Map<String, dynamic>> gallery(
    String reportUuid, {
    String? area,
    String? stage,
  }) async {
    final output = <Map<String, dynamic>>[];
    Map<String, dynamic>? first;
    var page = 1;
    while (true) {
      final data = (await _dio.get<Map<String, dynamic>>(
        'photo-reports/$reportUuid/',
        queryParameters: {
          'page': page,
          'page_size': 100,
          if (area != null && area.isNotEmpty) 'area': area,
          if (stage != null && stage.isNotEmpty) 'stage': stage,
        },
      )).data!;
      first ??= data;
      output.addAll(
        (data['results'] as List<dynamic>).map(
          (item) => Map<String, dynamic>.from(item as Map),
        ),
      );
      if (data['next'] == null) break;
      page++;
    }
    return {...first, 'results': output};
  }

  Future<Uint8List> image(String url) async {
    final response = await _dio.get<List<int>>(
      url,
      options: Options(responseType: ResponseType.bytes),
    );
    return Uint8List.fromList(response.data!);
  }
}
