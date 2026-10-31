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

/// Вход, список/ход, настройки (модель и видимый профиль).
class EntryShell extends StatefulWidget {
  const EntryShell({super.key, required this.client, required this.sessions});

  final ChannelClient client;
  final SessionStore sessions;

  @override
  State<EntryShell> createState() => _EntryShellState();
}

enum _Panel { auth, list, run, settings, models, profile, profileEdit, second }

enum _ProfileStep { strengths, weaknesses, fact }

class _EntryShellState extends State<EntryShell> {
  final _email = TextEditingController();
  final _code = TextEditingController();
  final _topic = TextEditingController();
  final _answer = TextEditingController();
  final _profileInput = TextEditingController();
  final _secondInput = TextEditingController();
  final _linkCode = TextEditingController();

  String _status = 'Укажи email.\nСервер: $channelBaseUrl';
  bool _busy = false;
  _Panel _panel = _Panel.auth;
  List<Map<String, String>> _runs = const [];
  String? _openRunId;
  String? _openRunTopic;
  String? _answerIdempotencyKey;
  List<String> _models = const [];
  String? _currentModel;
  _ProfileStep _profileStep = _ProfileStep.strengths;
  String _profilePrompt = '';
  bool _offerSecondEntrance = false;
  String _secondMode = ''; // email | telegram | code

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
    _profileInput.dispose();
    _secondInput.dispose();
    _linkCode.dispose();
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

  String _messageOf(Map body) {
    if (body['message'] != null) return '${body['message']}';
    if (body['text'] != null) return '${body['text']}';
    return '$body';
  }

  Future<bool> _refreshRuns(String secret) async {
    final result = await widget.client.listRuns(secret);
    if (result['statusCode'] != 200) return false;
    final body = result['body'] as Map;
    setState(() {
      _panel = _Panel.list;
      _openRunId = null;
      _openRunTopic = null;
      _runs = _parseRuns(body['runs']);
      _status = _runs.isEmpty
          ? 'Ходов пока нет. Напиши формулировку ниже.'
          : 'Список ходов. Нажми ход или начни новый.';
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
        final detail = body is Map ? _messageOf(body as Map) : body;
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
        setState(() => _status = body is Map ? _messageOf(body as Map) : '$body');
        return;
      }
      _topic.clear();
      final actions = _actionsText((result['body'] as Map)['actions']);
      final listed = await widget.client.listRuns(secret);
      final runs = listed['statusCode'] == 200
          ? _parseRuns((listed['body'] as Map)['runs'])
          : <Map<String, String>>[];
      setState(() {
        _runs = runs;
        if (runs.isNotEmpty) {
          _openRunId = runs.first['id'];
          _openRunTopic = runs.first['topic'] ?? topic;
          _panel = _Panel.run;
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
        setState(() => _status = 'Не открыли ход: ${body is Map ? _messageOf(body as Map) : body}');
        return;
      }
      final actions = _actionsText((result['body'] as Map)['actions']);
      setState(() {
        _openRunId = run['id'];
        _openRunTopic = run['topic'];
        _panel = _Panel.run;
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
        setState(() => _status = 'Ответ не принят: ${body is Map ? _messageOf(body as Map) : body}');
        return;
      }
      _answer.clear();
      _answerIdempotencyKey = null;
      final actions = _actionsText((result['body'] as Map)['actions']);
      setState(() {
        _status = actions.isEmpty ? 'Ответ принят.' : actions;
        // After finale the person stays on the run surface with settings available.
        _panel = _Panel.run;
      });
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
        _panel = _Panel.list;
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

  Future<void> _openSettings() async {
    final secret = await widget.sessions.get();
    if (secret == null) return;
    setState(() {
      _busy = true;
      _status = 'Открываю настройки…';
    });
    try {
      final result = await widget.client.openSettings(secret);
      if (result['statusCode'] != 200) {
        setState(() => _status = 'Настройки недоступны: ${result['body']}');
        return;
      }
      final body = result['body'] as Map;
      setState(() {
        _panel = _Panel.settings;
        _offerSecondEntrance = body['offers_second_entrance'] == true;
        _status = 'Настройки. Модель и информация о себе.';
      });
    } catch (error) {
      setState(() => _status = 'Не достучались до сервера: $error');
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Future<void> _closeSettings() async {
    if (_openRunId != null) {
      setState(() {
        _panel = _Panel.run;
        _status = 'Ход: ${_openRunTopic ?? _openRunId}. Продолжай ответ или вернись к списку.';
      });
      return;
    }
    final secret = await widget.sessions.get();
    if (secret == null) return;
    await _refreshRuns(secret);
  }

  Future<void> _openModels() async {
    final secret = await widget.sessions.get();
    if (secret == null) return;
    setState(() {
      _busy = true;
      _status = 'Загружаю модели…';
    });
    try {
      final result = await widget.client.getModels(secret);
      if (result['statusCode'] != 200) {
        setState(() => _status = 'Модели недоступны: ${result['body']}');
        return;
      }
      final body = result['body'] as Map;
      final models = (body['models'] as List?)?.map((e) => '$e').toList() ?? const <String>[];
      setState(() {
        _panel = _Panel.models;
        _models = models;
        _currentModel = body['current']?.toString();
        _status = body['text']?.toString() ?? 'Выбери модель.';
      });
    } catch (error) {
      setState(() => _status = 'Не достучались до сервера: $error');
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Future<void> _pickModel(String modelId) async {
    final secret = await widget.sessions.get();
    if (secret == null) return;
    setState(() {
      _busy = true;
      _status = 'Меняю модель…';
    });
    try {
      final result = await widget.client.chooseModel(secret, modelId);
      if (result['statusCode'] != 200) {
        setState(() => _status = 'Не сменили модель: ${result['body']}');
        return;
      }
      final body = result['body'] as Map;
      setState(() {
        _currentModel = body['current']?.toString() ?? modelId;
        _status = body['text']?.toString() ?? 'Модель изменена.';
        _panel = _Panel.settings;
      });
    } catch (error) {
      setState(() => _status = 'Не достучались до сервера: $error');
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Future<void> _openProfile() async {
    final secret = await widget.sessions.get();
    if (secret == null) return;
    setState(() {
      _busy = true;
      _status = 'Загружаю профиль…';
    });
    try {
      final result = await widget.client.getProfile(secret);
      if (result['statusCode'] != 200) {
        setState(() => _status = 'Профиль недоступен: ${result['body']}');
        return;
      }
      final body = result['body'] as Map;
      setState(() {
        _panel = _Panel.profile;
        _status = body['text']?.toString() ?? 'Профиль.';
        _profilePrompt = body['next']?.toString() ?? '';
        _profileStep = _ProfileStep.strengths;
      });
    } catch (error) {
      setState(() => _status = 'Не достучались до сервера: $error');
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Future<void> _beginProfileEdit() async {
    setState(() {
      _panel = _Panel.profileEdit;
      _profileInput.clear();
      _status = _profilePrompt.isEmpty ? 'Сильные стороны:' : _profilePrompt;
    });
  }

  Future<void> _saveProfilePart() async {
    final text = _profileInput.text.trim();
    final secret = await widget.sessions.get();
    if (secret == null) return;
    setState(() {
      _busy = true;
      _status = 'Сохраняю…';
    });
    try {
      late final Map<String, dynamic> result;
      if (_profileStep == _ProfileStep.strengths) {
        result = await widget.client.saveProfileStrengths(secret, text);
      } else if (_profileStep == _ProfileStep.weaknesses) {
        result = await widget.client.saveProfileWeaknesses(secret, text);
      } else {
        result = await widget.client.saveProfileFact(secret, text);
      }
      if (result['statusCode'] != 200) {
        setState(() => _status = 'Не сохранили: ${result['body']}');
        return;
      }
      final body = result['body'] as Map;
      _profileInput.clear();
      if (_profileStep == _ProfileStep.strengths) {
        setState(() {
          _profileStep = _ProfileStep.weaknesses;
          _profilePrompt = body['prompt']?.toString() ?? body['then']?.toString() ?? 'Слабые стороны:';
          _status = '${body['text']}\n\n$_profilePrompt';
          _panel = _Panel.profileEdit;
        });
      } else if (_profileStep == _ProfileStep.weaknesses) {
        setState(() {
          _profileStep = _ProfileStep.fact;
          _profilePrompt = body['prompt']?.toString() ?? body['fact']?.toString() ?? 'Факт (необязательно):';
          _status = '${body['text']}\n\n$_profilePrompt';
          _panel = _Panel.profileEdit;
        });
      } else {
        setState(() {
          _panel = _Panel.profile;
          _status = body['text']?.toString() ?? 'Профиль обновлён.';
          _profileStep = _ProfileStep.strengths;
        });
      }
    } catch (error) {
      setState(() => _status = 'Не достучались до сервера: $error');
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Future<void> _openSecondEntrance() async {
    final secret = await widget.sessions.get();
    if (secret == null) return;
    setState(() {
      _busy = true;
      _status = 'Открываю второй вход…';
    });
    try {
      final result = await widget.client.openSecondEntrance(secret);
      if (result['statusCode'] != 200) {
        setState(() => _status = 'Второй вход недоступен: ${result['body']}');
        return;
      }
      final body = result['body'] as Map;
      setState(() {
        _panel = _Panel.second;
        _secondMode = '';
        _secondInput.clear();
        _linkCode.clear();
        _status = body['text']?.toString() ?? 'Второй вход.';
      });
    } catch (error) {
      setState(() => _status = 'Не достучались до сервера: $error');
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Future<void> _submitSecondEmail() async {
    final secret = await widget.sessions.get();
    if (secret == null) return;
    setState(() => _busy = true);
    try {
      final result = await widget.client.submitSecondEmail(secret, _secondInput.text.trim());
      final body = result['body'] as Map? ?? {};
      setState(() {
        _status = body['text']?.toString() ?? '$body';
        if (result['statusCode'] == 200) {
          _secondMode = 'code';
          _linkCode.clear();
        }
      });
    } catch (error) {
      setState(() => _status = 'Не достучались до сервера: $error');
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Future<void> _submitSecondTelegram() async {
    final secret = await widget.sessions.get();
    if (secret == null) return;
    setState(() => _busy = true);
    try {
      final result = await widget.client.submitSecondTelegram(secret, _secondInput.text.trim());
      final body = result['body'] as Map? ?? {};
      setState(() {
        _status = body['text']?.toString() ?? '$body';
        if (result['statusCode'] == 200) {
          _secondMode = 'code';
          _linkCode.clear();
        }
      });
    } catch (error) {
      setState(() => _status = 'Не достучались до сервера: $error');
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Future<void> _submitLinkCode() async {
    final secret = await widget.sessions.get();
    if (secret == null) return;
    setState(() => _busy = true);
    try {
      final result = await widget.client.submitSecondCode(secret, _linkCode.text.trim());
      final body = result['body'] as Map? ?? {};
      setState(() {
        _status = body['text']?.toString() ?? '$body';
        if (body['waiting'] != true && result['statusCode'] == 200) {
          _panel = _Panel.settings;
          _secondMode = '';
        }
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
      _panel = _Panel.auth;
      _runs = const [];
      _openRunId = null;
      _openRunTopic = null;
      _status = 'Вышел. Нужен новый код.\nСервер: $channelBaseUrl';
    });
  }

  List<Widget> _settingsButton() => [
        ElevatedButton(
          onPressed: _busy ? null : _openSettings,
          child: const Text('Настройки'),
        ),
      ];

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
            if (_busy)
              const Padding(
                padding: EdgeInsets.symmetric(vertical: 12),
                child: Center(child: CircularProgressIndicator()),
              ),
            ..._body(),
          ],
        ),
      ),
    );
  }

  List<Widget> _body() {
    switch (_panel) {
      case _Panel.auth:
        return [
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
          ElevatedButton(onPressed: _busy ? null : _requestCode, child: const Text('Запросить код')),
          ElevatedButton(onPressed: _busy ? null : _confirm, child: const Text('Подтвердить')),
        ];
      case _Panel.list:
        return [
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
            decoration: const InputDecoration(labelText: 'Новая формулировка'),
            minLines: 1,
            maxLines: 3,
          ),
          ElevatedButton(onPressed: _busy ? null : _startRun, child: const Text('Начать ход')),
          ..._settingsButton(),
          ElevatedButton(onPressed: _busy ? null : _logout, child: const Text('Выйти')),
        ];
      case _Panel.run:
        return [
          Text('Ход: ${_openRunTopic ?? _openRunId}', style: Theme.of(context).textTheme.titleMedium),
          const SizedBox(height: 8),
          TextField(
            controller: _answer,
            enabled: !_busy,
            decoration: const InputDecoration(labelText: 'Ответ'),
            minLines: 2,
            maxLines: 5,
          ),
          ElevatedButton(onPressed: _busy ? null : _sendAnswer, child: const Text('Отправить ответ')),
          ElevatedButton(onPressed: _busy ? null : _backToList, child: const Text('К списку')),
          ..._settingsButton(),
        ];
      case _Panel.settings:
        return [
          ElevatedButton(onPressed: _busy ? null : _openModels, child: const Text('Модель')),
          ElevatedButton(onPressed: _busy ? null : _openProfile, child: const Text('О себе')),
          if (_offerSecondEntrance)
            ElevatedButton(
              onPressed: _busy ? null : _openSecondEntrance,
              child: const Text('Второй вход'),
            ),
          ElevatedButton(onPressed: _busy ? null : _closeSettings, child: const Text('Назад')),
        ];
      case _Panel.models:
        return [
          Expanded(
            child: ListView(
              children: _models
                  .map(
                    (id) => ListTile(
                      title: Text(id),
                      selected: id == _currentModel,
                      onTap: _busy ? null : () => _pickModel(id),
                    ),
                  )
                  .toList(),
            ),
          ),
          ElevatedButton(
            onPressed: _busy
                ? null
                : () => setState(() {
                      _panel = _Panel.settings;
                      _status = 'Настройки.';
                    }),
            child: const Text('Назад'),
          ),
        ];
      case _Panel.profile:
        return [
          ElevatedButton(onPressed: _busy ? null : _beginProfileEdit, child: const Text('Изменить')),
          ElevatedButton(
            onPressed: _busy
                ? null
                : () => setState(() {
                      _panel = _Panel.settings;
                      _status = 'Настройки.';
                    }),
            child: const Text('Назад'),
          ),
        ];
      case _Panel.profileEdit:
        return [
          TextField(
            controller: _profileInput,
            enabled: !_busy,
            decoration: InputDecoration(labelText: _profilePrompt.isEmpty ? 'Текст' : _profilePrompt),
            minLines: 2,
            maxLines: 4,
          ),
          ElevatedButton(onPressed: _busy ? null : _saveProfilePart, child: const Text('Сохранить')),
          ElevatedButton(
            onPressed: _busy
                ? null
                : () => setState(() {
                      _panel = _Panel.profile;
                    }),
            child: const Text('Назад'),
          ),
        ];
      case _Panel.second:
        return _secondBody();
    }
  }

  List<Widget> _secondBody() {
    if (_secondMode == 'code') {
      return [
        TextField(
          controller: _linkCode,
          enabled: !_busy,
          decoration: const InputDecoration(labelText: 'Код из письма или бота'),
        ),
        ElevatedButton(onPressed: _busy ? null : _submitLinkCode, child: const Text('Подтвердить код')),
        ElevatedButton(
          onPressed: _busy
              ? null
              : () => setState(() {
                    _panel = _Panel.settings;
                    _status = 'Настройки.';
                  }),
          child: const Text('Назад'),
        ),
      ];
    }
    if (_secondMode == 'email') {
      return [
        TextField(
          controller: _secondInput,
          enabled: !_busy,
          decoration: const InputDecoration(labelText: 'Email'),
          keyboardType: TextInputType.emailAddress,
        ),
        ElevatedButton(onPressed: _busy ? null : _submitSecondEmail, child: const Text('Отправить код')),
        ElevatedButton(
          onPressed: _busy ? null : () => setState(() => _secondMode = ''),
          child: const Text('Назад'),
        ),
      ];
    }
    if (_secondMode == 'telegram') {
      return [
        TextField(
          controller: _secondInput,
          enabled: !_busy,
          decoration: const InputDecoration(labelText: 'Telegram id'),
        ),
        ElevatedButton(onPressed: _busy ? null : _submitSecondTelegram, child: const Text('Отправить код')),
        ElevatedButton(
          onPressed: _busy ? null : () => setState(() => _secondMode = ''),
          child: const Text('Назад'),
        ),
      ];
    }
    return [
      ElevatedButton(
        onPressed: _busy
            ? null
            : () => setState(() {
                  _secondMode = 'email';
                  _secondInput.clear();
                  _status = 'Пришли email.';
                }),
        child: const Text('Добавить email'),
      ),
      ElevatedButton(
        onPressed: _busy
            ? null
            : () => setState(() {
                  _secondMode = 'telegram';
                  _secondInput.clear();
                  _status = 'Пришли Telegram id.';
                }),
        child: const Text('Добавить Telegram'),
      ),
      ElevatedButton(
        onPressed: _busy
            ? null
            : () => setState(() {
                  _panel = _Panel.settings;
                  _status = 'Настройки.';
                }),
        child: const Text('Назад'),
      ),
    ];
  }
}
