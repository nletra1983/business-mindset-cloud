# Data Model: Расшифровка голосовых сообщений

История не добавляет новые продуктовые таблицы; расширяет входные события и результат распознавания, который переходит в существующую текстовую модель реплик.

## VoiceMessageInput (event model)

Входящий Telegram update для сообщения с полем `voice`.

## Fields

- `update_id` — идентификатор входящего update.
- `message_id` — идентификатор сообщения в чате.
- `chat_id` — чат сообщения.
- `person_id` — внутренний id человека после `upsert_from_telegram`.
- `voice.file_id` — идентификатор файла voice в Telegram.
- `voice.mime_type` — тип аудио (если передан Telegram).
- `voice.duration` — длительность voice-сообщения.

## Constraints

- Для этой истории используется только событие `voice`; `audio` и `video_note` не входят в обработку.
- Повторная доставка того же `update_id` не должна сдвигать шаг второй раз (существующий dedup).

## VoiceRecognitionOutcome (transient domain model)

Результат попытки получить текст из voice-сообщения.

## States

- `unsupported` — выбранная модель не поддерживает voice-path (`Эта модель не разбирает голос.`).
- `empty` — распознавание выполнено, но текст не получен (`Голос не разобран.`).
- `recognized` — непустой распознанный текст готов к передаче в text-flow.

## Fields

- `state`
- `recognized_text` (только для `recognized`)

## Constraints

- В состояниях `unsupported` и `empty` run/profile step не изменяется.
- `recognized_text` передаётся в существующую text-обработку без изменения бизнес-правил.

## RecognizedTextUtterance (persisted model reuse)

Используется существующая таблица `utterance`.

## Constraints

- Сохраняется только текст распознанной реплики.
- Исходный audio payload не хранится после распознавания.
- Логика профиля, хода и кнопок использует тот же flow, что для typed text.
