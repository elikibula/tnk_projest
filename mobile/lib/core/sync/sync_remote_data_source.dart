import 'package:dio/dio.dart';

import '../auth/auth_failures.dart';
import 'sync_models.dart';

class SyncBatchResponse {
  const SyncBatchResponse(this.accepted, this.conflicts, this.failed);
  final List<Map<String, dynamic>> accepted;
  final List<Map<String, dynamic>> conflicts;
  final List<Map<String, dynamic>> failed;
}

class SyncChangesResponse {
  const SyncChangesResponse(
    this.nextCursor,
    this.changes,
    this.deletions, {
    this.hasMore = false,
  });
  final String nextCursor;
  final List<Map<String, dynamic>> changes;
  final List<Map<String, dynamic>> deletions;
  final bool hasMore;
}

abstract interface class SyncRemoteDataSource {
  Future<SyncBatchResponse> upload(
    String accessToken,
    List<Map<String, dynamic>> changes,
  );
  Future<SyncChangesResponse> download(String accessToken, String? cursor);
}

class DioSyncRemoteDataSource implements SyncRemoteDataSource {
  DioSyncRemoteDataSource(this._dio);
  final Dio _dio;

  @override
  Future<SyncBatchResponse> upload(
    String accessToken,
    List<Map<String, dynamic>> changes,
  ) async {
    final data = await _request(
      () => _dio.post<Map<String, dynamic>>(
        'sync/batch/',
        data: {'changes': changes},
        options: Options(headers: {'Authorization': 'Bearer $accessToken'}),
      ),
    );
    return SyncBatchResponse(
      _objects(data['accepted']),
      _objects(data['conflicts']),
      _objects(data['failed']),
    );
  }

  @override
  Future<SyncChangesResponse> download(
    String accessToken,
    String? cursor,
  ) async {
    final data = await _request(
      () => _dio.get<Map<String, dynamic>>(
        'sync/changes/',
        queryParameters: cursor == null ? null : {'cursor': cursor},
        options: Options(headers: {'Authorization': 'Bearer $accessToken'}),
      ),
    );
    return SyncChangesResponse(
      data['next_cursor'] as String,
      _objects(data['changes']),
      _objects(data['deletions']),
      hasMore: data['has_more'] as bool? ?? false,
    );
  }

  Future<Map<String, dynamic>> _request(
    Future<Response<Map<String, dynamic>>> Function() request,
  ) async {
    try {
      return (await request()).data!;
    } on DioException catch (error) {
      if ({
        DioExceptionType.connectionTimeout,
        DioExceptionType.sendTimeout,
        DioExceptionType.receiveTimeout,
        DioExceptionType.connectionError,
      }.contains(error.type)) {
        throw const SyncNetworkFailure();
      }
      if (error.response?.statusCode == 401) {
        throw const SessionExpiredFailure();
      }
      if (error.response?.statusCode == 403) {
        throw const DeviceRevokedFailure();
      }
      throw const SyncUnexpectedFailure();
    }
  }

  List<Map<String, dynamic>> _objects(Object? values) =>
      (values as List<dynamic>? ?? const [])
          .map((value) => Map<String, dynamic>.from(value as Map))
          .toList(growable: false);
}
