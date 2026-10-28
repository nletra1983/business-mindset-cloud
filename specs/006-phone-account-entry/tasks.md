# Tasks: Вход с телефона без обязательного Telegram

**Input**: Design documents from `/specs/006-phone-account-entry/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/account-entrances.md, quickstart.md

**Tests**: Проверка из quickstart, потому что история меняет уже работающий вход.

**Organization**: Сначала общая схема, затем истории по приоритету.

## Format: `[ID] [P?] [Story] Description`

## Phase 1: Setup

- [x] T001 Добавить таблицы привязки телефона, кода и сохранённого текста профиля в `app/schema.sql`

## Phase 2: Foundational

- [x] T002 Вынести правила кода, SMS и слияния отметок в `app/entrances.py`
- [x] T003 Подключить отправку кода без текста упражнения в `app/sms.py`

## Phase 3: User Story 1 — вход с телефона (P1)

**Goal**: Номер и верный код пускают без Telegram. Неверный код не создаёт второго человека.

**Independent Test**: `begin_phone_login` и `confirm_phone_login` в `tests/test_phone_entrances.py`.

- [x] T004 [US1] Принять номер и последний код в `app/entrances.py`
- [x] T005 [US1] Проверить вход, отказ и текст SMS в `tests/test_phone_entrances.py`

## Phase 4: User Story 2 — бот без телефона (P1)

**Goal**: Человек в Telegram продолжает ход. В настройках телефон пуст, пока его не добавят.

**Independent Test**: шаг `idle` не спрашивает телефон, меню показывает «не указан».

- [x] T006 [US2] Показать пустой телефон в меню настроек в `app/account_settings.py` и `app/telegram_poll.py`
- [x] T007 [US2] Проверить, что обычный текст не становится запросом телефона, в `tests/test_phone_entrances.py`

## Phase 5: User Story 3 — слияние из настроек (P2)

**Goal**: Второй вход подтверждается кодом. До обоих кодов ходы разделены. После них ходы у одного человека, разные отметки становятся «неравномерно», тексты профиля остаются двумя.

**Independent Test**: два человека, два кода, сравнение ходов, отметок и текстов.

- [x] T008 [US3] Провести телефон и Telegram через настройки бота в `app/telegram_poll.py`
- [x] T009 [US3] Слить ходы и отметки и сохранить оба текста в `app/entrances.py`
- [x] T010 [US3] Показать второй текст отдельно в `app/account_settings.py`
- [x] T011 [US3] Проверить отказ, ожидание второго кода и слияние в `tests/test_phone_entrances.py`

## Phase 6: Polish

- [x] T012 Прогнать `py -3.12 -m pytest tests/test_phone_entrances.py tests/test_account_settings_entry.py tests/test_self_info_profile.py`
- [x] T013 Отметить историю в `features/feature-map.md` как идущую в реализацию

## Dependencies

US1 и US2 опираются на фазу 2. US3 опирается на US1 и US2. Полировка — после них.

## Parallel example

T005 и T007 можно писать рядом после T004 и T006. T010 не блокирует T009.

## Implementation strategy

Сначала вход по телефону и неприкосновенность бота. Затем слияние из настроек. Приложение Android не входит в эти задачи.
