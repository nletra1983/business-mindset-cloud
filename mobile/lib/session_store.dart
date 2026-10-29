import 'package:flutter_secure_storage/flutter_secure_storage.dart';

/// Секрет сессии в аппаратном хранилище платформы (история №3).
class SessionStore {
  SessionStore({FlutterSecureStorage? storage})
      : _storage = storage ?? const FlutterSecureStorage();

  static const _key = 'session_secret';
  final FlutterSecureStorage _storage;

  Future<void> put(String secret) => _storage.write(key: _key, value: secret);

  Future<String?> get() => _storage.read(key: _key);

  Future<void> clear() => _storage.delete(key: _key);
}
