import 'package:dio/dio.dart';

import '../auth/auth_failures.dart';
import 'bootstrap_failures.dart';
import 'bootstrap_models.dart';

abstract interface class BootstrapRemoteDataSource {
  Future<BootstrapBundle> download(String accessToken);
}

class DioBootstrapRemoteDataSource implements BootstrapRemoteDataSource {
  DioBootstrapRemoteDataSource(this._dio);
  final Dio _dio;

  @override
  Future<BootstrapBundle> download(String accessToken) async {
    try {
      final response = await _dio.get<Map<String, dynamic>>(
        'sync/bootstrap/',
        options: Options(headers: {'Authorization': 'Bearer $accessToken'}),
      );
      final bundle = BootstrapBundle.fromJson(response.data!);
      final policy = bundle.device['version_policy'] as Map<String, dynamic>?;
      if (policy?['force_upgrade'] == true || bundle.schemaVersion != 1) {
        throw const BootstrapUpgradeRequiredFailure();
      }
      return bundle;
    } on BootstrapFailure {
      rethrow;
    } on DioException catch (error) {
      if ({
        DioExceptionType.connectionTimeout,
        DioExceptionType.sendTimeout,
        DioExceptionType.receiveTimeout,
        DioExceptionType.connectionError,
      }.contains(error.type)) {
        throw const BootstrapNetworkFailure();
      }
      final body = error.response?.data.toString().toLowerCase() ?? '';
      if (body.contains('revoked')) throw const DeviceRevokedFailure();
      if (error.response?.statusCode == 401) {
        throw const SessionExpiredFailure();
      }
      throw const BootstrapUnexpectedFailure();
    } on FormatException {
      throw const BootstrapUnexpectedFailure();
    } on TypeError {
      throw const BootstrapUnexpectedFailure();
    }
  }
}
