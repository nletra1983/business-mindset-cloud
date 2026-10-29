# Tasks: Сессия на устройстве и явный выход

**Input**: Design documents from `/specs/013-app-session/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: quickstart.

## Phase 1: Setup

- [x] T001 Добавить протокол vault устройства в `app/device_session.py`

## Phase 2: Foundational

- [x] T002 Подключить `POST /app/v1/auth/logout` в `app/channel_api.py` через `sessions.revoke`

## Phase 3: User Story 1 — остаться вошедшим (P1)

- [x] T003 [US1] После confirm класть секрет в vault и открывать список без нового кода в `tests/test_app_session.py`

## Phase 4: User Story 2 — явный выход (P1)

- [x] T004 [US2] Logout отзывает сервер и чистит vault в `tests/test_app_session.py`
- [x] T005 [US2] Старый секрет после logout не открывает `/runs`

## Phase 5: Polish

- [x] T006 Прогнать `py -3.12 -m pytest tests/test_app_session.py tests/test_channel_api.py`
- [x] T007 Отметить историю в `features/feature-map.md` как `in-impl`

## Dependencies

US1 и US2 опираются на T001–T002. Flutter-проект не создаём.

## Implementation strategy

Сначала logout на сервере и vault-протокол, затем сценарии stay-signed-in и logout в тестах.
