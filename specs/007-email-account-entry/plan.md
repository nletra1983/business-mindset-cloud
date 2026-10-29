# Implementation Plan: Вход по email без обязательного Telegram

**Branch**: `007-email-account-entry` | **Date**: 2026-10-29 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/007-email-account-entry/spec.md`

## Summary

Человек может появиться по email и коду из письма и пользоваться продуктом без Telegram. Человек в боте по-прежнему работает без email. Правила слияния живут здесь: второй вход подтверждается кодом, до обоих кодов ходы не смешиваются, после них ходы остаются у одного человека, разные отметки навыка становятся «неравномерно», тексты профиля не склеиваются. Экраны приложения и кнопки настроек — следующие истории.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: `httpx`, `psycopg` (v3, binary), существующий Telegram long-poll

**Storage**: Postgres текущего контура. Email — отдельная привязка. Существующая привязка Telegram не переписывается.

**Testing**: `pytest`. Письмо в тестах подменяется записью, наружу код не уходит.

**Target Platform**: тот же контейнер `bot` на Selectel

**Project Type**: один серверный процесс

**Performance Goals**: новый порог не задаётся

**Constraints**: стек не перевыбирается. Почтовый сервис не выбирается. Диалог в письмо не попадает. Экраны приложения этой историей не строятся. Текст профиля скилл не склеивает. Конституция не меняется. Номер телефона не реализуется.

**Scale/Scope**: текущий контур автора. Три сценария спеки: вход по email, бот без email, правило слияния.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Один процесс, без нового сервиса. Pass.
- Канал не владеет ходом. Email и Telegram — привязки, не ключ человека. Pass.
- Записи остаются в Postgres на Selectel. Письмо уносит только код. Pass.
- Стек не перевыбирается. Почтовый сервис не фиксируется. Pass.
- Граница истории: правила аккаунта. Экраны приложения, кнопки второго входа, разбор новости и склейка текста профиля не входят. Pass.
- Открытых `NEEDS CLARIFICATION` в spec нет. Pass.

### Post-design

Контракт описывает действия аккаунта без экранов. Отдельного клиента и отдельного хранилища нет.

## Project Structure

### Documentation (this feature)

```text
specs/007-email-account-entry/
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
├── entrances.py
└── mail.py

tests/
└── test_email_entrances.py
```

**Structure Decision**: тот же пакет `app/`. Привязка email и коды живут рядом с человеком. Бот этой историей не получает новых кнопок.
