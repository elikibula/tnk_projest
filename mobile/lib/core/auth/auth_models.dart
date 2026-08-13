import 'dart:convert';

class AuthUser {
  const AuthUser({
    required this.uuid,
    required this.username,
    required this.fullName,
    required this.preferredLanguage,
    required this.roles,
  });

  factory AuthUser.fromJson(Map<String, dynamic> json) => AuthUser(
    uuid: json['uuid'] as String,
    username: json['username'] as String,
    fullName: json['full_name'] as String? ?? '',
    preferredLanguage: json['preferred_language'] as String? ?? 'en',
    roles: List<String>.unmodifiable(
      (json['roles'] as List<dynamic>? ?? const []).cast<String>(),
    ),
  );

  final String uuid;
  final String username;
  final String fullName;
  final String preferredLanguage;
  final List<String> roles;

  Map<String, dynamic> toJson() => {
    'uuid': uuid,
    'username': username,
    'full_name': fullName,
    'preferred_language': preferredLanguage,
    'roles': roles,
  };
}

class AuthTokens {
  const AuthTokens({
    required this.accessToken,
    required this.refreshToken,
    required this.deviceUuid,
  });

  final String accessToken;
  final String refreshToken;
  final String deviceUuid;

  DateTime? get accessExpiresAt => _jwtExpiry(accessToken);

  Map<String, dynamic> toJson() => {
    'access_token': accessToken,
    'refresh_token': refreshToken,
    'device_uuid': deviceUuid,
  };

  factory AuthTokens.fromJson(Map<String, dynamic> json) => AuthTokens(
    accessToken: json['access_token'] as String,
    refreshToken: json['refresh_token'] as String,
    deviceUuid: json['device_uuid'] as String,
  );
}

class AuthSession {
  const AuthSession({
    required this.user,
    required this.tokens,
    required this.establishedAt,
    required this.offlineValidUntil,
    this.isOffline = false,
  });

  final AuthUser user;
  final AuthTokens tokens;
  final DateTime establishedAt;
  final DateTime offlineValidUntil;
  final bool isOffline;

  AuthSession copyWith({AuthTokens? tokens, bool? isOffline}) => AuthSession(
    user: user,
    tokens: tokens ?? this.tokens,
    establishedAt: establishedAt,
    offlineValidUntil: offlineValidUntil,
    isOffline: isOffline ?? this.isOffline,
  );

  Map<String, dynamic> toJson() => {
    'user': user.toJson(),
    'tokens': tokens.toJson(),
    'established_at': establishedAt.toUtc().toIso8601String(),
    'offline_valid_until': offlineValidUntil.toUtc().toIso8601String(),
  };

  factory AuthSession.fromJson(Map<String, dynamic> json) => AuthSession(
    user: AuthUser.fromJson(json['user'] as Map<String, dynamic>),
    tokens: AuthTokens.fromJson(json['tokens'] as Map<String, dynamic>),
    establishedAt: DateTime.parse(json['established_at'] as String),
    offlineValidUntil: DateTime.parse(json['offline_valid_until'] as String),
  );
}

DateTime? _jwtExpiry(String token) {
  try {
    final parts = token.split('.');
    if (parts.length != 3) return null;
    final payload =
        jsonDecode(utf8.decode(base64Url.decode(base64Url.normalize(parts[1]))))
            as Map<String, dynamic>;
    final seconds = payload['exp'] as int?;
    return seconds == null
        ? null
        : DateTime.fromMillisecondsSinceEpoch(seconds * 1000, isUtc: true);
  } on FormatException {
    return null;
  }
}
