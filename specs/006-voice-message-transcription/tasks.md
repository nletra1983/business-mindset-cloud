# Tasks: Voice Message Becomes Text in Existing Flows

**Input**: Design documents from `/specs/006-voice-message-transcription/`

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
- Spec artifacts: `specs/006-voice-message-transcription/`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Подготовить voice-константы и тестовый каркас для новой ветки входящих сообщений.

- [ ] T001 Добавить в `app/account_settings.py` текстовые константы recoverable-ответов для voice-flow (`Эта модель не разбирает голос.`, `Голос не разобран.`) и helpers для action-ответов.
- [ ] T002 [P] Создать `tests/test_voice_messages.py` с каркасом сценариев US1-US3.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Добавить общий pipeline voice->text перед существующей обработкой текста.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T003 Реализовать в `app/model_client.py` voice transcription interface с retry-повтором по правилам model-call и явной ошибкой неподдерживаемой voice-capability для моделей без подтверждённого voice-path.
- [ ] T004 [P] Добавить в `app/telegram_poll.py` функции загрузки voice-файла из Telegram (`getFile` + download bytes) без сохранения audio на диск/в БД.
- [ ] T005 В `app/telegram_poll.py` расширить входящий message route: поддержать `message.voice`, оставить `message.text` поведение неизменным, `audio`/`video_note` не обрабатывать как voice этой истории.
- [ ] T006 В `app/telegram_poll.py` реализовать общий `_voice_message_actions(...)`: unsupported/empty outcomes не двигают шаг, recognized text сначала отправляется как отдельное сообщение, потом проходит через текущий text-flow.

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Voice reply enters the same dialogue flow as typed text (Priority: P1) 🎯 MVP

**Goal**: Voice from microphone становится текстом и обрабатывается теми же правилами, что typed text.

**Independent Test**: При валидном распознавании бот сначала показывает распознанный текст, затем выполняет те же state transitions, что и для текстового сообщения.

### Tests for User Story 1

- [ ] T007 [P] [US1] Дописать `tests/test_voice_messages.py`: при `message.voice` и валидном распознавании `_dispatch` отправляет распознанный текст отдельным сообщением и затем вызывает существующий text path.
- [ ] T008 [P] [US1] Дописать `tests/test_voice_messages.py`: profile-edit step (`read_profile_edit_step != idle`) обрабатывает распознанный текст теми же profile rules, что и typed text.

### Implementation for User Story 1

- [ ] T009 [US1] В `app/telegram_poll.py` подключить recognized text к существующим вызовам `_profile_message_actions(...)` и `handle_text(...)`, не создавая отдельный run-flow.
- [ ] T010 [US1] В `app/telegram_poll.py` гарантировать, что распознанный текст отправляется отдельным bot message без дополнительной подписи.

**Checkpoint**: User Story 1 is fully functional and independently testable

---

## Phase 4: User Story 2 - Unsupported voice capability does not move dialogue state (Priority: P2)

**Goal**: Неподдерживаемая модель возвращает понятный ответ без изменения run/profile step.

**Independent Test**: При выбранной неподдерживаемой модели voice-сообщение возвращает `Эта модель не разбирает голос.` и не вызывает text-flow.

### Tests for User Story 2

- [ ] T011 [P] [US2] Дописать `tests/test_voice_messages.py`: unsupported model возвращает `Эта модель не разбирает голос.` без вызовов `handle_text(...)`/profile writes.
- [ ] T012 [P] [US2] Дописать `tests/test_voice_messages.py`: `audio` и `video_note` не проходят через voice pipeline этой истории.

### Implementation for User Story 2

- [ ] T013 [US2] В `app/model_client.py` и `app/telegram_poll.py` добавить явную unsupported ветку для моделей без подтверждённого voice-path.
- [ ] T014 [US2] Проверить, что unsupported ветка не изменяет model state, run status и profile-edit step.

**Checkpoint**: User Stories 1 and 2 both work independently

---

## Phase 5: User Story 3 - Empty recognition result is recoverable and preserves state (Priority: P3)

**Goal**: Пустой результат распознавания даёт recoverable сообщение без побочных изменений состояния.

**Independent Test**: При пустом распознанном тексте бот отвечает `Голос не разобран.` и не вызывает text-flow.

### Tests for User Story 3

- [ ] T015 [P] [US3] Дописать `tests/test_voice_messages.py`: empty transcription возвращает `Голос не разобран.` и не двигает шаг.
- [ ] T016 [P] [US3] Дописать `tests/test_voice_messages.py`: duplicate update behavior для voice остаётся защищённым существующим dedup path.

### Implementation for User Story 3

- [ ] T017 [US3] В `app/telegram_poll.py` добавить обработку empty transcription как recoverable outcome с нулевым влиянием на шаги.
- [ ] T018 [US3] В `app/telegram_poll.py` убедиться, что ошибка загрузки/распознавания voice не пробрасывает state-changing side effects.

**Checkpoint**: All user stories are independently functional and state-safe

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Финальная валидация и синхронизация с quickstart.

- [ ] T019 [P] Запустить `python3 -m pytest tests/test_voice_messages.py tests/test_account_settings_state.py tests/test_self_info_profile.py tests/test_skill_gate.py` и сохранить вывод как артефакт.
- [ ] T020 Запустить `python3 -m pytest tests` для регрессии и сохранить вывод как артефакт.
- [ ] T021 Сверить `specs/006-voice-message-transcription/quickstart.md` с фактическим покрытием тестов и обновить quickstart при расхождении.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: starts immediately.
- **Phase 2 (Foundational)**: depends on Phase 1 and blocks all user stories.
- **Phase 3 (US1)**: starts after voice pipeline foundation.
- **Phase 4 (US2)**: starts after US1 baseline voice->text behavior.
- **Phase 5 (US3)**: starts after US1/US2 outcomes are implemented.
- **Phase 6 (Polish)**: runs after implementation phases.

### User Story Dependencies

- **US1 (P1)**: independent after foundational phase.
- **US2 (P2)**: depends on US1/Foundational pipeline and adds unsupported guardrails.
- **US3 (P3)**: depends on US1/US2 to validate empty-result and error outcomes.

### Within Each User Story

- Tests first, then implementation.
- Voice download/transcription primitives before route integration.
- Outcome-specific branches after baseline recognized-text path is stable.

### Parallel Opportunities

- T002 and T004 can run in parallel after T001/T003.
- T007 and T008 can run in parallel.
- T011 and T012 can run in parallel.
- T015 and T016 can run in parallel.

---

## Parallel Example: User Story 1

```bash
# Parallel test preparation for US1
Task: "T007 [US1] Voice recognized-text route test in tests/test_voice_messages.py"
Task: "T008 [US1] Profile-edit compatibility test in tests/test_voice_messages.py"

# Then implementation
Task: "T009 [US1] Integrate recognized text into existing text-flow in app/telegram_poll.py"
Task: "T010 [US1] Emit recognized text as standalone message in app/telegram_poll.py"
```

---

## Implementation Strategy

### MVP First (US1 only)

1. Complete Phases 1-2.
2. Deliver US1 voice->text integration through current text-flow.
3. Validate independently.

### Incremental Delivery

1. Add US1 (recognized text path).
2. Add US2 (unsupported capability guard).
3. Add US3 (empty/error recoverable outcomes).
4. Run targeted and full regression after each increment.

### Parallel Team Strategy

1. Один разработчик готовит model_client + download primitives.
2. Второй готовит voice-route tests.
3. Третий интегрирует `telegram_poll` path и проверяет регрессии профиля/хода.

---

## Notes

- Граница истории: voice message превращается в text и проходит существующие правила; новые каналы/виды упражнений не добавляются.
- Audio payload после распознавания не хранится.
