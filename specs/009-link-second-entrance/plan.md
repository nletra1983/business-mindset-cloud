# Implementation Plan: Второй вход из настроек

**Branch**: `009-link-second-entrance` | **Date**: 2026-10-29 | **Spec**: [spec.md](./spec.md)

## Summary

В настройках бота и в том же действии приложения человек указывает email, Telegram или оба. Код подтверждает добавляемый вход. Один код из двух не сливает ходы. После обоих кодов вызывается уже принятое правило слияния.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: `app/entrances.py`, текущие настройки Telegram

**Storage**: шаги диалога настроек в уже существующей сессии профиля

**Testing**: `pytest`

**Target Platform**: тот же процесс `bot`

**Project Type**: один серверный процесс

**Constraints**: правила аккаунта не переписываются. Выбор модели и информация о себе не меняются. Номер телефона не добавляется.

## Constitution Check

- Один процесс. Pass.
- Канал не владеет ходом. Pass.
- Стек не перевыбирается. Pass.
- Граница: только второй вход. Pass.
- Открытых `NEEDS CLARIFICATION` нет. Pass.

## Project Structure

```text
app/account_settings.py
app/telegram_poll.py
app/app_links.py
app/schema.sql
tests/test_link_second_entrance.py
```

**Structure Decision**: кнопки добавляются в уже открытые настройки. Приложение вызывает те же функции.
