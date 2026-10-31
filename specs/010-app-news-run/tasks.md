---
description: "Task list for start/resume news review in the app"
---

# Tasks: Начать разбор новости в приложении и вернуться в незаконченный

**Input**: Design documents from `/specs/010-app-news-run/`

**Prerequisites**: plan.md (required), spec.md (required)

**Tests**: plan.md asks for `pytest`; include focused tests. Flutter widget tests only if already in the mobile harness.

**Organization**: Server rules already live in `app/app_news.py` and `/app/v1` routes; remaining work is gaps on the server path with Postgres and the Flutter list/run screens from `specs/008` / `014`.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: US1 / US2 from spec.md
- Exact file paths in every task

## Phase 1: Setup

**Purpose**: Confirm the feature folder and existing seams

- [x] T001 Confirm `app/app_news.py` and `tests/test_app_news_run.py` match plan.md structure; note any missing seam for Flutter in `specs/010-app-news-run/tasks.md` notes only if found during implement
- [x] T002 [P] Read `specs/012-app-channel-api/contracts/app-channel-v1.md` run endpoints and map them to Flutter client methods in `mobile/lib/channel_client.dart`

---

## Phase 2: Foundational (Blocking)

**Purpose**: List + start/resume/answer usable from the app channel without past/redo/delete

**⚠️ CRITICAL**: No Flutter story UI until blank-topic and list payload are honest for `/app/v1`

- [x] T003 Reject empty or content-free `topic` on `POST /app/v1/runs` when `conn` is present (same product wording as memory path) in `app/channel_api.py`
- [x] T004 [P] Ensure `GET /app/v1/runs` (or documented list path used by the app) returns enough fields to open an unfinished run (id + label/step) without offering past/redo/delete — `app/channel_api.py`, reuse `app/app_news.py` `list_screen` / `LIST_ACTIONS` / `EXCLUDED_ACTIONS` as needed
- [x] T005 [P] Add or extend channel API tests for blank topic and list shape in `tests/test_channel_api.py` (and keep `tests/test_app_news_run.py` green)

**Checkpoint**: Foundation ready — Flutter can call start/list/resume/answer safely

---

## Phase 3: User Story 1 - Start a review from the person's own words (Priority: P1) 🎯 MVP

**Goal**: From the run list in the app, submit a formulation and get the first question; empty formulation does not start a run

**Independent Test**: Real wording → one new open run and one question on screen. Empty → message to formulate again, no new run

### Implementation for User Story 1

- [x] T006 [P] [US1] Add `startRun` (POST `/runs` with `topic`, optional Idempotency-Key) on `mobile/lib/channel_client.dart`
- [x] T007 [US1] On the post-login list screen in `mobile/lib/main.dart` (or a small dedicated widget file under `mobile/lib/`), add formulation field + start action; show server question/actions; surface blank-topic error without inventing an event
- [x] T008 [US1] Refresh the run list after a successful start in `mobile/lib/main.dart` (or the widget introduced in T007)

**Checkpoint**: US1 works on device/emulator against `CHANNEL_BASE_URL`

---

## Phase 4: User Story 2 - Return to an unfinished review (Priority: P1)

**Goal**: Open unfinished run from the list at the same step; leave to list keeps it unfinished; duplicate answer delivery does not move twice; cannot start another run from inside the open run

**Independent Test**: Open unfinished → same step; back to list → still unfinished; second identical Idempotency-Key answer → no second move; no «new run» control inside the run screen

### Implementation for User Story 2

- [x] T009 [P] [US2] Add `resumeRun` and `answerRun` (with Idempotency-Key) on `mobile/lib/channel_client.dart`
- [x] T010 [US2] Make list items open resume in `mobile/lib/main.dart` (or run screen widget under `mobile/lib/`); show current step/actions from the server
- [x] T011 [US2] Add answer field + send on the open-run screen; reuse Idempotency-Key so a repeated delivery does not move the step twice — `mobile/lib/main.dart` / `mobile/lib/channel_client.dart`
- [x] T012 [US2] Add explicit back-to-list that leaves the run unfinished (no pause status) and does not offer past/redo/delete — `mobile/lib/main.dart`
- [x] T013 [US2] Ensure the open-run screen has no control to start another review (FR-006) in `mobile/lib/main.dart`

**Checkpoint**: US1 and US2 both work from the APK list

---

## Phase 5: Polish & Cross-Cutting

- [x] T014 [P] Run `py -3.12 -m pytest tests/test_app_news_run.py tests/test_channel_api.py`
- [x] T015 Rebuild author APK with `CHANNEL_BASE_URL=https://get-business-idea.ru` via `mobile/tool/build_author_apk.ps1` when Flutter changes are ready
- [x] T016 Update story status for «Начать разбор новости…» in `features/feature-map.md` (or leave for `/publish`)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: immediate
- **Foundational (Phase 2)**: after Setup — blocks Flutter stories
- **US1 (Phase 3)**: after Foundational — MVP
- **US2 (Phase 4)**: after Foundational; uses the same list screen as US1 (T007)
- **Polish (Phase 5)**: after desired stories

### User Story Dependencies

- **US1**: no dependency on US2
- **US2**: shares list shell with US1; independently testable once list + resume/answer client exist

### Parallel Opportunities

- T002 || T001
- T004 || T005 after T003 (T005 may follow T003+T004)
- T006 || early draft of T009 (different methods in same file — serialize if one edit)
- T014 || T015 after code complete

---

## Parallel Example: User Story 1

```text
Task: "Add startRun on mobile/lib/channel_client.dart"
Task: "Formulation field + start on list screen in mobile/lib/main.dart"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1–2
2. Phase 3 (US1)
3. Validate empty vs real formulation
4. Then US2

### Incremental Delivery

1. Foundational API honesty → US1 start → US2 resume/answer/back
2. Do not add past-review card, topic redo, or delete

## Notes

- Do not rewrite bot news rules; call existing `begin_from_list` / `resume_from_list` / `handle_text`.
- App must not call a model provider.
- Account settings and second entrance are out of scope.
