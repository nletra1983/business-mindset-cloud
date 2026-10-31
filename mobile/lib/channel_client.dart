import 'dart:convert';

import 'package:http/http.dart' as http;

/// Клиент входа каналов `/app/v1`. Не ходит в Telegram API и не вызывает модель.
class ChannelClient {
  ChannelClient({required this.baseUrl, http.Client? httpClient})
      : _http = httpClient ?? http.Client();

  /// Например `https://example.ru` — тот же хост сервиса бота.
  final String baseUrl;
  final http.Client _http;

  static const prefix = '/app/v1';

  Uri _uri(String path) => Uri.parse('$baseUrl$prefix$path');

  Future<Map<String, dynamic>> requestEmailCode(String email) async {
    final response = await _http.post(
      _uri('/auth/email/request'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'email': email}),
    );
    return _decode(response);
  }

  Future<Map<String, dynamic>> confirmEmailCode(String email, String code) async {
    final response = await _http.post(
      _uri('/auth/email/confirm'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'email': email, 'code': code}),
    );
    return _decode(response);
  }

  Future<Map<String, dynamic>> listRuns(String sessionSecret) async {
    final response = await _http.get(
      _uri('/runs'),
      headers: {'Authorization': 'Bearer $sessionSecret'},
    );
    return _decode(response);
  }

  Future<Map<String, dynamic>> leaveToList(String sessionSecret) async {
    final response = await _http.post(
      _uri('/runs/leave'),
      headers: {'Authorization': 'Bearer $sessionSecret'},
    );
    return _decode(response);
  }

  Future<Map<String, dynamic>> startRun(
    String sessionSecret,
    String topic, {
    String? idempotencyKey,
  }) async {
    final headers = <String, String>{
      'Authorization': 'Bearer $sessionSecret',
      'Content-Type': 'application/json',
    };
    if (idempotencyKey != null && idempotencyKey.isNotEmpty) {
      headers['Idempotency-Key'] = idempotencyKey;
    }
    final response = await _http.post(
      _uri('/runs'),
      headers: headers,
      body: jsonEncode({'topic': topic}),
    );
    return _decode(response);
  }

  Future<Map<String, dynamic>> resumeRun(String sessionSecret, String runId) async {
    final response = await _http.post(
      _uri('/runs/$runId/resume'),
      headers: {'Authorization': 'Bearer $sessionSecret'},
    );
    return _decode(response);
  }

  Future<Map<String, dynamic>> answerRun(
    String sessionSecret,
    String runId,
    String text, {
    String? idempotencyKey,
  }) async {
    final headers = <String, String>{
      'Authorization': 'Bearer $sessionSecret',
      'Content-Type': 'application/json',
    };
    if (idempotencyKey != null && idempotencyKey.isNotEmpty) {
      headers['Idempotency-Key'] = idempotencyKey;
    }
    final response = await _http.post(
      _uri('/runs/$runId/answers'),
      headers: headers,
      body: jsonEncode({'text': text}),
    );
    return _decode(response);
  }

  Future<Map<String, dynamic>> logout(String sessionSecret) async {
    final response = await _http.post(
      _uri('/auth/logout'),
      headers: {'Authorization': 'Bearer $sessionSecret'},
    );
    return _decode(response);
  }

  Future<Map<String, dynamic>> openSettings(String sessionSecret) async {
    final response = await _http.get(
      _uri('/settings'),
      headers: {'Authorization': 'Bearer $sessionSecret'},
    );
    return _decode(response);
  }

  Future<Map<String, dynamic>> getModels(String sessionSecret) async {
    final response = await _http.get(
      _uri('/settings/models'),
      headers: {'Authorization': 'Bearer $sessionSecret'},
    );
    return _decode(response);
  }

  Future<Map<String, dynamic>> chooseModel(String sessionSecret, String modelId) async {
    final response = await _http.post(
      _uri('/settings/models'),
      headers: {
        'Authorization': 'Bearer $sessionSecret',
        'Content-Type': 'application/json',
      },
      body: jsonEncode({'model_id': modelId}),
    );
    return _decode(response);
  }

  Future<Map<String, dynamic>> getProfile(String sessionSecret) async {
    final response = await _http.get(
      _uri('/settings/profile'),
      headers: {'Authorization': 'Bearer $sessionSecret'},
    );
    return _decode(response);
  }

  Future<Map<String, dynamic>> saveProfileStrengths(String sessionSecret, String text) async {
    return _postProfilePart(sessionSecret, '/settings/profile/strengths', text);
  }

  Future<Map<String, dynamic>> saveProfileWeaknesses(String sessionSecret, String text) async {
    return _postProfilePart(sessionSecret, '/settings/profile/weaknesses', text);
  }

  Future<Map<String, dynamic>> saveProfileFact(String sessionSecret, String text) async {
    return _postProfilePart(sessionSecret, '/settings/profile/fact', text);
  }

  Future<Map<String, dynamic>> openSecondEntrance(String sessionSecret) async {
    final response = await _http.get(
      _uri('/settings/second-entrance'),
      headers: {'Authorization': 'Bearer $sessionSecret'},
    );
    return _decode(response);
  }

  Future<Map<String, dynamic>> submitSecondEmail(String sessionSecret, String email) async {
    final response = await _http.post(
      _uri('/settings/second-entrance/email'),
      headers: {
        'Authorization': 'Bearer $sessionSecret',
        'Content-Type': 'application/json',
      },
      body: jsonEncode({'email': email}),
    );
    return _decode(response);
  }

  Future<Map<String, dynamic>> submitSecondTelegram(String sessionSecret, String telegram) async {
    final response = await _http.post(
      _uri('/settings/second-entrance/telegram'),
      headers: {
        'Authorization': 'Bearer $sessionSecret',
        'Content-Type': 'application/json',
      },
      body: jsonEncode({'telegram': telegram}),
    );
    return _decode(response);
  }

  Future<Map<String, dynamic>> submitSecondCode(String sessionSecret, String code) async {
    final response = await _http.post(
      _uri('/settings/second-entrance/code'),
      headers: {
        'Authorization': 'Bearer $sessionSecret',
        'Content-Type': 'application/json',
      },
      body: jsonEncode({'code': code}),
    );
    return _decode(response);
  }

  Future<Map<String, dynamic>> _postProfilePart(
    String sessionSecret,
    String path,
    String text,
  ) async {
    final response = await _http.post(
      _uri(path),
      headers: {
        'Authorization': 'Bearer $sessionSecret',
        'Content-Type': 'application/json',
      },
      body: jsonEncode({'text': text}),
    );
    return _decode(response);
  }

  Map<String, dynamic> _decode(http.Response response) {
    final body = response.body.isEmpty
        ? <String, dynamic>{}
        : jsonDecode(response.body) as Map<String, dynamic>;
    return {'statusCode': response.statusCode, 'body': body};
  }
}
