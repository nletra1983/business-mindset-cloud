# Implementation Plan: Открыть настройки с клавиатуры разбора

**Branch**: `003-open-settings-from-keyboard` | **Date**: 2026-10-28 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/003-open-settings-from-keyboard/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

В контуре Telegram кнопка входа в настройки должна заменить прямой вход в выбор модели и работать в тех же контекстах: незавершённый ход, список ходов и после финала. Нажатие `настройки` открывает меню из двух пунктов (`выбор модели`, `информация о себе`) и не меняет состояние текущего хода само по себе. Существующее поведение выбора модели сохраняется, меняется только точка входа.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: `httpx`, `psycopg` (v3, binary), существующая обвязка Telegram Bot API через `TELEGRAM_API_BASE`

**Storage**: Postgres существующего контура; новых таблиц в этой истории не требуется

**Testing**: `pytest` (точечные проверки клавиатуры/маршрутизации), ручная Telegram-проверка по quickstart

**Target Platform**: Linux-контур Selectel, тот же контейнер `bot`

**Project Type**: один серверный процесс (Telegram-бот + бизнес-логика)

**Performance Goals**: отдельный новый KPI не задан; нажатие `настройки` должно обрабатываться в рамках текущего UX-отклика бота

**Constraints**: стек и топология не перевыбираются; новых провайдеров и новых каналов нет; вход в настройки не должен ломать шаг, транскрипт и статус хода

**Scale/Scope**: фича для текущего Telegram-контура (порядок сотен пользователей); охват только точки входа и меню настроек

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Один продукт/процесс: изменения остаются в существующем процессе `app/*`, отдельный сервис не добавляется. Pass.
- Первый канал Telegram: история расширяет Telegram-клавиатуру, не уводит состояние хода в канал. Pass.
- Вызов моделей с сервера: правила model-switch не меняются, клиент не ходит к провайдерам напрямую. Pass.
- Стек и облако не перевыбираются: Python + Postgres + Selectel + `TELEGRAM_API_BASE` остаются прежними. Pass.
- Граница истории: реализуется одна история «Открыть настройки с клавиатуры разбора» без расширения на полную редактуру профиля. Pass.
- Открытых `NEEDS CLARIFICATION` в текущей спецификации нет. Pass.

### Post-design

После Phase 1 решения остаются в той же границе: новые артефакты описывают меню и маршрутизацию, без смены стека, без новых сервисов и без выхода за историю.

## Project Structure

### Documentation (this feature)

```text
specs/003-open-settings-from-keyboard/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── telegram-account-settings-entry.md
└── tasks.md              # /speckit-tasks, этим шагом не создаётся
```

### Source Code (repository root)

```text
app/
├── telegram_poll.py      # обработка callback/клавиатуры
├── run_list.py           # список ходов и кнопки
├── model_switch.py       # действующий поток выбора модели (переиспользуется)
└── db.py / schema.sql    # существующие данные, без новых таблиц в этой истории

tests/
└── test_model_choice.py  # уже существующие близкие сценарии UI-поведения кнопок
```

**Structure Decision**: используем текущую single-process структуру `app/` и существующие тесты; новые артефакты планирования остаются в `specs/003-open-settings-from-keyboard/`.

## Complexity Tracking

Нарушений конституции, которые нужно отдельно оправдывать, нет.
