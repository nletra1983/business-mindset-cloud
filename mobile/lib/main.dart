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

/// Вход по email и список/ход (история 010). Настройки — другая история.
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
  final _topic = TextEditingController();
  final _answer = TextEditingController();
  String _status = 'Укажи email.\nСервер: $channelBaseUrl';
  bool _inside = false;
  bool _busy = false;
  List<Map<String, String>> _runs = const [];
  String? _openRunId;
  String? _openRunTopic;
  String? _answerIdempotencyKey;

  @override
  void initState() {
    super.initState();
    _restore();
  }

  @override
  void dispose() {
    _email.dispose();
    _code.dispose();
    _topic.dispose();
    _answer.dispose();
    super.dispose();
  }

  Future<void> _restore() async {
    final secret = await widget.sessions.get();
    if (secret == null) return;
    try {
      final ok = await _refreshRuns(secret);
      if (!ok) await widget.sessions.clear();
    } catch (_) {
      await widget.sessions.clear();
    }
  }

  List<Map<String, String>> _parseRuns(dynamic raw) {
    if (raw is! List) return const [];
    final out = <Map<String, String>>[];
    for (final item in raw) {
      if (item is Map) {
        final id = '${item['id'] ?? ''}';
        final topic = '${item['topic'] ?? item['topic_text'] ?? id}';
        final step = '${item['step'] ?? ''}';
        if (id.isEmpty) continue;
        out.add({'id': id, 'topic': topic, 'step': step});
      } else {
        final label = '$item';
        out.add({'id': label, 'topic': label, 'step': ''});
      }
    }
    return out;
  }

  String _actionsText(dynamic actions) {
    if (actions is! List || actions.isEmpty) return '';
    final parts = <String>[];
    for (final action in actions) {
      if (action is Map && action['text'] != null) {
        parts.add('${action['text']}');
      } else {
        parts.add('$action');
      }
    }
    return parts.join('\n');
  }

  Future<bool> _refreshRuns(String secret) async {
    final result = await widget.client.listRuns(secret);
    if (result['statusCode'] != 200) return false;
    final body = result['body'] as Map;
    setState(() {
      _inside = true;
      _openRunId = null;
      _openRunTopic = null;
      _runs = _parseRuns(body['runs']);
      _status = _runs.isEmpty ? 'Ходов пока нет. Напиши формулировку ниже.' : 'Список ходов. Нажми ход или начни новый.';
    });
    return true;
  }

  Future<void> _requestCode() async {
    final email = _email.text.trim();
    if (email.isEmpty) {
      setState(() => _status = 'Сначала введи email.');
      return;
    }
    setState(() {
      _busy = true;
      _status = 'Отправляю запрос на сервер…\n$channelBaseUrl';
    });
    try {
      final result = await widget.client.requestEmailCode(email);
      setState(() {
        _status = result['statusCode'] == 200
            ? 'Пришли код из письма на $email'
            : 'Код не отправлен. Ответ: ${result['statusCode']} ${result['body']}';
      });
    } catch (error) {
      setState(() => _status = 'Не достучались до сервера: $error');
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Future<void> _confirm() async {
    setState(() {
      _busy = true;
      _status = 'Проверяю код…';
    });
    try {
      final result = await widget.client.confirmEmailCode(
        _email.text.trim(),
        _code.text.trim(),
      );
      if (result['statusCode'] != 200) {
        final body = result['body'];
        final detail = body is Map && body['message'] != null ? body['message'] : body;
        setState(() => _status = 'Код не подошёл. Ответ: ${result['statusCode']} $detail');
        return;
      }
      final secret = (result['body'] as Map)['session_secret'] as String;
      await widget.sessions.put(secret);
      await _refreshRuns(secret);
    } catch (error) {
      setState(() => _status = 'Не достучались до сервера: $error');
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Future<void> _startRun() async {
    final topic = _topic.text.trim();
    if (topic.isEmpty) {
      setState(() => _status = 'Пусто. Сформулируй новость или проблему своими словами.');
      return;
    }
    final secret = await widget.sessions.get();
    if (secret == null) return;
    setState(() {
      _busy = true;
      _status = 'Начинаю ход…';
    });
    try {
      final result = await widget.client.startRun(secret, topic);
      if (result['statusCode'] != 200) {
        final body = result['body'];
        final detail = body is Map && body['message'] != null ? body['message'] : body;
        setState(() => _status = '$detail');
        return;
      }
      _topic.clear();
      final actions = _actionsText((result['body'] as Map)['actions']);
      final listed = await widget.client.listRuns(secret);
      final runs = listed['statusCode'] == 200
          ? _parseRuns((listed['body'] as Map)['runs'])
          : <Map<String, String>>[];
      setState(() {
        _inside = true;
        _runs = runs;
        if (runs.isNotEmpty) {
          _openRunId = runs.first['id'];
          _openRunTopic = runs.first['topic'] ?? topic;
        }
        _status = actions.isEmpty ? 'Ход начат.' : actions;
      });
    } catch (error) {
      setState(() => _status = 'Не достучались до сервера: $error');
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Future<void> _openRun(Map<String, String> run) async {
    final secret = await widget.sessions.get();
    if (secret == null) return;
    setState(() {
      _busy = true;
      _status = 'Открываю ход…';
      _answerIdempotencyKey = null;
    });
    try {
      final result = await widget.client.resumeRun(secret, run['id']!);
      if (result['statusCode'] != 200) {
        final body = result['body'];
        final detail = body is Map && body['message'] != null ? body['message'] : body;
        setState(() => _status = 'Не открыли ход: $detail');
        return;
      }
      final actions = _actionsText((result['body'] as Map)['actions']);
      setState(() {
        _openRunId = run['id'];
        _openRunTopic = run['topic'];
        _status = actions.isEmpty ? 'Ход открыт.' : actions;
      });
    } catch (error) {
      setState(() => _status = 'Не достучались до сервера: $error');
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Future<void> _sendAnswer() async {
    final text = _answer.text.trim();
    final runId = _openRunId;
    if (runId == null) return;
    if (text.isEmpty) {
      setState(() => _status = 'Напиши ответ на вопрос.');
      return;
    }
    final secret = await widget.sessions.get();
    if (secret == null) return;
    _answerIdempotencyKey ??=
        '$runId-${text.hashCode}-${DateTime.now().millisecondsSinceEpoch}';
    setState(() {
      _busy = true;
      _status = 'Отправляю ответ…';
    });
    try {
      final result = await widget.client.answerRun(
        secret,
        runId,
        text,
        idempotencyKey: _answerIdempotencyKey,
      );
      if (result['statusCode'] != 200) {
        final body = result['body'];
        final detail = body is Map && body['message'] != null ? body['message'] : body;
        setState(() => _status = 'Ответ не принят: $detail');
        return;
      }
      _answer.clear();
      _answerIdempotencyKey = null;
      final actions = _actionsText((result['body'] as Map)['actions']);
      setState(() => _status = actions.isEmpty ? 'Ответ принят.' : actions);
    } catch (error) {
      setState(() => _status = 'Не достучались до сервера: $error');
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Future<void> _backToList() async {
    final secret = await widget.sessions.get();
    if (secret == null) return;
    setState(() {
      _busy = true;
      _answerIdempotencyKey = null;
    });
    try {
      final result = await widget.client.leaveToList(secret);
      if (result['statusCode'] != 200) {
        setState(() => _status = 'Не вернулись к списку: ${result['body']}');
        return;
      }
      final body = result['body'] as Map;
      setState(() {
        _openRunId = null;
        _openRunTopic = null;
        _runs = _parseRuns(body['runs']);
        _status = _runs.isEmpty
            ? 'Ходов пока нет. Напиши формулировку ниже.'
            : 'Список ходов. Нажми ход или начни новый.';
      });
    } catch (error) {
      setState(() => _status = 'Не достучались до сервера: $error');
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Future<void> _logout() async {
    final secret = await widget.sessions.get();
    if (secret != null) {
      try {
        await widget.client.logout(secret);
      } catch (_) {}
    }
    await widget.sessions.clear();
    setState(() {
      _inside = false;
      _runs = const [];
      _openRunId = null;
      _openRunTopic = null;
      _status = 'Вышел. Нужен новый код.\nСервер: $channelBaseUrl';
    });
  }

  @override
  Widget build(BuildContext context) {
    final inRun = _openRunId != null;
    return Scaffold(
      appBar: AppBar(title: const Text('Business Mindset')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(_status),
            if (_busy)
              const Padding(
                padding: EdgeInsets.symmetric(vertical: 12),
                child: Center(child: CircularProgressIndicator()),
              ),
            if (!_inside) ...[
              TextField(
                controller: _email,
                enabled: !_busy,
                decoration: const InputDecoration(labelText: 'Email'),
                keyboardType: TextInputType.emailAddress,
              ),
              TextField(
                controller: _code,
                enabled: !_busy,
                decoration: const InputDecoration(labelText: 'Код'),
              ),
              ElevatedButton(
                onPressed: _busy ? null : _requestCode,
                child: const Text('Запросить код'),
              ),
              ElevatedButton(
                onPressed: _busy ? null : _confirm,
                child: const Text('Подтвердить'),
              ),
            ] else if (!inRun) ...[
              Expanded(
                child: ListView(
                  children: _runs
                      .map(
                        (run) => ListTile(
                          title: Text(run['topic'] ?? run['id'] ?? ''),
                          subtitle: (run['step'] ?? '').isEmpty ? null : Text('Шаг: ${run['step']}'),
                          onTap: _busy ? null : () => _openRun(run),
                        ),
                      )
                      .toList(),
                ),
              ),
              TextField(
                controller: _topic,
                enabled: !_busy,
                decoration: const InputDecoration(
                  labelText: 'Новая формулировка',
                ),
                minLines: 1,
                maxLines: 3,
              ),
              ElevatedButton(
                onPressed: _busy ? null : _startRun,
                child: const Text('Начать ход'),
              ),
              ElevatedButton(onPressed: _busy ? null : _logout, child: const Text('Выйти')),
            ] else ...[
              Text('Ход: ${_openRunTopic ?? _openRunId}', style: Theme.of(context).textTheme.titleMedium),
              const SizedBox(height: 8),
              TextField(
                controller: _answer,
                enabled: !_busy,
                decoration: const InputDecoration(labelText: 'Ответ'),
                minLines: 2,
                maxLines: 5,
              ),
              ElevatedButton(
                onPressed: _busy ? null : _sendAnswer,
                child: const Text('Отправить ответ'),
              ),
              ElevatedButton(
                onPressed: _busy ? null : _backToList,
                child: const Text('К списку'),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
