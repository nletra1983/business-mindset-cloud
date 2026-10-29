# Implementation Plan: Настройки того же входа в приложении

**Branch**: `011-app-settings` | **Date**: 2026-10-29 | **Spec**: [spec.md](./spec.md)

## Summary

Настройки открываются в те же три момента, что в боте. Внутри — выбор модели и видимая информация о себе. Скрытый профиль не показывается. Второй вход и разбор новости не входят.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: `app/model_switch.py`, `app/account_settings.py`

**Storage**: уже существующие модель и видимый профиль

**Testing**: `pytest`

**Target Platform**: тот же процесс

**Constraints**: новые правила модели не пишутся. Скрытые отметки не меняются.

## Constitution Check

- Один процесс. Pass.
- Канал не владеет ходом. Pass.
- Стек не перевыбирается. Pass.
- Граница истории соблюдена. Pass.
- Открытых `NEEDS CLARIFICATION` нет. Pass.

## Project Structure

```text
app/app_settings.py
tests/test_app_settings.py
```
