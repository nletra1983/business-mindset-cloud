# Implementation Plan: Расшифровка голосовых сообщений

**Branch**: `006-voice-message-transcription` | **Date**: 2026-10-28 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/006-voice-message-transcription/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

История добавляет вход голосом в уже существующие текстовые потоки Telegram: голосовое с микрофона становится текстом и обрабатывается как обычное сообщение человека. При этом существующая логика шага хода, дубликатов update, профиля и кнопок не переписывается. Для моделей без подтверждённого голосового входа бот возвращает recoverable ответ и не двигает шаг.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: `httpx`, `psycopg` (v3, binary), существующий Telegram long-poll

**Storage**: Postgres без новых таблиц; текстовые записи остаются в `utterance`

**Testing**: `pytest` (новые unit/integration-like тесты маршрутизации voice-сообщений и регрессия текущих тестов)

**Target Platform**: Linux-контур Selectel, тот же процесс `bot`

**Project Type**: один серверный процесс (Telegram-бот + бизнес-логика)

**Performance Goals**: отдельный KPI не вводится; голосовая расшифровка не должна ломать текущий UX-цикл ответа

**Constraints**: стек/облако не меняются; voice не хранится после распознавания; голос не нажимает кнопки; неподдерживаемый voice не двигает шаг

**Scale/Scope**: текущий Telegram MVP; только микрофонные voice-сообщения как вход в уже существующие текстовые потоки

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Один процесс и тот же репозиторий: изменения ограничены `app/*` и `tests/*`, без нового сервиса. Pass.
- Telegram остаётся первым каналом; голос только новый способ ввода текста. Pass.
- Хранение остаётся в текущем контуре (текст), audio-артефакты не сохраняются. Pass.
- Серверный вызов модели сохраняется; клиент не вызывает провайдера напрямую. Pass.
- Стек не перевыбирается: Python + Postgres + Telegram через `TELEGRAM_API_BASE`. Pass.
- Граница истории соблюдена: voice→text в существующих потоках; без новых кнопок, новых каналов и платёжного контура. Pass.
- Открытых `NEEDS CLARIFICATION` в spec нет. Pass.

### Post-design

После Phase 1 артефакты остаются в той же границе: вход voice-message, трансформация в text, переиспользование существующего message-flow, без изменения модели данных продукта выше текстовой записи реплик.

## Project Structure

### Documentation (this feature)

```text
specs/006-voice-message-transcription/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── telegram-voice-message-flow.md
└── tasks.md             # /speckit-tasks, этим шагом не создаётся
```

### Source Code (repository root)
```text
app/
├── telegram_poll.py       # входящие update, маршрутизация текст/voice
├── model_client.py        # вызовы модели и voice->text
├── run_flow.py            # существующий text-flow для хода
├── person.py              # текущая модель человека
└── config.py              # urls/env для model call paths

tests/
├── test_voice_messages.py
├── test_model_down.py
├── test_model_choice.py
└── test_self_info_profile.py
```

**Structure Decision**: используем существующий single-process модуль `app/`; добавляем voice-entry в текущий polling-route и переиспользуем текущий text handling path без новых сервисов.

## Complexity Tracking

Нарушений конституции, требующих отдельного обоснования, нет.
