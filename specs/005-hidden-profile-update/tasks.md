# Tasks: Update Hidden Skill Profile from Exercise Results

**Input**: Design documents from `/specs/005-hidden-profile-update/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: `plan.md` фиксирует `pytest` как основной способ проверки, поэтому тестовые задачи включены.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Runtime code: `app/`
- Tests: `tests/`
- Spec artifacts: `specs/005-hidden-profile-update/`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Подготовить доменные константы и тестовые каркасы для hidden-профиля.

- [X] T001 Добавить в `app/person.py` константы характеристик (`spotting`, `creativity`, `valuing`, `uncertainty`, `resources`, `learning`) и допустимых статусов (`не наблюдалось`, `проявляется`, `слабо`, `устойчиво`, `неравномерно`).
- [X] T002 [P] Создать `tests/test_hidden_profile_update.py` с каркасом сценариев US1-US3 (обновление по свидетельству, merge статусов, идемпотентность, приватность).

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Добавить персистентные hidden-сущности и общий apply-пайплайн обновления.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T003 Обновить `app/schema.sql`: добавить hidden-таблицы профиля и свидетельств с ограничениями из `data-model.md` — статусы только `не наблюдалось|проявляется|слабо|устойчиво|неравномерно`, `current_focus` только одна из шести характеристик, уникальность `(run_id, characteristic_id)` для идемпотентности.
- [X] T004 [P] Реализовать в `app/person.py` чтение/инициализацию hidden-профиля по `person_id` с дефолтами (`не наблюдалось` по всем характеристикам, один валидный `current_focus`).
- [X] T005 Реализовать в `app/person.py` apply-функцию для обновлений hidden-профиля по payload контракта (`run_id`, `exercise_id`, `observations[]`) с валидацией `characteristic_id` и `signal`, без изменений при невалидном payload.
- [X] T006 Подключить в `app/run_flow.py` вызов apply-функции при финализации хода, используя `run_id` и результат упражнения как источник структурированных наблюдений.

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Save evidence-based characteristic updates after an exercise (Priority: P1) 🎯 MVP

**Goal**: Обновлять hidden-профиль только по фактически наблюдённым характеристикам завершённого/поставленного на паузу упражнения.

**Independent Test**: После завершения хода с наблюдением по `spotting` меняется только `spotting`; ненаблюдавшиеся характеристики не меняются.

### Tests for User Story 1

- [X] T007 [P] [US1] Дописать `tests/test_hidden_profile_update.py`: первое наблюдение переводит `spotting` из `не наблюдалось` в сигнал и сохраняет свидетельство (`run_id`, `quote_or_paraphrase`, `exercise_id`).
- [X] T008 [P] [US1] Дописать `tests/test_hidden_profile_update.py`: отсутствие наблюдения по характеристике не помечает её как слабую и не меняет статус.
- [X] T009 [P] [US1] Дописать `tests/test_hidden_profile_update.py`: при завершении хода `run_flow` вызывает hidden-profile update один раз с текущим `run_id`.

### Implementation for User Story 1

- [X] T010 [US1] Реализовать в `app/run_flow.py` сбор наблюдений для hidden-профиля в рамках текущей границы smoke: допускается обновление только `spotting`.
- [X] T011 [US1] Реализовать в `app/person.py` запись `CharacteristicEvidence` и обновление статуса только по характеристикам из `observations[]`, не трогая остальные.
- [X] T012 [US1] Добавить в `app/person.py` проверку short-flow ограничения: для smoke-упражнения любые характеристики, кроме `spotting`, отклоняются без изменения persisted профиля.

**Checkpoint**: User Story 1 is fully functional and independently testable

---

## Phase 4: User Story 2 - Merge status across runs using profile rules (Priority: P2)

**Goal**: Применять детерминированные merge-правила между ходами: повтор одного сигнала ведёт к `устойчиво`, противоречие ведёт к `неравномерно`.

**Independent Test**: На последовательности двух и более ходов статусы переходят по правилам без потери свидетельств.

### Tests for User Story 2

- [X] T013 [P] [US2] Дописать `tests/test_hidden_profile_update.py`: второй завершённый ход с тем же сигналом переводит характеристику в `устойчиво`.
- [X] T014 [P] [US2] Дописать `tests/test_hidden_profile_update.py`: противоположный сигнал переводит характеристику в `неравномерно` и сохраняет оба свидетельства.
- [X] T015 [P] [US2] Дописать `tests/test_hidden_profile_update.py`: один ход никогда не ставит `устойчиво`.

### Implementation for User Story 2

- [X] T016 [US2] Реализовать в `app/person.py` merge-логику статусов по правилам: `не наблюдалось`→сигнал, повтор сигнала во втором завершённом ходе→`устойчиво`, конфликт сигналов→`неравномерно`.
- [X] T017 [US2] Добавить в `app/person.py` хранение истории свидетельств без стирания предыдущих записей при конфликте сигналов.

**Checkpoint**: User Stories 1 and 2 both work independently

---

## Phase 5: User Story 3 - Keep hidden profile private while selecting current training focus (Priority: P3)

**Goal**: Сохранять приватность hidden-профиля и выбирать ровно один `current_focus` после обновления.

**Independent Test**: Повторная доставка одного результата не создаёт дубликатов; `current_focus` выбирается из шести характеристик; visible-flow не раскрывает hidden-данные.

### Tests for User Story 3

- [X] T018 [P] [US3] Дописать `tests/test_hidden_profile_update.py`: повтор той же пары (`run_id`, `characteristic_id`) не создаёт дубликат свидетельства и не меняет статус повторно.
- [X] T019 [P] [US3] Дописать `tests/test_hidden_profile_update.py`: после обновления выбран ровно один `current_focus` по приоритету `слабо` → `неравномерно` → `не наблюдалось`.
- [X] T020 [P] [US3] Дописать `tests/test_account_settings_state.py`: правка `информация о себе` не меняет hidden-статусы и не показывает внутренние characteristic ids.

### Implementation for User Story 3

- [X] T021 [US3] Реализовать в `app/person.py` идемпотентную обработку `(run_id, characteristic_id)` и выбор одного `current_focus` только из шести характеристик.
- [X] T022 [US3] Проверить и при необходимости поправить `app/account_settings.py` / `app/telegram_poll.py`, чтобы user-visible профиль не раскрывал hidden-статусы и не триггерил hidden merge-процедуру.

**Checkpoint**: All user stories are independently functional and privacy-safe

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Финальная валидация и синхронизация артефактов.

- [X] T023 [P] Запустить `python3 -m pytest tests/test_hidden_profile_update.py tests/test_self_info_profile.py tests/test_account_settings_state.py` и сохранить вывод как артефакт.
- [X] T024 Запустить `python3 -m pytest tests` для регрессии и сохранить вывод как артефакт.
- [X] T025 Сверить `specs/005-hidden-profile-update/quickstart.md` с фактическими сценариями тестов и обновить quickstart при расхождении.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: starts immediately.
- **Phase 2 (Foundational)**: depends on Phase 1 and blocks all user stories.
- **Phase 3 (US1)**: starts after foundational storage/apply pipeline.
- **Phase 4 (US2)**: starts after US1 baseline update path.
- **Phase 5 (US3)**: starts after US1/US2 merge behavior exists.
- **Phase 6 (Polish)**: runs after implementation phases.

### User Story Dependencies

- **US1 (P1)**: independent after foundational phase.
- **US2 (P2)**: depends on US1 update pipeline and evidence persistence.
- **US3 (P3)**: depends on US1/US2 behavior to validate idempotency, focus, and privacy boundaries.

### Within Each User Story

- Tests first, then implementation.
- Schema and persistence primitives before run-flow integration.
- Merge and focus logic after baseline apply path.

### Parallel Opportunities

- T002 and T004 can run in parallel after T001/T003.
- T007, T008, T009 can run in parallel.
- T013, T014, T015 can run in parallel.
- T018, T019, T020 can run in parallel.

---

## Parallel Example: User Story 2

```bash
# Parallel test preparation for US2
Task: "T013 [US2] Same-signal transition test in tests/test_hidden_profile_update.py"
Task: "T014 [US2] Contradictory-signal transition test in tests/test_hidden_profile_update.py"
Task: "T015 [US2] Single-run cannot become stable test in tests/test_hidden_profile_update.py"

# Then implementation
Task: "T016 [US2] Implement status merge rules in app/person.py"
Task: "T017 [US2] Persist evidence history in app/person.py"
```

---

## Implementation Strategy

### MVP First (US1 only)

1. Complete Phases 1-2.
2. Deliver US1 evidence-based update for `spotting`.
3. Validate independently.

### Incremental Delivery

1. Add US1 (observed-only updates + smoke boundary).
2. Add US2 (cross-run merge rules).
3. Add US3 (idempotency + current focus + privacy guard).
4. Run targeted and full regression after each increment.

### Parallel Team Strategy

1. Один разработчик закрывает schema/person persistence.
2. Второй подготавливает hidden-profile тесты.
3. Третий интегрирует run-flow вызов и проверяет privacy boundary в settings-flow.

---

## Notes

- Граница истории: hidden profile update по результатам задания; visible profile edit остаётся отдельным потоком.
- Поле `сейчас тренировать` выбирается из существующих шести характеристик и не трактуется как отдельная седьмая характеристика.
