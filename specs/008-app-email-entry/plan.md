# Implementation Plan: Войти в приложение по email и увидеть свои ходы

**Branch**: `008-app-email-entry` | **Date**: 2026-10-29 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/008-app-email-entry/spec.md`

## Summary

Человек в приложении указывает email и код из письма и видит список ходов этого входа. Telegram не предлагается. Чужие ходы не показываются. Пустой список всё равно означает, что человек внутри. Открыть ход, начать разбор, настройки и второй вход эта история не даёт.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: уже существующие правила входа из `app/entrances.py` и `app/mail.py`

**Storage**: Postgres текущего контура, без новой схемы

**Testing**: `pytest`

**Target Platform**: тот же процесс `bot`. Экран Android рисует готовый ответ этого процесса. Сборка apk на этой машине не проверяется: Android SDK здесь нет.

**Project Type**: один серверный процесс и ответ, который показывает клиент

**Performance Goals**: новый порог не задаётся

**Constraints**: стек не перевыбирается. Приложение не вызывает модели. Правила аккаунта не переписываются. Кнопки следующих историй не добавляются.

**Scale/Scope**: вход и список. Один автор.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Один процесс. Клиент не становится вторым продуктом и не вызывает модель. Pass.
- Канал не владеет ходом. Список только читает ходы входа. Pass.
- Записи остаются в текущем контуре. Pass.
- Стек не перевыбирается. Pass.
- Граница истории соблюдена: нет разбора, настроек и второго входа. Pass.
- Открытых `NEEDS CLARIFICATION` нет. Pass.

### Post-design

Ответ экрана — данные для клиента. Отдельного сервиса нет.

## Project Structure

### Documentation (this feature)

```text
specs/008-app-email-entry/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── app-entry-screen.md
└── tasks.md
```

### Source Code (repository root)

```text
app/
└── app_entry.py

tests/
└── test_app_email_entry.py
```

**Structure Decision**: экранный ответ живёт рядом с правилами входа. Клиент Android позже только показывает этот ответ.
