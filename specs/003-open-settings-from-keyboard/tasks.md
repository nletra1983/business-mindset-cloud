# Tasks: Open Settings from Dialogue Keyboard

**Input**: Design documents from `/specs/003-open-settings-from-keyboard/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: `plan.md` фиксирует `pytest` как способ проверки маршрутизации клавиатуры, поэтому тестовые задачи включены.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Runtime code: `app/`
- Tests: `tests/`
- Spec artifacts: `specs/003-open-settings-from-keyboard/`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Подготовить общее место для callback-ключей и меню настроек.

- [ ] T001 Создать `app/account_settings.py` с константами callback-ключей (`settings`, `settings:model`, `settings:profile`) и текстовыми константами для меню первого уровня.
- [ ] T002 [P] Добавить новый тестовый файл `tests/test_account_settings_entry.py` с базовым каркасом проверок для кнопки входа в настройки и меню.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Добавить общий канал обработки нового типа действий, который используют все пользовательские истории.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T003 [P] Реализовать в `app/account_settings.py` фабрики payload для действий `settings_menu` и recoverable-ответа для устаревших/неподдерживаемых callback.
- [ ] T004 Добавить в `app/telegram_poll.py` обработку действия `settings_menu` в `_perform(...)` с отрисовкой меню из двух inline-кнопок.
- [ ] T005 В `app/telegram_poll.py` подключить callback-роутинг для `settings`, `settings:model`, `settings:profile` так, чтобы текущие ветки `to_list`, `m:*`, `r:*` и защита duplicate update (`_seen/_mark`) оставались рабочими.

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Open settings from supported dialogue contexts (Priority: P1) 🎯 MVP

**Goal**: Пользователь может открыть настройки из тех же мест, где раньше был прямой вход в выбор модели.

**Independent Test**: В незавершённом ходе, в списке ходов и после финала кнопка `настройки` открывает меню настроек.

### Tests for User Story 1

- [ ] T006 [P] [US1] Дописать `tests/test_account_settings_entry.py`: `exit_row(...)` в `app/run_list.py` возвращает кнопку `настройки` с callback `settings` вместо прямого model-opener.
- [ ] T007 [P] [US1] Дописать `tests/test_account_settings_entry.py`: при формировании ответа списка (`kind == "list"`) в `app/telegram_poll.py` клавиатура сохраняет доступ к `настройки`.

### Implementation for User Story 1

- [ ] T008 [US1] Обновить `app/run_list.py`: `exit_row(...)` использует кнопку `настройки` и callback из `app/account_settings.py`.
- [ ] T009 [US1] Обновить `app/telegram_poll.py`: ветка callback `settings` открывает меню настроек для поддерживаемых контекстов (незавершённый ход, список ходов, пост-финал).
- [ ] T010 [US1] В `app/telegram_poll.py` убедиться, что стандартные send/edit-ответы после открытия настроек не теряют навигационную клавиатуру и не создают новый ход.

**Checkpoint**: User Story 1 is fully functional and independently testable

---

## Phase 4: User Story 2 - Show two clear settings options and route each one (Priority: P2)

**Goal**: В меню настроек отображаются ровно два пункта, и каждый ведёт в ожидаемую ветку.

**Independent Test**: После нажатия `настройки` отображаются `выбор модели` и `информация о себе`; выбор каждого пункта ведёт в соответствующую ветку.

### Tests for User Story 2

- [ ] T011 [P] [US2] Дописать `tests/test_account_settings_entry.py`: меню настроек содержит ровно два пункта с подписями `выбор модели` и `информация о себе`.
- [ ] T012 [P] [US2] Дописать `tests/test_account_settings_entry.py`: callback `settings:model` использует существующий поток выбора модели, а `settings:profile` уводит в entry-point ветки профиля.

### Implementation for User Story 2

- [ ] T013 [US2] Реализовать в `app/account_settings.py` inline-меню первого уровня с двумя пунктами и фиксированным порядком: `выбор модели`, `информация о себе`.
- [ ] T014 [US2] Обновить `app/telegram_poll.py`: callback `settings:model` возвращает текущий flow выбора модели (`kind: models`, `PICK_TEXT`, `current`).
- [ ] T015 [US2] Обновить `app/telegram_poll.py`: callback `settings:profile` возвращает entry-point сообщение для следующей истории без показа скрытого профиля.

**Checkpoint**: User Stories 1 and 2 both work independently

---

## Phase 5: User Story 3 - Preserve run state and handle stale callbacks safely (Priority: P3)

**Goal**: Открытие настроек не ломает ход; неподдерживаемые/устаревшие callback обрабатываются восстановимо.

**Independent Test**: При входе в настройки шаг/статус/транскрипт не меняются; stale callback даёт recoverable-ответ и не портит данные.

### Tests for User Story 3

- [ ] T016 [P] [US3] Добавить `tests/test_account_settings_state.py`: открытие `settings` не меняет `run.step`, `run.status` и не добавляет новые реплики в текущем ходе.
- [ ] T017 [P] [US3] Добавить `tests/test_account_settings_state.py`: неподдерживаемый или устаревший callback возвращает recoverable-сообщение и не меняет `person.current_model` / `run.model_requested`.

### Implementation for User Story 3

- [ ] T018 [US3] Обновить `app/telegram_poll.py`: для неподдерживаемых/stale settings-callback возвращать recoverable user message вместо молчаливого no-op.
- [ ] T019 [US3] Обновить `app/telegram_poll.py`: гарантировать, что ветка `settings` не вызывает `write_model_state(...)`, `write_open_run_model(...)` и не изменяет окно хода.
- [ ] T020 [US3] При необходимости уточнить helper-логику в `app/account_settings.py`, чтобы recoverable-путь и обычный путь имели единый формат действий для `_perform(...)`.

**Checkpoint**: All user stories are independently functional and state-safe

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Финальная валидация и фиксация результата.

- [ ] T021 [P] Запустить `pytest tests/test_account_settings_entry.py tests/test_account_settings_state.py tests/test_model_choice.py` и зафиксировать результат в артефакте.
- [ ] T022 Пройти сценарии из `specs/003-open-settings-from-keyboard/quickstart.md` и зафиксировать итоги (happy path + stale callback) в артефакте.
- [ ] T023 Обновить `specs/003-open-settings-from-keyboard/quickstart.md` только если фактические шаги проверки отличаются от текущего описания.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: starts immediately.
- **Phase 2 (Foundational)**: depends on Phase 1 and blocks all user stories.
- **Phase 3 (US1)**: starts after Phase 2.
- **Phase 4 (US2)**: starts after US1 entry flow exists (Phase 3).
- **Phase 5 (US3)**: starts after US1/US2 callback routing is in place.
- **Phase 6 (Polish)**: runs after all targeted stories are implemented.

### User Story Dependencies

- **US1 (P1)**: no dependency on other stories after foundational work.
- **US2 (P2)**: depends on US1 entry point, then remains independently testable.
- **US3 (P3)**: depends on callback paths from US1/US2, then validates invariants independently.

### Within Each User Story

- Tests first, then implementation.
- Callback/menu helpers before handler integration.
- Handler integration before final regression checks.

### Parallel Opportunities

- T002 and T003 can proceed in parallel after T001.
- T006 and T007 can run in parallel.
- T011 and T012 can run in parallel.
- T016 and T017 can run in parallel.
- Final validation T021 can run independently from documentation touch-up T023.

---

## Parallel Example: User Story 2

```bash
# Parallel test tasks for US2
Task: "T011 [US2] Validate settings menu has exactly two options in tests/test_account_settings_entry.py"
Task: "T012 [US2] Validate routing for settings:model and settings:profile in tests/test_account_settings_entry.py"

# Then implementation sequence
Task: "T013 [US2] Build settings first-level menu in app/account_settings.py"
Task: "T014 [US2] Route settings:model in app/telegram_poll.py"
Task: "T015 [US2] Route settings:profile in app/telegram_poll.py"
```

---

## Implementation Strategy

### MVP First (US1 only)

1. Finish Phases 1-2.
2. Implement Phase 3 (US1).
3. Validate US1 independently from quickstart scenarios.
4. Demo/merge if only MVP entry point is needed.

### Incremental Delivery

1. Add US1 (entry availability in contexts).
2. Add US2 (clear menu options + routing).
3. Add US3 (state safety + stale callback handling).
4. Re-run targeted tests and quickstart after each increment.

### Parallel Team Strategy

1. One developer takes foundational callback/action plumbing (Phase 2).
2. Second developer prepares story tests (T006/T011/T016 branches).
3. After Phase 2, split by stories:
   - Dev A: US1 implementation
   - Dev B: US2 implementation
   - Dev C: US3 invariants/recoverable handling

---

## Notes

- Every task includes exact file paths.
- Story phases are isolated so each story can be validated independently.
- Do not expand into full profile editing in this feature; only entry-point routing is in scope.
