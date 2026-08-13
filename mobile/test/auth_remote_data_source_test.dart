import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:package_info_plus/package_info_plus.dart';
import 'package:tnk_insight_mobile/core/auth/auth_failures.dart';
import 'package:tnk_insight_mobile/core/auth/auth_remote_data_source.dart';

void main() {
  test('login sends the backend contract and parses login plus me', () async {
    final requests = <RequestOptions>[];
    final dio = _stubDio((options) {
      requests.add(options);
      if (options.path.endsWith('auth/login/')) {
        return _response(options, {
          'access': 'access-token',
          'refresh': 'refresh-token',
          'device_uuid': '11111111-2222-4333-8444-555555555555',
          'version_policy': {
            'minimum_supported_version': '1.0.0',
            'latest_version': '1.0.0',
            'force_upgrade': false,
            'update_available': false,
          },
        });
      }
      return _response(options, {
        'uuid': 'aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee',
        'username': 'demo_tnk_a1',
        'full_name': 'Demo TNK',
        'preferred_language': 'en',
        'roles': ['turaga_ni_koro'],
        'location_assignments': <Object>[],
        'record_version': 1,
      });
    });
    final remote = DioAuthRemoteDataSource(
      dio,
      packageInfo: () async => _packageInfo(version: '1.0.0-development'),
    );

    final result = await remote.login(
      username: 'demo_tnk_a1',
      password: 'fictional-password',
      installationId: '11111111-2222-4333-8444-555555555555',
    );

    final login = requests.first;
    expect(login.method, 'POST');
    expect(login.path, 'auth/login/');
    expect(login.contentType, Headers.jsonContentType);
    expect(login.data, {
      'username': 'demo_tnk_a1',
      'password': 'fictional-password',
      'device_identifier': '11111111-2222-4333-8444-555555555555',
      'platform': 'android',
      'app_version': '1.0.0+1',
      'device_name': 'windows',
    });
    expect(requests.last.path, 'me/');
    expect(requests.last.headers['Authorization'], 'Bearer access-token');
    expect(result.tokens.refreshToken, 'refresh-token');
    expect(result.user.roles, ['turaga_ni_koro']);
  });

  test(
    '400 field validation is surfaced without exposing password data',
    () async {
      final remote = DioAuthRemoteDataSource(
        _errorDio(400, {
          'code': 'invalid',
          'app_version': [
            'Use semantic version format such as 1.2.3 or 1.2.3+45.',
          ],
        }),
        packageInfo: () async => _packageInfo(version: 'invalid-development'),
      );

      await expectLater(
        remote.login(
          username: 'user',
          password: 'secret',
          installationId: '11111111-2222-4333-8444-555555555555',
        ),
        throwsA(
          isA<AuthValidationFailure>().having(
            (failure) => failure.message,
            'message',
            contains('app_version: Use semantic version format'),
          ),
        ),
      );
    },
  );

  test(
    '400 credential and 401 login responses remain credential failures',
    () async {
      for (final stub in <Dio>[
        _errorDio(400, {
          'code': 'invalid',
          'credentials': ['Unable to sign in with the supplied credentials.'],
        }),
        _errorDio(401, {'code': 'not_authenticated'}),
      ]) {
        final remote = DioAuthRemoteDataSource(
          stub,
          packageInfo: () async => _packageInfo(),
        );
        await expectLater(
          remote.login(
            username: 'user',
            password: 'secret',
            installationId: '11111111-2222-4333-8444-555555555555',
          ),
          throwsA(isA<InvalidCredentialsFailure>()),
        );
      }
    },
  );
}

PackageInfo _packageInfo({String version = '1.0.0'}) => PackageInfo(
  appName: 'TNK Insight Dev',
  packageName: 'fj.gov.tnk.tnk_insight_mobile.development',
  version: version,
  buildNumber: '1',
  buildSignature: '',
  installerStore: null,
);

Dio _stubDio(Response<dynamic> Function(RequestOptions) response) {
  final dio = Dio(BaseOptions(baseUrl: 'http://example.test/api/v1/'));
  dio.interceptors.add(
    InterceptorsWrapper(
      onRequest: (options, handler) => handler.resolve(response(options)),
    ),
  );
  return dio;
}

Dio _errorDio(int statusCode, Object data) {
  final dio = Dio(BaseOptions(baseUrl: 'http://example.test/api/v1/'));
  dio.interceptors.add(
    InterceptorsWrapper(
      onRequest: (options, handler) => handler.reject(
        DioException.badResponse(
          statusCode: statusCode,
          requestOptions: options,
          response: _response(options, data, statusCode: statusCode),
        ),
      ),
    ),
  );
  return dio;
}

Response<dynamic> _response(
  RequestOptions options,
  Object data, {
  int statusCode = 200,
}) => Response<dynamic>(
  requestOptions: options,
  statusCode: statusCode,
  data: data,
);
