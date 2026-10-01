import 'package:dio/dio.dart';

/// Retries a rejected access token once. Refresh requests use a separate client.
class SessionInterceptor extends Interceptor {
  SessionInterceptor(
    this.dio, {
    required this.currentToken,
    required this.refresh,
    required this.expire,
  });
  final Dio dio;
  final String? Function() currentToken;
  final Future<String> Function() refresh;
  final Future<void> Function() expire;
  Future<String>? _refreshing;

  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) {
    final base = Uri.parse(dio.options.baseUrl);
    if (options.uri.origin != base.origin ||
        !options.uri.path.startsWith(base.path)) {
      handler.reject(
        DioException(requestOptions: options, type: DioExceptionType.cancel),
      );
      return;
    }
    final token = currentToken();
    if (token == null) {
      handler.reject(
        DioException(requestOptions: options, type: DioExceptionType.cancel),
      );
      return;
    }
    options.headers['Authorization'] = 'Bearer $token';
    handler.next(options);
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) async {
    if (err.response?.statusCode != 401) {
      handler.next(err);
      return;
    }
    if (err.requestOptions.extra['sessionRetried'] == true) {
      await expire();
      handler.next(err);
      return;
    }
    try {
      final rejected = err.requestOptions.headers['Authorization'];
      var token = currentToken();
      if (token == null) {
        handler.next(err);
        return;
      }
      if (rejected == 'Bearer $token') {
        final pending = _refreshing ??= refresh();
        try {
          token = await pending;
        } on Object {
          await expire();
          handler.next(err);
          return;
        } finally {
          if (identical(_refreshing, pending)) _refreshing = null;
        }
      }
      final options = err.requestOptions;
      final data = options.data;
      try {
        final response = await dio.fetch<dynamic>(
          options.copyWith(
            data: data is FormData ? data.clone() : data,
            headers: {...options.headers, 'Authorization': 'Bearer $token'},
            extra: {...options.extra, 'sessionRetried': true},
          ),
        );
        handler.resolve(response);
      } on DioException catch (retryError) {
        handler.next(retryError);
      }
    } on Object {
      handler.next(err);
    }
  }
}
