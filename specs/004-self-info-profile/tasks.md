# Tasks: Read and Update Self Information

**Input**: Design documents from `/specs/004-self-info-profile/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: `plan.md` фиксирует `pytest` как базовый способ проверки, поэтому тестовые задачи включены.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Runtime code: `app/`
- Tests: `tests/`
- Spec artifacts: `specs/004-self-info-profile/`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Подготовить контрактные константы и структуру тестов для профиля.

- [X] T001 Обновить `app/account_settings.py`: добавить тексты/константы для шагов `информация о себе` (промпты, retry, финальные сообщения).
- [X] T002 [P] Создать `tests/test_self_info_profile.py` с каркасом тестов step-by-step поведения profile edit flow.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Добавить устойчивое хранение видимого профиля и состояния шага редактирования.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T003 Добавить в `app/schema.sql` таблицу `visible_profile` (обязательные поля `person_id`, `strengths_text`, `weaknesses_text`, `self_facts`, `updated_at`) и таблицу `profile_edit_session` (`person_id`, `step`, `updated_at`) с ограничением step на `idle`, `awaiting_strengths`, `awaiting_weaknesses`, `awaiting_extra_fact`.
- [X] T004 [P] Добавить в `app/person.py` функции чтения/записи `visible_profile` и чтения/записи `profile_edit_session`.
- [X] T005 Подключить в `app/telegram_poll.py` общий message-route для активной profile edit session до вызова `handle_text(...)`, чтобы профильный поток не смешивался с run-flow.

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Read current self information from settings (Priority: P1) 🎯 MVP

**Goal**: Пользователь открывает `информация о себе` и видит user-visible профиль.

**Independent Test**: Нажатие `settings:profile` возвращает текст профиля и переводит сессию в ожидание сильных сторон.

### Tests for User Story 1

- [X] T006 [P] [US1] Дописать `tests/test_account_settings_entry.py`: callback `settings:profile` показывает user-visible профиль и запускает шаг `awaiting_strengths`.
- [X] T007 [P] [US1] Дописать `tests/test_self_info_profile.py`: формат профиля содержит только visible разделы и не раскрывает hidden evaluator поля.

### Implementation for User Story 1

- [X] T008 [US1] Обновить `_settings_actions(...)` в `app/telegram_poll.py`: по `settings:profile` читать visible профиль, ставить шаг `awaiting_strengths`, отправлять профиль + prompt.
- [X] T009 [US1] В `app/account_settings.py` реализовать `render_visible_profile(...)` и стартовые profile actions для user-visible ответа.

**Checkpoint**: User Story 1 is fully functional and independently testable

---

## Phase 4: User Story 2 - Update strengths, weaknesses, and add facts (Priority: P2)

**Goal**: Пользователь по шагам обновляет сильные/слабые стороны и добавляет факт о себе.

**Independent Test**: В сессии редактирования валидные ответы последовательно сохраняются и видны при повторном чтении профиля.

### Tests for User Story 2

- [X] T010 [P] [US2] Дописать `tests/test_self_info_profile.py`: `awaiting_strengths` сохраняет `strengths_text` и переводит в `awaiting_weaknesses`.
- [X] T011 [P] [US2] Дописать `tests/test_self_info_profile.py`: `awaiting_weaknesses` сохраняет `weaknesses_text` и переводит в `awaiting_extra_fact`.
- [X] T012 [P] [US2] Дописать `tests/test_self_info_profile.py`: `awaiting_extra_fact` добавляет факт (или skip по `нет`) и завершает сессию в `idle`.

### Implementation for User Story 2

- [X] T013 [US2] Реализовать `_profile_message_actions(...)` в `app/telegram_poll.py` для шагов `awaiting_strengths`, `awaiting_weaknesses`, `awaiting_extra_fact`.
- [X] T014 [US2] В `app/person.py` реализовать append/read/write операции для фактов и текстовых полей visible профиля с сохранением в Postgres.
- [X] T015 [US2] В `app/account_settings.py` добавить финальные profile actions после сохранения (`profile_saved_actions(...)`).

**Checkpoint**: User Stories 1 and 2 both work independently

---

## Phase 5: User Story 3 - Keep hidden profile private and handle stale/invalid safely (Priority: P3)

**Goal**: Hidden evaluator профиль не раскрывается и не перезаписывается прямыми правками; stale/invalid входы обрабатываются recoverable.

**Independent Test**: Пустой ввод не затирает данные; stale/unknown step даёт recoverable ответ и не портит persisted профиль.

### Tests for User Story 3

- [X] T016 [P] [US3] Дописать `tests/test_self_info_profile.py`: пустой ввод на каждом profile step возвращает recoverable prompt без сохранения.
- [X] T017 [P] [US3] Дописать `tests/test_self_info_profile.py`: unknown profile step сбрасывается в `idle` и возвращает recoverable ответ.
- [X] T018 [P] [US3] Дописать `tests/test_account_settings_state.py`: profile-flow не вызывает model/state write функции run-flow.

### Implementation for User Story 3

- [X] T019 [US3] В `_profile_message_actions(...)` добавить recoverable-ветки для пустого ввода и неизвестного шага, без стирания валидных данных.
- [X] T020 [US3] Убедиться в `app/telegram_poll.py`, что profile-flow не вызывает `write_model_state(...)` / `write_open_run_model(...)` и не переписывает hidden evaluator статусы.

**Checkpoint**: All user stories are independently functional and state-safe

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Подтверждение целостности и фиксация результатов.

- [X] T021 [P] Запустить `python3 -m pytest tests/test_account_settings_entry.py tests/test_account_settings_state.py tests/test_self_info_profile.py` и сохранить вывод как артефакт.
- [X] T022 Запустить `python3 -m pytest tests` для регрессии и сохранить вывод как артефакт.
- [X] T023 Сверить сценарии из `specs/004-self-info-profile/quickstart.md` с покрытием тестов и обновить quickstart только при расхождении.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: starts immediately.
- **Phase 2 (Foundational)**: depends on Phase 1 and blocks all user stories.
- **Phase 3 (US1)**: starts after foundational storage/session support.
- **Phase 4 (US2)**: starts after US1 entry flow.
- **Phase 5 (US3)**: starts after US2 step flow exists.
- **Phase 6 (Polish)**: runs after implementation phases.

### User Story Dependencies

- **US1 (P1)**: independent after foundational phase.
- **US2 (P2)**: depends on US1 entry point and profile rendering.
- **US3 (P3)**: depends on US1/US2 flow, then validates safety boundaries.

### Within Each User Story

- Tests first, then implementation.
- Storage/session primitives before routing logic.
- Routing logic before final regression.

### Parallel Opportunities

- T002 and T004 can proceed in parallel after T001/T003 are started.
- T006 and T007 can run in parallel.
- T010, T011, T012 can run in parallel.
- T016, T017, T018 can run in parallel.

---

## Parallel Example: User Story 2

```bash
# Parallel test preparation for US2
Task: "T010 [US2] Strengths step test in tests/test_self_info_profile.py"
Task: "T011 [US2] Weaknesses step test in tests/test_self_info_profile.py"
Task: "T012 [US2] Extra fact step test in tests/test_self_info_profile.py"

# Then implementation
Task: "T013 [US2] Implement _profile_message_actions in app/telegram_poll.py"
Task: "T014 [US2] Implement visible profile writes in app/person.py"
Task: "T015 [US2] Add final profile actions in app/account_settings.py"
```

---

## Implementation Strategy

### MVP First (US1 only)

1. Complete Phases 1-2.
2. Deliver US1 read-only profile entry.
3. Validate independently.

### Incremental Delivery

1. Add US1 (open/read profile).
2. Add US2 (edit steps and persistence).
3. Add US3 (privacy + stale/invalid safety).
4. Run targeted and full regression after each increment.

### Parallel Team Strategy

1. One developer covers schema/person storage primitives.
2. Second developer prepares profile step tests.
3. Third developer integrates Telegram routing and safety checks.

---

## Notes

- Story scope is limited to user-visible profile read/edit/add.
- Hidden evaluator profile update-by-exercise is intentionally deferred to the next separate story.
