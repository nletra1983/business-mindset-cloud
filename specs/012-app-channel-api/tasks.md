# Tasks: Защищённый вход модуля каналов для приложения

**Input**: Design documents from `/specs/012-app-channel-api/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/app-channel-v1.md

**Tests**: quickstart.

## Phase 1: Setup

- [x] T001 Добавить таблицы сессий и повторов операций в `app/schema.sql`
- [x] T002 Опубликовать локальный порт входа в `docker-compose.yml` на `127.0.0.1`

## Phase 2: Foundational

- [x] T003 Выдать и проверить секрет сессии в `app/sessions.py`
- [x] T004 Поднять HTTP-слушатель `/app/v1` в том же процессе в `app/channel_http.py` и `app/main.py`

## Phase 3: User Story 1 — вход по email через каналы (P1)

- [x] T005 [US1] Запрос кода, подтверждение и выдача секрета в `app/channel_api.py`
- [x] T006 [US1] Проверить успех и отказ в `tests/test_channel_api.py`

## Phase 4: User Story 2 — тот же хост, действия продукта (P1)

- [x] T007 [US2] Список ходов, разбор, настройки и слияние через секрет в `app/channel_api.py`
- [x] T008 [US2] Проверить путь `/app/v1` и отказ без секрета в `tests/test_channel_api.py`

## Phase 5: User Story 3 — повтор операции (P2)

- [x] T009 [US3] Сохранять ответ по `Idempotency-Key` в `app/channel_api.py` / `app/sessions.py`
- [x] T010 [US3] Проверить, что повтор не двигает шаг, в `tests/test_channel_api.py`

## Phase 6: Polish

- [x] T011 Прогнать `py -3.12 -m pytest tests/test_channel_api.py tests/test_email_entrances.py tests/test_app_email_entry.py`
- [x] T012 Отметить историю в `features/feature-map.md` как `in-impl`

## Dependencies

US1 → US2 → US3. Flutter и APK не входят.

## Implementation strategy

Сначала сессия и auth, затем продуктные вызовы, затем идемпотентность.
