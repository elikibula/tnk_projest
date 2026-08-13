import 'package:dio/dio.dart';

abstract interface class DashboardRemoteDataSource {
  Future<Map<String, dynamic>> load(String token, {String? reportUuid});
  Future<Map<String, dynamic>> start(
    String token,
    String villageUuid,
    String periodUuid,
  );
}

class DioDashboardRemoteDataSource implements DashboardRemoteDataSource {
  DioDashboardRemoteDataSource(this._dio);
  final Dio _dio;
  Options _options(String token) =>
      Options(headers: {'Authorization': 'Bearer $token'});
  @override
  Future<Map<String, dynamic>> load(String token, {String? reportUuid}) async =>
      (await _dio.get<Map<String, dynamic>>(
        'dashboard/',
        queryParameters: reportUuid == null
            ? null
            : {'report_uuid': reportUuid},
        options: _options(token),
      )).data!;
  @override
  Future<Map<String, dynamic>> start(
    String token,
    String villageUuid,
    String periodUuid,
  ) async => (await _dio.post<Map<String, dynamic>>(
    'reports/',
    data: {'village_uuid': villageUuid, 'reporting_period_uuid': periodUuid},
    options: _options(token),
  )).data!;
}
