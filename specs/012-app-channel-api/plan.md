# Implementation Plan: Защищённый вход модуля каналов для приложения

**Branch**: `012-app-channel-api` | **Date**: 2026-10-29 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/012-app-channel-api/spec.md`

## Summary

В том же процессе, что бот, открывается HTTPS-вход приложения: тот же хост сервиса, отдельный путь `/app/v1`. По входу запрашивают код на email, подтверждают его, получают секрет сессии и с ним вызывают уже принятые действия списка, разбора, настроек и слияния. Второй процесс и второй хост не поднимаются. Экраны Flutter и хранение секрета на телефоне не входят.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: `httpx`, `psycopg`, стандартный `http.server` в том же процессе (новый фреймворк не вводим)

**Storage**: Postgres текущего контура. Таблица сессий приложения и ключей повтора операции.

**Testing**: `pytest` на обработчиках входа без живого HTTPS-терминатора

**Target Platform**: контейнер `bot` на Selectel; снаружи тот же хост, TLS на краю хоста, путь `/app/`

**Project Type**: один серверный процесс

**Performance Goals**: новый порог не задаётся

**Constraints**: стек не перевыбирается. Правила аккаунта и хода не дублируются. Flutter и APK не входят. Имя пути — `/app/v1` (реализация ADL-021).

**Scale/Scope**: авторский контур. Три сценария спеки.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Один процесс, без нового сервиса. Pass.
- Канал не владеет ходом; вход только вызывает уже принятые правила. Pass.
- Записи в Postgres Selectel. Pass.
- Стек не перевыбирается; stdlib HTTP вместо нового фреймворка. Pass.
- Граница: шов сервера. Экраны, APK, хранение секрета на устройстве — нет. Pass.
- Открытых `NEEDS CLARIFICATION` нет. Pass.

### Post-design

Контракт JSON под `/app/v1`. TLS снаружи процесса. Отдельного контейнера нет.

## Project Structure

### Documentation (this feature)

```text
specs/012-app-channel-api/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── app-channel-v1.md
└── tasks.md
```

### Source Code (repository root)

```text
app/
├── schema.sql
├── channel_api.py
├── channel_http.py
├── sessions.py
└── main.py

tests/
└── test_channel_api.py
```

**Structure Decision**: HTTP-слушатель в том же процессе, что long poll. Обработчики вызывают `entrances`, `app_entry`, `app_news`, `app_settings`, `app_links`.
