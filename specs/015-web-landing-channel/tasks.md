# Tasks: Веб-канал лендинга на Selectel

**Input**: Design documents from `/specs/015-web-landing-channel/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/web-landing-v1.md, quickstart.md

**Tests**: pytest per quickstart.

## Phase 1: Setup

- [x] T001 Добавить `secrets/smartcaptcha.env` в `env_file` сервиса `bot` в `docker-compose.yml`
- [x] T002 [P] Создать каркас `web/index.html` (минимальная оболочка лендинга)
- [x] T003 [P] Добавить в документацию/`.env.example` или README оператора имя `YANDEX_METRIKA_COUNTER_ID` без секрета (без значений ключей)

## Phase 2: Foundational

- [x] T004 Таблицы `guest_session` и `guest_window` в `app/schema.sql` по `data-model.md`
- [x] T005 Модуль гостевой сессии (выдача cookie id, счётчик окон дня, TTL) в `app/web_landing.py`
- [x] T006 Встроить раздачу статики и маршрутов `/web/v1/...` в существующий HTTP-слушатель (`app/channel_http.py` / `app/main.py`) без поломки `/app/v1`

## Phase 3: User Story 1 — хост лендинга (P1)

- [x] T007 [US1] Отдавать `web/index.html` на корне лендинга и ставить guest cookie при первом заходе в `app/web_landing.py` / `app/channel_http.py`
- [x] T008 [US1] Проверка в `tests/test_web_landing.py`: HTML 200 + Set-Cookie; регрессия `tests/test_channel_api.py`

## Phase 4: User Story 2 — гостевой билет (P1)

- [x] T009 [US2] Чтение/создание `guest_session` и ответ `GET /web/v1/guest/session` в `app/web_landing.py`
- [x] T010 [US2] Заложить поля окна и правило TTL 24 ч от `first_reply_at` (очистка UI не обязана удалять строку) в `app/web_landing.py`
- [x] T011 [US2] Тесты сессии и отсутствия person в `tests/test_web_landing.py`

## Phase 5: User Story 3 — крючки get-news / captcha / mail (P2)

- [x] T012 [US3] Хук обновления бэклога get-news (4 ч) в `app/get_news_backlog.py` (или рядом) + вызов из процесса `app/main.py`
- [x] T013 [US3] Убедиться, что `secrets/mail.env` остаётся единственным контуром почты витрины; не читать значения в тестах
- [x] T014 [US3] Тест/проверка возраста бэклога в `tests/test_web_landing.py` или узком unit-тесте

## Phase 6: Polish

- [x] T015 Прогнать `py -3.12 -m pytest tests/test_web_landing.py tests/test_channel_api.py`
- [x] T016 Краткая памятка DNS/nginx для оператора в `specs/015-web-landing-channel/quickstart.md` (без SSH агента)
- [x] T017 Отметить историю №0 в `features/feature-map.md` как `in-impl` при старте кода / `done` после приёмки — по факту implement
