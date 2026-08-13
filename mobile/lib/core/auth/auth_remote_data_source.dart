import 'dart:io';

import 'package:dio/dio.dart';
import 'package:package_info_plus/package_info_plus.dart';

import 'auth_failures.dart';
import 'auth_models.dart';

class LoginResult {
  const LoginResult({required this.user, required this.tokens});
  final AuthUser user;
  final AuthTokens tokens;
}

abstract interface class AuthRemoteDataSource {
  Future<LoginResult> login({
    required String username,
    required String password,
    required String installationId,
  });
  Future<AuthTokens> refresh(AuthTokens current);
  Future<void> logout(AuthTokens current);
}

class DioAuthRemoteDataSource implements AuthRemoteDataSource {
  DioAuthRemoteDataSource(
    this._dio, {
    Future<PackageInfo> Function()? packageInfo,
  }) : _packageInfo = packageInfo ?? PackageInfo.fromPlatform;

  final Dio _dio;
  final Future<PackageInfo> Function() _packageInfo;

  @override
  Future<LoginResult> login({
    required String username,
    required String password,
    required String installationId,
  }) async {
    try {
      final info = await _packageInfo();
      final response = await _dio.post<Map<String, dynamic>>(
        'auth/login/',
        data: {
          'username': username,
          'password': password,
          'device_identifier': installationId,
          'platform': Platform.isIOS ? 'ios' : 'android',
          'app_version': _apiAppVersion(info),
          'device_name': Platform.operatingSystem,
        },
      );
      final data = response.data!;
      final policy = data['version_policy'] as Map<String, dynamic>?;
      if (policy?['force_upgrade'] == true) {
        throw const UpgradeRequiredFailure();
      }
      final tokens = _tokens(data);
      final me = await _dio.get<Map<String, dynamic>>(
        'me/',
        options: Options(
          headers: {'Authorization': 'Bearer ${tokens.accessToken}'},
        ),
      );
      return LoginResult(user: AuthUser.fromJson(me.data!), tokens: tokens);
    } on AuthFailure {
      rethrow;
    } on DioException catch (error) {
      throw _mapFailure(error, duringLogin: true);
    } on Object {
      throw const UnexpectedAuthFailure();
    }
  }

  @override
  Future<AuthTokens> refresh(AuthTokens current) async {
    try {
      final response = await _dio.post<Map<String, dynamic>>(
        'auth/refresh/',
        data: {'refresh': current.refreshToken},
      );
      final data = response.data!;
      return AuthTokens(
        accessToken: data['access'] as String,
        refreshToken: data['refresh'] as String? ?? current.refreshToken,
        deviceUuid: current.deviceUuid,
      );
    } on DioException catch (error) {
      throw _mapFailure(error);
    } on Object {
      throw const UnexpectedAuthFailure();
    }
  }

  @override
  Future<void> logout(AuthTokens current) async {
    try {
      await _dio.post<void>(
        'auth/logout/',
        data: {'refresh': current.refreshToken},
        options: Options(
          headers: {'Authorization': 'Bearer ${current.accessToken}'},
        ),
      );
    } on DioException catch (error) {
      throw _mapFailure(error);
    }
  }

  AuthTokens _tokens(Map<String, dynamic> data) => AuthTokens(
    accessToken: data['access'] as String,
    refreshToken: data['refresh'] as String,
    deviceUuid: data['device_uuid'].toString(),
  );

  AuthFailure _mapFailure(DioException error, {bool duringLogin = false}) {
    if ({
      DioExceptionType.connectionTimeout,
      DioExceptionType.sendTimeout,
      DioExceptionType.receiveTimeout,
      DioExceptionType.connectionError,
    }.contains(error.type)) {
      return const AuthNetworkFailure();
    }
    final status = error.response?.statusCode;
    final body = error.response?.data.toString().toLowerCase() ?? '';
    if (body.contains('revoked')) return const DeviceRevokedFailure();
    if (duringLogin && (status == 400 || status == 401)) {
      final validation = _loginValidationFailure(error.response?.data);
      if (validation != null) return validation;
      return const InvalidCredentialsFailure();
    }
    if (status == 401 || status == 400) return const SessionExpiredFailure();
    return const UnexpectedAuthFailure();
  }

  String _apiAppVersion(PackageInfo info) {
    // Android flavor suffixes (for example, 1.0.0-development) are useful for
    // package identification but are not part of the mobile API version
    // contract. Send the pubspec semantic version and numeric build only.
    final semanticVersion = RegExp(
      r'^\d+\.\d+\.\d+',
    ).firstMatch(info.version)?.group(0);
    final version = semanticVersion ?? info.version;
    final build = RegExp(r'^\d+$').hasMatch(info.buildNumber)
        ? '+${info.buildNumber}'
        : '';
    return '$version$build';
  }

  AuthValidationFailure? _loginValidationFailure(Object? data) {
    if (data is! Map) return null;
    if (data.containsKey('credentials')) return null;

    final messages = <String>[];
    for (final entry in data.entries) {
      final field = entry.key.toString();
      if (field == 'code' || field == 'password') continue;
      final value = entry.value;
      if (value is List) {
        messages.addAll(value.map((message) => '$field: $message'));
      } else if (value != null) {
        messages.add('$field: $value');
      }
    }
    if (messages.isEmpty) return null;
    return AuthValidationFailure(messages.join(' '));
  }
}
