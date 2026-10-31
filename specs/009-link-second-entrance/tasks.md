---
description: "Task list for second entrance from settings and merge"
---

# Tasks: В настройках указать второй вход, подтвердить кодом и слить ходы

**Input**: Design documents from `/specs/009-link-second-entrance/`

**Prerequisites**: plan.md, spec.md

**Tests**: `tests/test_link_second_entrance.py` + channel coverage

**Organization**: Merge rules already in `app/entrances.py` / `app/app_links.py` and `/app/v1/settings/second-entrance*`. Remaining work is Flutter (and any thin API gaps). Depends on settings hub from `011-app-settings` for the app path; bot path already has settings buttons per plan.

## Format: `[ID] [P?] [Story] Description`

## Phase 1: Setup

- [ ] T001 Confirm `app/app_links.py`, bot settings wiring in `app/account_settings.py` / `app/telegram_poll.py`, and `tests/test_link_second_entrance.py` match plan.md
- [ ] T002 [P] Map second-entrance routes from `app/channel_api.py` to `mobile/lib/channel_client.dart`

---

## Phase 2: Foundational (Blocking)

**Purpose**: App can open second-entrance screen without starting model/profile/news flows

- [ ] T003 Verify `GET /app/v1/settings/second-entrance` returns email+telegram only (`opens_model`/`opens_profile` false) in `app/app_links.py` / `app/channel_api.py`
- [ ] T004 [P] Verify POST email / telegram / code paths call `submit_email_link` / `submit_telegram_link` / `submit_link_code` and do not merge on a single confirmed code — `app/channel_api.py`
- [ ] T005 [P] Extend `tests/test_link_second_entrance.py` and/or `tests/test_channel_api.py` for one-code-no-merge and both-codes-merge signals already required by the account rule

**Checkpoint**: Channel second-entrance ready for Flutter

---

## Phase 3: User Story 1 - Offer the second entrance (Priority: P1) 🎯 MVP

**Goal**: Same two additions (email, Telegram) in bot settings and in the app settings action

**Independent Test**: Open second-entrance in app (and keep bot menu) — both additions offered; model/profile edit does not start by itself from this screen

- [ ] T006 [US1] From the app settings hub (011), add entry «Второй вход» that opens `GET /settings/second-entrance` — `mobile/lib/main.dart` or `mobile/lib/settings_shell.dart` / new `mobile/lib/second_entrance.dart`
- [ ] T007 [P] [US1] Client method `openSecondEntrance` on `mobile/lib/channel_client.dart`
- [ ] T008 [US1] Screen offers only email and telegram actions (no model, no profile, no news start) in the Flutter second-entrance UI

**Checkpoint**: US1 visible in app

---

## Phase 4: User Story 2 - Confirm each entrance with its own code (Priority: P1)

**Goal**: Codes confirm separately; merge only after both latest codes; marks/profile rules unchanged (call existing merge)

**Independent Test**: Confirm one code → runs stay apart; confirm second latest code → both run sets on one person; differing marks → «неравномерно»; two visible texts remain

- [ ] T009 [P] [US2] Client methods for email link, telegram link, and code submit on `mobile/lib/channel_client.dart`
- [ ] T010 [US2] Email flow: enter address → show «код отправлен» / failure; wait for code — Flutter second-entrance UI
- [ ] T011 [US2] Telegram flow: enter identity → code in bot path; wait for code — same UI
- [ ] T012 [US2] Code submit UI: show rejected / still waiting / confirmed / merged texts from server; do not invent merge client-side — Flutter + `app/app_links.py` responses
- [ ] T013 [US2] After merge or confirm, return to settings hub without starting a news review — Flutter

**Checkpoint**: US1 + US2 complete

---

## Phase 5: Polish

- [ ] T014 [P] Run `py -3.12 -m pytest tests/test_link_second_entrance.py tests/test_channel_api.py`
- [ ] T015 Note APK rebuild for explicit implement/publish
- [ ] T016 Leave feature-map status for `/publish` after implement

---

## Dependencies

- App US1 assumes settings hub from `011-app-settings` (implement 011 before or with this story's Flutter entry).
- Account merge rules from `007` are called, not rewritten.
- Does not change model choice, self-info editing, or email sign-in screens beyond adding the second-entrance action.

## Implementation strategy

1. Confirm API/tests → Flutter offer screen → confirm/merge flows.
2. Prefer implementing **011** first so the settings hub exists; then this story's entry point.
3. Stop after tasks; wait for explicit `/speckit-implement`.
