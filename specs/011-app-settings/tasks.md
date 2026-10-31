---
description: "Task list for app account settings (model + visible profile)"
---

# Tasks: Открыть настройки того же входа: модель и информация о себе

**Input**: Design documents from `/specs/011-app-settings/`

**Prerequisites**: plan.md, spec.md

**Tests**: plan asks for pytest; keep `tests/test_app_settings.py` green and extend channel coverage where needed.

**Organization**: Server helpers already in `app/app_settings.py` and `/app/v1/settings*`. Remaining work is profile write seams (if missing) and Flutter screens at the three moments. Second entrance is **out of scope** (story 009).

## Format: `[ID] [P?] [Story] Description`

## Phase 1: Setup

- [ ] T001 Confirm `app/app_settings.py` and `tests/test_app_settings.py` match plan.md; list existing `/app/v1/settings` routes in `app/channel_api.py`
- [ ] T002 [P] Map settings contract from `specs/012-app-channel-api/contracts/app-channel-v1.md` to methods in `mobile/lib/channel_client.dart`

---

## Phase 2: Foundational (Blocking)

**Purpose**: Channel can open settings, choose model, read/edit visible profile without second-entrance or news actions

- [ ] T003 Ensure `GET /app/v1/settings` returns model+profile only (`offers_second_entrance: false`) via `app/app_settings.py` / `app/channel_api.py`
- [ ] T004 [P] Persist model choice on `POST /app/v1/settings/models` to person/run using existing bot rules in `app/channel_api.py` (call `choose_model` / `apply_choice` with real `conn` when present)
- [ ] T005 [P] Add profile write endpoints for strengths, then weaknesses, then optional fact (visible file only; hidden marks unchanged) in `app/channel_api.py` and thin helpers in `app/app_settings.py` if missing
- [ ] T006 Extend `tests/test_app_settings.py` and/or `tests/test_channel_api.py` for model change phrase, no second-entrance action, and visible-only profile edit

**Checkpoint**: API ready for Flutter settings

---

## Phase 3: User Story 1 - Open settings at the same moments (Priority: P1) 🎯 MVP

**Goal**: Settings reachable during unfinished run, from run list, and after finale; actions are model + profile only

**Independent Test**: Those three moments show a settings entry; no invented fourth moment; no second-entrance merge from this screen

- [ ] T007 [US1] Add a «Настройки» entry on the run list, open-run, and after-finale surfaces in `mobile/lib/main.dart` (or `mobile/lib/settings_shell.dart`) using `settings_available` moments from the product rule
- [ ] T008 [US1] Open settings hub that lists only model and profile (no second entrance, no start review) via `GET /settings` in `mobile/lib/main.dart` / `mobile/lib/settings_shell.dart`
- [ ] T009 [P] [US1] Add `openSettings` on `mobile/lib/channel_client.dart`

**Checkpoint**: US1 moments work on device

---

## Phase 4: User Story 2 - Choose model and edit visible profile (Priority: P1)

**Goal**: Model choice shows «Модель изменена.»; visible profile edit asks strengths then weaknesses and may add a fact; hidden marks never shown/changed

**Independent Test**: Pick a model → phrase + current matches; edit visible text → zero hidden marks on screen and in store

- [ ] T010 [P] [US2] Add `getModels` / `chooseModel` / `getProfile` / profile save methods on `mobile/lib/channel_client.dart`
- [ ] T011 [US2] Model picker screen using server model list and current; show server text after choice — `mobile/lib/main.dart` or `mobile/lib/settings_shell.dart`
- [ ] T012 [US2] Visible profile flow: show file, ask strengths, then weaknesses, optional fact; never render hidden skill marks — same Flutter files
- [ ] T013 [US2] Return from settings to the same moment (list / open run / after finale) without starting a news review — `mobile/lib/main.dart`

**Checkpoint**: US1 + US2 complete for this story

---

## Phase 5: Polish

- [ ] T014 [P] Run `py -3.12 -m pytest tests/test_app_settings.py tests/test_channel_api.py`
- [ ] T015 Note APK rebuild for `/speckit-implement` / `/publish` (do not publish from tasks)
- [ ] T016 Leave feature-map status update for `/publish` after implement

---

## Dependencies

- US2 uses the hub from US1.
- Does not implement second entrance (009) or news start (010).
- Reuses bot model/profile rules; does not invent unavailable-model behavior.

## Implementation strategy

1. Foundational API writes → settings hub at three moments → model → profile.
2. Stop after tasks; wait for explicit `/speckit-implement`.
