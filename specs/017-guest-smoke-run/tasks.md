# Tasks: Гостевой тренажёр smoke

**Input**: `/specs/017-guest-smoke-run/`

## Phase 1: Setup

- [x] T001 UI демо-зоны в `web/` (форма→лента, ожидание, очистить)

## Phase 2: Foundational

- [x] T002 Вызов get-news / приём своего факта в `app/web_guest_smoke.py`
- [x] T003 Проверка SmartCaptcha перед моделью

## Phase 3: US1 Three steps (P1)

- [x] T004 [US1] Цикл smoke ≤3 шагов, лента ответов
- [x] T005 [US1] После 3-го — показ гейта (без отправки email)
- [x] T006 [US1] Тесты шагов в `tests/test_guest_smoke.py`

## Phase 4: US2 Limits (P1)

- [x] T007 [US2] Лимит 3 окна/день; clear UI
- [x] T008 [US2] Тесты лимита и отказа без captcha

## Phase 5: Polish

- [x] T009 Статус №2 в feature-map при implement
