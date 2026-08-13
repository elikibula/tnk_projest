import 'package:dio/dio.dart';

abstract interface class EvidenceRemoteDataSource {
  Future<Map<String, dynamic>> upload({
    required String token,
    required String reportUuid,
    required String idempotencyKey,
    required String filename,
    required String mediaType,
    required List<int> bytes,
    required Map<String, dynamic> metadata,
  });
}

class EvidenceUploadFailure implements Exception {
  const EvidenceUploadFailure({required this.permanent});
  final bool permanent;
}

class DioEvidenceRemoteDataSource implements EvidenceRemoteDataSource {
  DioEvidenceRemoteDataSource(this._dio);
  final Dio _dio;

  @override
  Future<Map<String, dynamic>> upload({
    required String token,
    required String reportUuid,
    required String idempotencyKey,
    required String filename,
    required String mediaType,
    required List<int> bytes,
    required Map<String, dynamic> metadata,
  }) async {
    final form = FormData.fromMap({
      ...metadata.map((key, value) => MapEntry(key, value?.toString())),
      'file': MultipartFile.fromBytes(
        bytes,
        filename: filename,
        contentType: DioMediaType.parse(mediaType),
      ),
    });
    try {
      final response = await _dio.post<Map<String, dynamic>>(
        'reports/$reportUuid/evidence/',
        data: form,
        options: Options(
          headers: {
            'Authorization': 'Bearer $token',
            'Idempotency-Key': idempotencyKey,
          },
        ),
        onSendProgress: (_, _) {},
      );
      return response.data!;
    } on DioException catch (error) {
      final status = error.response?.statusCode;
      final permanent =
          status != null &&
          status >= 400 &&
          status < 500 &&
          status != 408 &&
          status != 429;
      throw EvidenceUploadFailure(permanent: permanent);
    }
  }
}
