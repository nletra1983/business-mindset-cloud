# Tasks: Войти в приложение по email и увидеть свои ходы

**Input**: Design documents from `/specs/008-app-email-entry/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/app-entry-screen.md

**Tests**: Проверка из quickstart.

## Phase 1: User Story 1 — вход без Telegram (P1)

- [x] T001 [US1] Собрать шаги адреса и кода без упоминания Telegram в `app/app_entry.py`
- [x] T002 [US1] Проверить отказ и несозданного человека в `tests/test_app_email_entry.py`

## Phase 2: User Story 2 — список своих ходов (P1)

- [x] T003 [US2] Показать только ходы этого входа, включая пустой список, в `app/app_entry.py`
- [x] T004 [US2] Проверить чужие ходы и отсутствие лишних действий в `tests/test_app_email_entry.py`

## Phase 3: Polish

- [x] T005 Прогнать `py -3.12 -m pytest tests/test_app_email_entry.py tests/test_email_entrances.py`
- [x] T006 Отметить историю в `features/feature-map.md`

## Dependencies

US2 опирается на успешный код из US1. Правила аккаунта из `specs/007-email-account-entry/` не переписываются.

## Implementation strategy

Сначала ответ экрана и тесты. Сборка Android не входит: SDK на машине нет.
