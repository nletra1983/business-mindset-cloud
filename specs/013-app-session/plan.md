# Implementation Plan: Сессия на устройстве и явный выход

**Branch**: `013-app-session` | **Date**: 2026-10-29 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/013-app-session/spec.md`

## Summary

После верного кода секрет остаётся у человека без таймерного выхода. Явный выход отзывает сессию на сервере и стирает секрет на устройстве. HTTPS-вход уже есть в `012`. Проект Flutter и APK — `014` / история №4; здесь — отзыв на сервере, контракт хранилища устройства и проверяемое поведение «остаться вошедшим / выйти».

## Technical Context

**Language/Version**: Python 3.12 (сервер); контракт устройства для будущего Flutter-клиента

**Primary Dependencies**: уже есть `app/sessions.py` с `revoke`; расширяем `channel_api`

**Storage**: `app_session.revoked_at`; на устройстве — secure store (реализация UI в №4)

**Testing**: `pytest` на logout, отказ старого секрета, устройство-хранилище как in-memory vault в тестах протокола

**Target Platform**: тот же контейнер `bot` + поведение клиента на Android автора

**Project Type**: серверный шов + протокол устройства

**Performance Goals**: не задаются

**Constraints**: без idle-timeout; без второго хоста; без создания Flutter-проекта в этой истории

**Scale/Scope**: авторский контур

## Constitution Check

- Один процесс. Pass.
- Канал не владеет ходом. Pass.
- Стек не перевыбирается. Pass.
- Flutter-проект не заводится здесь (история №4). Pass.
- Нет `NEEDS CLARIFICATION`. Pass.

### Post-design

`POST /app/v1/auth/logout` отзывает сессию. Клиентский vault — модуль протокола + тесты; wiring во Flutter в №4–№5.

## Project Structure

### Documentation (this feature)

```text
specs/013-app-session/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── session-logout.md
└── tasks.md
```

### Source Code

```text
app/
├── channel_api.py
├── sessions.py
└── device_session.py

tests/
└── test_app_session.py
```

**Structure Decision**: отзыв в существующем session store; `device_session` — протокол «положить / прочитать / стереть» для тестов и будущего клиента.
