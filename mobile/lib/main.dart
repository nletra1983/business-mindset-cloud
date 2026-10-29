import 'package:flutter/material.dart';

import 'channel_client.dart';
import 'session_store.dart';

/// Базовый URL того же хоста, что у бота. Задаётся при сборке:
/// `--dart-define=CHANNEL_BASE_URL=https://your-host`
const channelBaseUrl = String.fromEnvironment(
  'CHANNEL_BASE_URL',
  defaultValue: 'http://127.0.0.1:8080',
);

void main() {
  runApp(const BusinessMindsetApp());
}

class BusinessMindsetApp extends StatelessWidget {
  const BusinessMindsetApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Business Mindset',
      home: EntryShell(
        client: ChannelClient(baseUrl: channelBaseUrl),
        sessions: SessionStore(),
      ),
    );
  }
}

/// Тонкий каркас входа. Полные экраны — истории №5–№8.
class EntryShell extends StatefulWidget {
  const EntryShell({super.key, required this.client, required this.sessions});

  final ChannelClient client;
  final SessionStore sessions;

  @override
  State<EntryShell> createState() => _EntryShellState();
}

class _EntryShellState extends State<EntryShell> {
  final _email = TextEditingController();
  final _code = TextEditingController();
  String _status = 'Укажи email. Клиент ходит только в /app/v1.';
  bool _inside = false;
  List<dynamic> _runs = const [];

  @override
  void initState() {
    super.initState();
    _restore();
  }

  Future<void> _restore() async {
    final secret = await widget.sessions.get();
    if (secret == null) return;
    final result = await widget.client.listRuns(secret);
    if (result['statusCode'] == 200) {
      setState(() {
        _inside = true;
        _runs = (result['body'] as Map)['runs'] as List<dynamic>? ?? const [];
        _status = _runs.isEmpty ? 'Ходов пока нет.' : 'Список ходов.';
      });
    } else {
      await widget.sessions.clear();
    }
  }

  Future<void> _requestCode() async {
    final result = await widget.client.requestEmailCode(_email.text.trim());
    setState(() {
      _status = result['statusCode'] == 200
          ? 'Пришли код из письма.'
          : 'Код не отправлен.';
    });
  }

  Future<void> _confirm() async {
    final result = await widget.client.confirmEmailCode(
      _email.text.trim(),
      _code.text.trim(),
    );
    if (result['statusCode'] != 200) {
      setState(() => _status = 'Код не подошёл.');
      return;
    }
    final secret = (result['body'] as Map)['session_secret'] as String;
    await widget.sessions.put(secret);
    setState(() {
      _inside = true;
      _runs = (result['body'] as Map)['runs'] as List<dynamic>? ?? const [];
      _status = _runs.isEmpty ? 'Ходов пока нет.' : 'Список ходов.';
    });
  }

  Future<void> _logout() async {
    final secret = await widget.sessions.get();
    if (secret != null) {
      await widget.client.logout(secret);
    }
    await widget.sessions.clear();
    setState(() {
      _inside = false;
      _runs = const [];
      _status = 'Вышел. Нужен новый код.';
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Business Mindset')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(_status),
            if (!_inside) ...[
              TextField(
                controller: _email,
                decoration: const InputDecoration(labelText: 'Email'),
                keyboardType: TextInputType.emailAddress,
              ),
              TextField(
                controller: _code,
                decoration: const InputDecoration(labelText: 'Код'),
              ),
              ElevatedButton(onPressed: _requestCode, child: const Text('Запросить код')),
              ElevatedButton(onPressed: _confirm, child: const Text('Подтвердить')),
            ] else ...[
              Expanded(
                child: ListView(
                  children: _runs.map((run) => ListTile(title: Text('$run'))).toList(),
                ),
              ),
              ElevatedButton(onPressed: _logout, child: const Text('Выйти')),
            ],
          ],
        ),
      ),
    );
  }
}
