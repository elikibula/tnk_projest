import 'package:dio/dio.dart';

import '../domain/validation_models.dart';

abstract interface class ValidationRemoteDataSource {
  Future<ValidationSnapshot> issues(String token, String reportUuid);
  Future<ValidationSnapshot> validate(String token, String reportUuid);
  Future<void> declare(String token, String reportUuid);
  Future<Map<String, dynamic>> transition(
    String token,
    String reportUuid,
    String action,
  );
  Future<Map<String, dynamic>> report(String token, String reportUuid);
}

class DioValidationRemoteDataSource implements ValidationRemoteDataSource {
  DioValidationRemoteDataSource(this._dio);
  final Dio _dio;
  Options _options(String token) =>
      Options(headers: {'Authorization': 'Bearer $token'});

  @override
  Future<ValidationSnapshot> issues(String token, String reportUuid) async =>
      ValidationSnapshot.fromJson(
        (await _dio.get<Map<String, dynamic>>(
          'reports/$reportUuid/validation/',
          options: _options(token),
        )).data!,
      );
  @override
  Future<ValidationSnapshot> validate(String token, String reportUuid) async =>
      ValidationSnapshot.fromJson(
        (await _dio.post<Map<String, dynamic>>(
          'reports/$reportUuid/validation/',
          options: _options(token),
        )).data!,
      );
  @override
  Future<void> declare(String token, String reportUuid) async {
    await _dio.post<Map<String, dynamic>>(
      'reports/$reportUuid/declaration/',
      data: const {'acknowledged': true},
      options: _options(token),
    );
  }

  @override
  Future<Map<String, dynamic>> transition(
    String token,
    String reportUuid,
    String action,
  ) async => (await _dio.post<Map<String, dynamic>>(
    'reports/$reportUuid/workflow/$action/',
    data: const {'acknowledged': true},
    options: _options(token),
  )).data!;
  @override
  Future<Map<String, dynamic>> report(String token, String reportUuid) async =>
      (await _dio.get<Map<String, dynamic>>(
        'reports/$reportUuid/',
        options: _options(token),
      )).data!;
}
