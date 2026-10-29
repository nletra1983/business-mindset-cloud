# Tasks: Вход по email без обязательного Telegram

**Input**: Design documents from `/specs/007-email-account-entry/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/account-entrances.md, quickstart.md

**Tests**: Проверка из quickstart, потому что история меняет уже работающий вход.

**Organization**: Сначала общая схема, затем истории по приоритету.

## Format: `[ID] [P?] [Story] Description`

## Phase 1: Setup

- [x] T001 Добавить таблицы email, кода и сохранённого текста профиля в `app/schema.sql`

## Phase 2: Foundational

- [x] T002 Вынести правила кода, письма и слияния отметок в `app/entrances.py`
- [x] T003 Подключить отправку кода без текста упражнения в `app/mail.py`

## Phase 3: User Story 1 — вход по email (P1)

**Goal**: Адрес и верный код пускают без Telegram. Неверный код и уже занятый адрес не создают второго человека.

**Independent Test**: `begin_email_login` и `confirm_email_login` в `tests/test_email_entrances.py`.

- [x] T004 [US1] Принять адрес и последний код в `app/entrances.py`
- [x] T005 [US1] Проверить вход, отказ и текст письма в `tests/test_email_entrances.py`

## Phase 4: User Story 2 — бот без email (P1)

**Goal**: Человек в Telegram продолжает ход. Email не спрашивается.

**Independent Test**: обычный текст бота не становится запросом email, схема не содержит вход по номеру.

- [x] T006 [US2] Не добавлять запрос email в текущий диалог бота
- [x] T007 [US2] Проверить это в `tests/test_email_entrances.py` и `tests/test_phone_entrances.py`

## Phase 5: User Story 3 — правило слияния (P2)

**Goal**: Один код из двух не сливает ходы. После обоих кодов ходы у одного человека, разные отметки становятся «неравномерно», тексты профиля остаются двумя.

**Independent Test**: два человека, два кода, сравнение ходов, отметок и текстов.

- [x] T008 [US3] Слить ходы и отметки и сохранить оба текста в `app/entrances.py`
- [x] T009 [US3] Проверить отказ, ожидание второго кода и слияние в `tests/test_email_entrances.py`

## Phase 6: Polish

- [x] T010 Прогнать `py -3.12 -m pytest tests/test_email_entrances.py tests/test_phone_entrances.py tests/test_account_settings_entry.py`
- [x] T011 Отметить историю в `features/feature-map.md` как идущую в реализацию

## Dependencies

US1 и US2 опираются на фазу 2. US3 опирается на US1. Полировка — после них. Экраны приложения и кнопки настроек в эти задачи не входят.

## Parallel example

T005 и T007 можно писать рядом после T004 и T006.

## Implementation strategy

Сначала вход по email и неприкосновенность бота. Затем правило слияния. Приложение Android не входит в эти задачи.
