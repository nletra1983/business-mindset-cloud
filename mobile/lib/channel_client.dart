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

  Future<Map<String, dynamic>> logout(String sessionSecret) async {
    final response = await _http.post(
      _uri('/auth/logout'),
      headers: {'Authorization': 'Bearer $sessionSecret'},
    );
    return _decode(response);
  }

  Map<String, dynamic> _decode(http.Response response) {
    final body = response.body.isEmpty ? <String, dynamic>{} : jsonDecode(response.body) as Map<String, dynamic>;
    return {'statusCode': response.statusCode, 'body': body};
  }
}
