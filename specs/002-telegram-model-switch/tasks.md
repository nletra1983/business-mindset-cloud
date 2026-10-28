# Tasks: Переключение модели в разборе

**Input**: Design documents from `/specs/002-telegram-model-switch/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: `plan.md` просит `pytest` на выбор, зелёную кнопку и откат после двух неудач. Эти тесты включены. Живой Telegram в них не нужен.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Код: `app/` в корне `D:\Business_mindset`
- Тесты: `tests/`
- Сервер: тот же сервис `bot` в `/opt/business-mindset`, без второго процесса

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Отдать уже лежащие ключи в тот же контейнер

- [ ] T001 [P] Добавить `./secrets/sber.env` и `./secrets/zai.env` в `env_file` сервиса `bot` в `docker-compose.yml`. Сервис `db` не менять. Второй сервис не добавлять. Значения ключей не писать.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Хранение выбора и вызов трёх моделей. Без этого истории не начинаются.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T002 Добавить в `app/schema.sql` к уже существующей таблице `person` колонки `current_model text NOT NULL` со значением по умолчанию `deepseek-chat` и `last_answered_model text NULL`. Для уже созданной таблицы использовать `ADD COLUMN IF NOT EXISTS`, а не только `CREATE TABLE IF NOT EXISTS`. Статус `paused` и `DELETE` не добавлять.
- [ ] T003 [P] Записать в `app/config.py` три модели в порядке DeepSeek `deepseek-chat`, GigaChat `GigaChat-2`, GLM `glm-5.3-flash` и подписи кнопок `DeepSeek`, `GigaChat`, `GLM`.
- [ ] T004 В `app/person.py` читать и записывать `current_model` и `last_answered_model`. Telegram user id остаётся только привязкой, не ключом человека.
- [ ] T005 Реализовать в `app/model_client.py` один вызов по id модели через `httpx`. DeepSeek: `POST https://api.deepseek.com/chat/completions`, модель `deepseek-chat`. GigaChat: `POST https://ngw.devices.sberbank.ru:9443/api/v2/oauth` со scope `GIGACHAT_API_PERS` и ключом `GIGACHAT_AUTH_KEY`, затем `POST https://api.giga.chat/v1/chat/completions`, модель `GigaChat-2`; токен человеку не показывать и в Postgres не писать; проверку TLS не отключать. GLM: `POST https://api.z.ai/api/paas/v4/chat/completions`, `Authorization: Bearer` и `ZAI_API_KEY`, модель `glm-5.3-flash`. Отдельный SDK не добавлять.

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Сменить модель в текущем разборе (Priority: P1) 🎯 MVP

**Goal**: В незавершённом ходе кнопка «модель» показывает три имени, выбор делает модель текущей, следующий вызов идёт ею, уже принятые ответы остаются.

**Independent Test**: В одном незавершённом разборе выбрать другую модель и дать следующий ответ. Следующий ответ идёт выбранной моделью, прежние ответы на месте, второй разбор не появился.

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T006 [P] [US1] Написать падающий `pytest` в `tests/test_model_choice.py`: выбор имени ставит `current_model`, у открытого хода `model_requested` становится тем же id, уже записанные реплики не меняются, у текущей кнопки стиль `success`, у двух остальных стиля нет.

### Implementation for User Story 1

- [ ] T007 [US1] Добавить кнопку «модель» рядом с «к другим вопросам» в `app/run_list.py`.
- [ ] T008 [US1] В `app/telegram_poll.py` по нажатию «модель» показывать три кнопки в порядке DeepSeek, GigaChat, GLM. Текущая — стиль `success`. Нажатие имени ставит `current_model` и `model_requested` открытого хода. Новый ход не создаётся. Текст кнопок не размечается жирным. Тот же update id проходит через уже существующую проверку `processed_telegram_update` и второй раз модель не меняет.
- [ ] T009 [US1] В `app/run_flow.py` следующий вопрос, оценка ответа и финал незавершённого хода вызывают `app/model_client.py` с `model_requested` этого хода. Уже принятые ответы не переписываются.

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Выбор сохраняется вне шага разбора (Priority: P2)

**Goal**: Выбор в списке ходов и после финала запоминается за человеком. Завершённый ход не меняется. Пока человек не выбирал, текущая модель — DeepSeek.

**Independent Test**: После финала выбрать другую модель. Завершённый ход тот же. Следующий новый ход зовёт выбранную модель.

### Tests for User Story 2 ⚠️

- [ ] T010 [P] [US2] Написать падающий `pytest` в `tests/test_model_memory.py`: смена после `status = completed` не меняет реплики, сводку и `model_requested` этого хода; `current_model` человека меняется; при отсутствии выбора `current_model` равен `deepseek-chat`.

### Implementation for User Story 2

- [ ] T011 [US2] В `app/telegram_poll.py` выбор из списка ходов и после финала обновляет только `current_model` человека. Если ход уже `completed`, его `model_requested`, реплики и сводку не обновлять.

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Выбранная модель не ответила (Priority: P3)

**Goal**: После вызова и одного повтора без ответа человек видит, что выбранная модель недоступна, и в том же сообщении три кнопки. Ход не завершается. Если модель уже отвечала, текущей становится она. Если нет — подставлять некого.

**Independent Test**: Довести один вызов до двух неудач. Одно сообщение о недоступности, три кнопки, ход всё ещё `open`.

### Tests for User Story 3 ⚠️

- [ ] T012 [P] [US3] Написать падающий `pytest` в `tests/test_model_down.py`: первый обрыв повторяет тот же вызов один раз; второй обрыв при заполненном `last_answered_model` ставит его в `current_model` и в `model_requested` открытого хода, статус остаётся `open`; при пустом `last_answered_model` `current_model` не подменяется.

### Implementation for User Story 3

- [ ] T013 [US3] В `app/model_client.py` повторять неудачный вызов один раз. В `app/run_flow.py` после второго обрыва не завершать ход и не вводить статус «пауза». Если `last_answered_model` заполнен, сделать его `current_model` и `model_requested` открытого хода. Если пуст, оставить `current_model`. Успешный ответ записывает запрошенный id в `last_answered_model`.
- [ ] T014 [US3] В `app/telegram_poll.py` сообщение о недоступности выбранной модели содержит те же три кнопки. Зелёная (`success`) — та, что стала текущей после правила T013.

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Проверка на уже работающем контуре

- [ ] T015 Пройти сценарии `specs/002-telegram-model-switch/quickstart.md` на существующем контуре: из `/opt/business-mindset` выполнить `docker compose up -d --build bot`. Второй процесс бота не запускать. Значения ключей не выводить.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2). Правка `app/telegram_poll.py` идёт после T008, чтобы не переписывать тот же обработчик вслепую. Проверка T010 от US1 не зависит.
- **User Story 3 (P3)**: Can start after Foundational (Phase 2). T013 зависит от вызова в T009. T014 идёт после T008.

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- T001 и T003 не зависят друг от друга
- T002 и T003 можно делать параллельно
- T006, T010 и T012 — разные файлы тестов; их можно писать параллельно после Phase 2
- T007, T008 и T009 трогают разные файлы и идут после T006
- T011 и T014 оба правят `app/telegram_poll.py`, поэтому не параллельны

---

## Parallel Example: User Story 1

```bash
# После Phase 2 тесты трёх историй можно писать вместе:
Task: "tests/test_model_choice.py"
Task: "tests/test_model_memory.py"
Task: "tests/test_model_down.py"

# Реализация US1 по разным файлам:
Task: "Кнопка «модель» в app/run_list.py"
Task: "Список и выбор в app/telegram_poll.py"
Task: "Вызов текущей модели в app/run_flow.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- Флаг моделей в аккаунте, свой ключ, оплата и статус «пауза» в эти задачи не входят
