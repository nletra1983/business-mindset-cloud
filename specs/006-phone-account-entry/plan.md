# Implementation Plan: Вход с телефона без обязательного Telegram

**Branch**: `006-phone-account-entry` | **Date**: 2026-10-28 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/006-phone-account-entry/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

Человек может появиться по номеру телефона и коду из SMS и пользоваться продуктом без Telegram. Человек в боте по-прежнему работает без телефона. Второй вход добавляется только в настройках и подтверждается кодом в добавляемом канале. До подтверждения обоих ходы не смешиваются. После слияния ходы обоих остаются у одного человека, разные отметки навыка становятся «неравномерно», тексты профиля не склеиваются.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: `httpx`, `psycopg` (v3, binary), существующий Telegram long-poll

**Storage**: Postgres текущего контура. Телефон — отдельная привязка. Существующая привязка Telegram не переписывается.

**Testing**: `pytest`. Отправка SMS в тестах подменяется записью сообщения, наружу код не уходит.

**Target Platform**: тот же контейнер `bot` на Selectel

**Project Type**: один серверный процесс

**Performance Goals**: новый порог не задаётся. Подтверждение кода происходит в том же диалоге, без нового упражнения.

**Constraints**: стек не перевыбирается. Провайдер SMS не выбирается. Диалог в SMS не попадает. Приложение Android этой историей не строится. Текст профиля скилл не склеивает. Конституция не меняется.

**Scale/Scope**: текущий контур автора. Три сценария спеки: вход с телефона, бот без телефона, слияние из настроек.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Один процесс, без нового сервиса. Pass.
- Канал не владеет ходом. Телефон и Telegram — привязки, не ключ человека. Pass.
- Записи остаются в Postgres на Selectel. SMS уносит только код. Pass.
- Стек не перевыбирается. Провайдер SMS не фиксируется. Pass.
- Граница истории: аккаунт. Экраны приложения, разбор новости в приложении и склейка текста профиля не входят. Pass.
- Открытых `NEEDS CLARIFICATION` в spec нет. Pass.

### Post-design

Контракт описывает действия аккаунта и кнопки настроек бота. Отдельного клиента и отдельного хранилища нет.

## Project Structure

### Documentation (this feature)

```text
specs/006-phone-account-entry/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── account-entrances.md
└── tasks.md
```

### Source Code (repository root)

```text
app/
├── schema.sql
├── person.py
├── entrances.py
├── sms.py
├── account_settings.py
└── telegram_poll.py

tests/
└── test_phone_entrances.py
```

**Structure Decision**: тот же пакет `app/`. Привязка телефона и коды живут рядом с человеком. Бот только проводит уже существующего человека через настройки.
