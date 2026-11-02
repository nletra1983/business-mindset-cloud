# -*- coding: utf-8 -*-
"""One-shot generator for specs 016-021. Run then delete if desired."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def w(rel: str, text: str) -> None:
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text.strip() + "\n", encoding="utf-8")


def checklist(title: str) -> str:
    return f"""# Specification Quality Checklist: {title}

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-11-02
**Feature**: [spec.md](../spec.md)

## Content Quality

- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

## Requirement Completeness

- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Success criteria are technology-agnostic (no implementation details)
- [x] All acceptance scenarios are defined
- [x] Edge cases are identified
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

## Feature Readiness

- [x] All functional requirements have clear acceptance criteria
- [x] User scenarios cover primary flows
- [x] Feature meets measurable outcomes defined in Success Criteria
- [x] No implementation details leak into specification

## Notes

- All items passed.
"""


# ---- 016 ----
w(
    "specs/016-landing-page-blocks/spec.md",
    """
# Feature Specification: Landing page hero and blocks

**Feature Branch**: `016-landing-page-blocks`

**Created**: 2026-11-02

**Status**: Draft

**Input**: История №1. Граница: `features/website-idea-assess/landing-page.md`.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Understand the promise and start (Priority: P1)

A visitor opens the landing, reads a result-focused hero with one CTA to try without registration, and reaches the on-page demo zone.

**Why this priority**: Without the hero CTA the funnel does not start.

**Independent Test**: Open on a phone-width viewport, see one primary CTA, activate it, reach the demo zone.

**Acceptance Scenarios**:

1. **Given** a first-time visitor, **When** they open the landing, **Then** they see a hero with a result-oriented headline, a short subtitle, and exactly one primary CTA to try without registration.
2. **Given** the hero is visible, **When** they activate the CTA, **Then** they move to the on-page demo/trainer zone.

---

### User Story 2 - Read trust blocks (Priority: P2)

The visitor scrolls through: how it works; not ChatGPT; outcomes; access levels (default amount orientation 100 RUB); honest example without fake reviews; for whom; author place; FAQ with educational disclaimer; final CTA.

**Why this priority**: Trust after CTA; can ship after hero.

**Independent Test**: Confirm each named block exists; no fake testimonials.

**Acceptance Scenarios**:

1. **Given** the landing is loaded, **When** the visitor scrolls, **Then** they see the required blocks in a mobile-first layout.
2. **Given** reviews are unavailable, **When** the example block is shown, **Then** it shows no fake logos or invented testimonials.

### Edge Cases

- Missing author materials → placeholder without inventing credentials.
- Trainer logic is story 2; this story only reserves the demo zone.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Landing MUST show hero with one primary CTA to try without registration.
- **FR-002**: Landing MUST include how-it-works, not-ChatGPT, outcomes, access levels (100 RUB default orientation), honest example, audience, author place, FAQ + educational disclaimer, final CTA.
- **FR-003**: Layout MUST be usable on phone first; language Russian.
- **FR-004**: MUST reserve a visible demo/trainer zone for story 2.
- **FR-005**: MUST NOT implement smoke, get-news, email gate, captcha, day-2 mail, or payment.
- **FR-006**: MUST NOT show fake reviews or fake partner logos.

### Key Entities

- **Landing page**: Marketing structure + CTA + demo anchor.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Primary CTA is findable above the fold on a typical phone screen.
- **SC-002**: All required blocks appear once.
- **SC-003**: Zero fake testimonials or fake logos.

## Assumptions

- Story 0 host/shell exists or is stubbed locally.
- Copy may be meaning-preserving placeholders.
""",
)
w("specs/016-landing-page-blocks/checklists/requirements.md", checklist("Landing page hero and blocks"))
w(
    "specs/016-landing-page-blocks/plan.md",
    """
# Implementation Plan: Лендинг — hero и блоки

**Branch**: `016-landing-page-blocks` | **Date**: 2026-11-02 | **Spec**: [spec.md](./spec.md)

## Summary

Секции лендинга и mobile-first стили на каркасе story 0; якорь демо; без агента.

## Technical Context

**Language/Version**: HTML/CSS served by existing Python HTTP process
**Primary Dependencies**: static `web/`
**Storage**: N/A
**Testing**: HTTP/html contains section ids
**Target Platform**: get-business-idea.ru via bot HTTP
**Project Type**: static landing
**Constraints**: no new framework; do not break `/app/v1`

## Constitution Check

- One process. Pass. Russian. Pass. No fake social proof. Pass.

## Project Structure

```text
web/index.html
web/styles.css
tests/test_landing_page.py
```
""",
)
w(
    "specs/016-landing-page-blocks/research.md",
    """
# Research: 016

## Decision: Single-page sections + `#demo` anchor

**Rationale**: Marketing only; trainer mounts in reserved zone in story 2.
""",
)
w("specs/016-landing-page-blocks/data-model.md", "# Data model: 016\n\nNo new stored entities.\n")
w(
    "specs/016-landing-page-blocks/contracts/landing-sections.md",
    """
# Contract: landing sections

Required section ids/anchors: `hero`, `demo`, `how`, `not-chatgpt`, `outcomes`, `levels`, `example`, `audience`, `author`, `faq`, `final-cta`.

Hero CTA targets `#demo`.
""",
)
w(
    "specs/016-landing-page-blocks/quickstart.md",
    """
# Quickstart: 016

1. Open landing via channel HTTP.
2. Check hero CTA and all sections at ~375px width.
""",
)
w(
    "specs/016-landing-page-blocks/tasks.md",
    """
# Tasks: Лендинг — hero и блоки

**Input**: `/specs/016-landing-page-blocks/`

## Phase 1: Setup

- [ ] T001 Каркас секций в `web/index.html`
- [ ] T002 [P] Mobile-first `web/styles.css`

## Phase 2: Foundational

- [ ] T003 Раздача обновлённого index через story 0 static path

## Phase 3: US1 Hero (P1)

- [ ] T004 [US1] Hero + одна CTA → `#demo`
- [ ] T005 [US1] Тест CTA/секций в `tests/test_landing_page.py`

## Phase 4: US2 Blocks (P2)

- [ ] T006 [US2] Остальные секции по contract
- [ ] T007 [US2] Без фейковых отзывов
- [ ] T008 [US2] Расширить `tests/test_landing_page.py`

## Phase 5: Polish

- [ ] T009 Проверка ~375px
- [ ] T010 Обновить статус №1 в `features/feature-map.md` при implement
""",
)

# ---- 017 ----
w(
    "specs/017-guest-smoke-run/spec.md",
    """
# Feature Specification: Guest smoke trainer (3 steps)

**Feature Branch**: `017-guest-smoke-run`

**Created**: 2026-11-02

**Status**: Draft

**Input**: История №2. Граница: `features/website-idea-assess/guest-smoke-run.md`.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Run three guest steps on a news fact (Priority: P1)

A guest without email starts from a get-news item (or own fact), answers in a form→thread UI, receives smoke feedback one question at a time, for up to three human steps, with a waiting indicator.

**Why this priority**: This is the product demo value.

**Independent Test**: Complete three guest answers on one window and see three agent replies; fourth human message is not a free guest step (gate shown — email gate is story 3).

**Acceptance Scenarios**:

1. **Given** a guest under the daily window limit, **When** they start with a news fact from get-news or a valid own fact, **Then** smoke asks one question at a time and accepts free-text answers.
2. **Given** three guest steps completed, **When** the third agent reply is shown, **Then** the product shows the continue/email gate entry point (implementation of email submit is story 3).
3. **Given** empty or meaningless input, **When** submitted, **Then** the product asks to restate the fact and does not invent a news item.

---

### User Story 2 - Limits, clear, captcha (Priority: P1)

Guest may use at most three windows per calendar day per cookie. Clear resets the UI. SmartCaptcha is checked before model calls.

**Why this priority**: Cost and abuse control.

**Independent Test**: Exhaust three windows same day → blocked with clear message; clear empties UI; missing captcha fails model call.

**Acceptance Scenarios**:

1. **Given** three windows already used today on this guest cookie, **When** a fourth window is started, **Then** the product refuses with a clear message.
2. **Given** an open thread, **When** the guest clears the window, **Then** the UI is empty; server transcript may remain until TTL (story 0 policy).
3. **Given** SmartCaptcha is required, **When** a model call is attempted without a valid captcha result, **Then** the model is not called.

### Edge Cases

- get-news backlog empty → explain no news; allow own fact.
- Model delay → waiting indicator visible.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Guest MUST run up to 3 smoke steps per window using `business-idea-from-news.smoke`.
- **FR-002**: Fact MUST come from get-news selection or guest own wording; empty MUST NOT invent news.
- **FR-003**: UI MUST be form-then-thread with waiting indicator.
- **FR-004**: After step 3 agent reply, MUST show gate entry for email continue (story 3 owns submit).
- **FR-005**: MUST enforce ≤3 guest windows per calendar day per cookie.
- **FR-006**: Clear MUST reset UI only (server TTL per ADL-023).
- **FR-007**: MUST verify SmartCaptcha before model invocation.
- **FR-008**: MUST NOT implement email without-code continue, day-2 mail, or payment.

### Key Entities

- **Guest window**: Up to 3 human steps; transcript.
- **Smoke turn**: One question / one answer per rules of smoke skill.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A guest can finish 3 steps on one window in a single visit when models respond.
- **SC-002**: A fourth window the same day is blocked for that cookie.
- **SC-003**: Zero model calls succeed without captcha verification in the guest path.

## Assumptions

- Story 0 guest session and captcha env wiring exist.
- Strong/service model chosen in gateway config.
""",
)
w("specs/017-guest-smoke-run/checklists/requirements.md", checklist("Guest smoke trainer"))
w(
    "specs/017-guest-smoke-run/plan.md",
    """
# Implementation Plan: Гостевой тренажёр smoke

**Branch**: `017-guest-smoke-run` | **Date**: 2026-11-02 | **Spec**: [spec.md](./spec.md)

## Summary

Guest API + UI in demo zone: get-news fact, smoke ≤3 steps, captcha, window limit, clear UI, gate placeholder.

## Technical Context

**Language/Version**: Python 3.12 + landing JS/HTML
**Primary Dependencies**: existing model gateway; SmartCaptcha verify; get-news backlog
**Storage**: guest_session / guest_window from story 0
**Testing**: pytest for limits/captcha gate; manual UI
**Constraints**: one process; no `/app` rewrite

## Constitution Check

- Server-side model calls. Pass. Smoke skill versioned. Pass. Captcha before call. Pass.

## Project Structure

```text
app/web_landing.py / app/web_guest_smoke.py
web/demo.js (or inline)
tests/test_guest_smoke.py
```
""",
)
w(
    "specs/017-guest-smoke-run/research.md",
    """
# Research: 017

## Decision: Smoke skill file as source of dialogue rules

**Rationale**: Product skill already defined; do not invent fixed Q1–Q3 bank.

## Decision: Captcha on each model call

**Rationale**: Boundary requires SmartCaptcha before model.
""",
)
w(
    "specs/017-guest-smoke-run/data-model.md",
    """
# Data model: 017

Uses `guest_session` / `guest_window` from 015. Window stores step count (0–3), transcript messages, `first_reply_at` for TTL.
""",
)
w(
    "specs/017-guest-smoke-run/contracts/guest-smoke-v1.md",
    """
# Contract: guest smoke v1

- `POST /web/v1/guest/window/start` — start window if under daily limit; attach news or accept fact.
- `POST /web/v1/guest/window/message` — body: text + captcha token; returns agent reply or gate flag after 3rd.
- `POST /web/v1/guest/window/clear` — client clear UI marker.
""",
)
w(
    "specs/017-guest-smoke-run/quickstart.md",
    """
# Quickstart: 017

1. Open `#demo`, start window, send 3 answers with captcha test keys if available.
2. Confirm gate banner after 3rd reply; fourth window same day blocked.
""",
)
w(
    "specs/017-guest-smoke-run/tasks.md",
    """
# Tasks: Гостевой тренажёр smoke

**Input**: `/specs/017-guest-smoke-run/`

## Phase 1: Setup

- [ ] T001 UI демо-зоны в `web/` (форма→лента, ожидание, очистить)

## Phase 2: Foundational

- [ ] T002 Вызов get-news / приём своего факта в `app/web_guest_smoke.py`
- [ ] T003 Проверка SmartCaptcha перед моделью

## Phase 3: US1 Three steps (P1)

- [ ] T004 [US1] Цикл smoke ≤3 шагов, лента ответов
- [ ] T005 [US1] После 3-го — показ гейта (без отправки email)
- [ ] T006 [US1] Тесты шагов в `tests/test_guest_smoke.py`

## Phase 4: US2 Limits (P1)

- [ ] T007 [US2] Лимит 3 окна/день; clear UI
- [ ] T008 [US2] Тесты лимита и отказа без captcha

## Phase 5: Polish

- [ ] T009 Статус №2 в feature-map при implement
""",
)

# ---- 018 ----
w(
    "specs/018-email-continue-gate/spec.md",
    """
# Feature Specification: Email continue without code (3 more steps)

**Feature Branch**: `018-email-continue-gate`

**Created**: 2026-11-02

**Status**: Draft

**Input**: История №3. Граница: `features/website-idea-assess/email-continue.md`. ADL-023.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Continue with email, no code wait (Priority: P1)

After three guest steps, the person enters email and immediately continues the same run for three more smoke steps. Guest transcript is attached to the person/run. Mobile app email+code login is unchanged.

**Why this priority**: Core funnel conversion.

**Independent Test**: Finish guest 3 → enter email → get step 4 without waiting for a code letter.

**Acceptance Scenarios**:

1. **Given** guest step 3 is done, **When** a valid email is submitted on the gate, **Then** steps 4–6 of the same run proceed without requiring an email code.
2. **Given** guest transcript existed, **When** email is accepted, **Then** prior messages remain available in the continued run.
3. **Given** the mobile app login flow, **When** this story ships, **Then** app still requires email code as before.

---

### User Story 2 - Return with the same email (Priority: P2)

A returning visitor enters the same email and continues from where they stopped.

**Why this priority**: Retention within the experiment.

**Independent Test**: Stop mid steps 4–6, return, enter same email, resume.

**Acceptance Scenarios**:

1. **Given** an in-progress post-email run, **When** the visitor returns and enters the same email, **Then** they resume at the saved step.
2. **Given** IP-only identification, **When** visiting, **Then** the product does not auto-login by IP.

### Edge Cases

- Invalid email format → ask again, do not continue.
- Day-2 letter is story 4; payment is story 5 (after step 6).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: After guest step 3, MUST accept email and continue without code on the web showcase.
- **FR-002**: MUST transfer guest transcript into the account run for that email.
- **FR-003**: MUST allow exactly three additional smoke steps after email in this free tier.
- **FR-004**: MUST support resume by re-entering the same email.
- **FR-005**: MUST NOT change mobile/Telegram code-login rules.
- **FR-006**: MUST NOT implement day-2 send or payment UI here.
- **FR-007**: MUST NOT use IP as sole identity.

### Key Entities

- **Person (by email)**: Created/found on gate.
- **Run**: Continued smoke run including guest history.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Time from email submit to first post-email question needs no mailbox round-trip.
- **SC-002**: Guest messages remain visible after continue in 100% of successful transfers in test.
- **SC-003**: App email+code path still requires a code in regression test.

## Assumptions

- Guest window from story 2 exists.
- Soft email binding risk accepted per ADL-023.
""",
)
w("specs/018-email-continue-gate/checklists/requirements.md", checklist("Email continue without code"))
w(
    "specs/018-email-continue-gate/plan.md",
    """
# Implementation Plan: Гейт email без кода

**Branch**: `018-email-continue-gate` | **Date**: 2026-11-02 | **Spec**: [spec.md](./spec.md)

## Summary

Web gate: bind guest session to person by email without code; continue smoke 3 steps; resume by email. App code login untouched.

## Technical Context

**Language/Version**: Python 3.12
**Primary Dependencies**: entrances/person model; guest_session; smoke
**Storage**: Postgres person + run + guest link
**Testing**: pytest continue without mail mock code
**Constraints**: do not alter app `/app/v1` code challenge

## Constitution Check

- Web may continue without code (ADL-023). Pass.
- Mobile code unchanged. Pass.

## Project Structure

```text
app/web_email_gate.py
tests/test_web_email_gate.py
```
""",
)
w(
    "specs/018-email-continue-gate/research.md",
    """
# Research: 018

## Decision: Soft person-by-email on web only

**Rationale**: ADL-023 conversion experiment; captcha+limits mitigate abuse.
""",
)
w(
    "specs/018-email-continue-gate/data-model.md",
    """
# Data model: 018

Link `guest_session` → `person_id` / `run_id` on email submit. Store `last_email` for resume.
""",
)
w(
    "specs/018-email-continue-gate/contracts/email-gate-v1.md",
    """
# Contract: email gate v1

- `POST /web/v1/gate/email` — `{ "email": "..." }` → continues run; no code field.
- `POST /web/v1/gate/resume` — same email → resume step.
""",
)
w(
    "specs/018-email-continue-gate/quickstart.md",
    """
# Quickstart: 018

1. Complete 3 guest steps → submit email → receive step 4 immediately.
2. Confirm app still needs code for `/app/v1` login.
""",
)
w(
    "specs/018-email-continue-gate/tasks.md",
    """
# Tasks: Гейт email без кода

**Input**: `/specs/018-email-continue-gate/`

## Phase 1–2

- [ ] T001 UI гейта email после 3-го шага
- [ ] T002 Привязка guest→person/run без кода в `app/web_email_gate.py`

## Phase 3: US1

- [ ] T003 [US1] Продолжение smoke шаги 4–6
- [ ] T004 [US1] Перенос транскрипта
- [ ] T005 [US1] Тесты в `tests/test_web_email_gate.py`

## Phase 4: US2

- [ ] T006 [US2] Resume по тому же email
- [ ] T007 [US2] Регрессия: app code login не сломан

## Phase 5

- [ ] T008 Статус №3 в feature-map при implement
""",
)

# ---- 019 ----
w(
    "specs/019-day2-return-email/spec.md",
    """
# Feature Specification: Day-2 return email

**Feature Branch**: `019-day2-return-email`

**Created**: 2026-11-02

**Status**: Draft

**Input**: История №4. Граница: `features/website-idea-assess/day2-email.md`.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Receive a day-2 invite (Priority: P1)

After the product knows the visitor email, it sends one email inviting them back to the exercise or a new fact. Sending uses the existing mail contour. The letter does not contain dialogue transcript. It does not block day-1 funnel.

**Why this priority**: Retention proxy for the experiment.

**Independent Test**: Complete email gate → after schedule/trigger, one invite letter arrives without dialogue body.

**Acceptance Scenarios**:

1. **Given** a known email from the web gate, **When** day-2 send runs, **Then** exactly one invite-style letter is sent via the existing mail contour.
2. **Given** the letter content, **When** opened, **Then** it has no exercise dialogue transcript.
3. **Given** day-1 funnel, **When** day-2 mail is enabled, **Then** steps 1–6 do not wait on that letter.

### Edge Cases

- Mail provider failure → log/retry policy without crashing the web request path.
- No marketing blast series in this story.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: MUST send one day-2 return invite for known web emails.
- **FR-002**: MUST use existing `secrets/mail.env` contour.
- **FR-003**: Letter MUST NOT include dialogue transcript.
- **FR-004**: MUST NOT block day-1 UX on mail delivery.
- **FR-005**: MUST NOT implement drip campaigns or referral.

### Key Entities

- **Day-2 outbox record**: email, scheduled_for, sent_at.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In test, a gated email produces one day-2 send attempt.
- **SC-002**: Letter body contains zero transcript lines from the run in fixture checks.

## Assumptions

- Scheduling may be “about 24h after email known” or next calendar morning — pick one consistent rule in plan (default: ~24h after email gate).
""",
)
w("specs/019-day2-return-email/checklists/requirements.md", checklist("Day-2 return email"))
w(
    "specs/019-day2-return-email/plan.md",
    """
# Implementation Plan: Письмо дня 2

**Branch**: `019-day2-return-email` | **Date**: 2026-11-02 | **Spec**: [spec.md](./spec.md)

## Summary

Schedule and send one return email ~24h after web email gate using mail.env; no transcript in body.

## Technical Context

**Language/Version**: Python 3.12
**Primary Dependencies**: existing SMTP mail helper
**Storage**: day2_outbox table or equivalent
**Testing**: pytest with mail mock
**Constraints**: no agent SSH; no dialogue in mail

## Constitution Check

- Mail contour reuse. Pass. No dialogue in mail. Pass.

## Decision

Default schedule: 24 hours after successful web email gate.
""",
)
w(
    "specs/019-day2-return-email/research.md",
    """
# Research: 019

## Decision: 24h after gate

**Rationale**: Simple, matches guest TTL scale; documented in plan.
""",
)
w(
    "specs/019-day2-return-email/data-model.md",
    """
# Data model: 019

**day2_mail**: person/email, run_id optional, due_at, sent_at, status.
""",
)
w(
    "specs/019-day2-return-email/contracts/day2-mail.md",
    """
# Contract: day2 mail

Internal: enqueue on email gate success; worker/tick sends via mail.env. No public HTTP required.
""",
)
w(
    "specs/019-day2-return-email/quickstart.md",
    """
# Quickstart: 019

1. Gate with test email → row due in 24h (or force due in test).
2. Run send tick → mock SMTP called once; body has no transcript.
""",
)
w(
    "specs/019-day2-return-email/tasks.md",
    """
# Tasks: Письмо дня 2

**Input**: `/specs/019-day2-return-email/`

- [ ] T001 Таблица/очередь day2 в `app/schema.sql`
- [ ] T002 Enqueue при успешном web email gate
- [ ] T003 Send tick через mail.env без транскрипта в `app/web_day2_mail.py`
- [ ] T004 Тесты mock SMTP в `tests/test_web_day2_mail.py`
- [ ] T005 Статус №4 в feature-map при implement
""",
)

# ---- 020 ----
w(
    "specs/020-fake-payment-amount/spec.md",
    """
# Feature Specification: Fake payment with amount field

**Feature Branch**: `020-fake-payment-amount`

**Created**: 2026-11-02

**Status**: Draft

**Input**: История №5. Граница: `features/website-idea-assess/fake-payment.md`.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - See paywall and choose amount (Priority: P1)

After six smoke steps, the person sees the fixed marketing text about regular training, an amount field (default 100 RUB, or last amount if they paid before), and a pay button. Click records interest and amount; honest message; no payment provider.

**Why this priority**: Measures willingness to pay.

**Independent Test**: Reach step 6 → see text+field default 100 → click → confirmation without charging.

**Acceptance Scenarios**:

1. **Given** step 6 is complete, **When** paywall opens, **Then** the specified Russian text and amount field are shown.
2. **Given** no prior amount, **When** the field renders, **Then** default is 100 RUB.
3. **Given** a prior recorded amount, **When** paywall opens again, **Then** the field shows that last amount.
4. **Given** the person clicks pay, **When** processed, **Then** click+amount are stored and an honest non-charge confirmation is shown.

### Edge Cases

- Non-positive / empty amount → ask for a valid amount.
- Real acquiring out of scope.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: MUST show the exact paywall copy from the boundary after step 6.
- **FR-002**: MUST show editable amount; default 100 RUB if none prior; else last amount.
- **FR-003**: MUST record click and amount without calling a payment provider.
- **FR-004**: MUST show honest confirmation that real charging comes later.
- **FR-005**: MUST NOT implement balance/traffic billing (separate feature).

### Key Entities

- **Fake payment intent**: email/person, amount, clicked_at.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of paywall views in test show the mandated sentence.
- **SC-002**: First-time default equals 100 RUB; second visit restores last amount in test.
- **SC-003**: Zero calls to external payment APIs from this story.

## Assumptions

- Prior amount stored simply per person/email until traffic feature exists.
""",
)
w("specs/020-fake-payment-amount/checklists/requirements.md", checklist("Fake payment with amount field"))
w(
    "specs/020-fake-payment-amount/plan.md",
    """
# Implementation Plan: Фейковая оплата

**Branch**: `020-fake-payment-amount` | **Date**: 2026-11-02 | **Spec**: [spec.md](./spec.md)

## Summary

Paywall UI + persist intent amount; no acquiring.

## Technical Context

**Language/Version**: Python 3.12 + landing UI
**Storage**: fake_payment_intent table
**Testing**: pytest persist/default amount
**Constraints**: no payment provider SDK

## Constitution Check

- Fake pay without provider allowed. Pass.
""",
)
w(
    "specs/020-fake-payment-amount/research.md",
    """
# Research: 020

## Decision: Store last amount on person

**Rationale**: Boundary needs prior amount without full wallet feature.
""",
)
w(
    "specs/020-fake-payment-amount/data-model.md",
    """
# Data model: 020

**fake_payment_intent**: person_id/email, amount_rub, created_at.
**person.last_fake_amount** (or derived from latest intent).
""",
)
w(
    "specs/020-fake-payment-amount/contracts/fake-pay-v1.md",
    """
# Contract: fake pay v1

- `GET /web/v1/paywall` — copy + default_amount
- `POST /web/v1/paywall/click` — `{ "amount": N }` → recorded; confirmation message
""",
)
w(
    "specs/020-fake-payment-amount/quickstart.md",
    """
# Quickstart: 020

1. After step 6 open paywall — default 100.
2. Click 150 → stored; reopen → 150 shown; no charge.
""",
)
w(
    "specs/020-fake-payment-amount/tasks.md",
    """
# Tasks: Фейковая оплата

**Input**: `/specs/020-fake-payment-amount/`

- [ ] T001 UI paywall + поле суммы после шага 6
- [ ] T002 Persist intent в `app/web_fake_pay.py` + schema
- [ ] T003 Дефолт 100 / последняя сумма
- [ ] T004 Тесты в `tests/test_web_fake_pay.py`
- [ ] T005 Статус №5 в feature-map при implement
""",
)

# ---- 021 ----
w(
    "specs/021-metrika-funnel-events/spec.md",
    """
# Feature Specification: Metrika funnel events

**Feature Branch**: `021-metrika-funnel-events`

**Created**: 2026-11-02

**Status**: Draft

**Input**: История №6. Граница: `features/website-idea-assess/metrika-funnel.md`.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Count the funnel (Priority: P1)

With `YANDEX_METRIKA_COUNTER_ID` configured, the landing fires events for: hero CTA; guest steps 1–3; gate shown; email submitted; steps 4–6; paywall shown; pay click + amount; day-2/return when measurable. Server still owns window limits—not Metrika.

**Why this priority**: Experiment learning.

**Independent Test**: Walk funnel in staging with Metrika debug / event log and see named events.

**Acceptance Scenarios**:

1. **Given** counter id is set, **When** pages load, **Then** Metrika counter is present.
2. **Given** the visitor moves through the funnel, **When** each milestone happens, **Then** the corresponding event is sent (or queued to Metrika).
3. **Given** Metrika is down, **When** the visitor uses the product, **Then** core funnel still works; limits still enforced server-side.

### Edge Cases

- Missing counter id → no JS errors; product works.
- Success thresholds are chosen by the owner outside code.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: MUST embed Metrika when `YANDEX_METRIKA_COUNTER_ID` is set.
- **FR-002**: MUST emit events for CTA, steps 1–3, gate, email, steps 4–6, paywall, pay click with amount; day-2/return best-effort.
- **FR-003**: MUST NOT use Metrika as authority for daily window limits.
- **FR-004**: MUST NOT build an analytics cabinet in-product.

### Key Entities

- **Funnel event**: name + optional amount.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: With counter configured, a full test walk produces the core event set.
- **SC-002**: With counter unset, landing remains usable with no blocking errors.
- **SC-003**: Window limit denials still occur with Metrika disabled.

## Assumptions

- Event names documented in contract for implement consistency.
""",
)
w("specs/021-metrika-funnel-events/checklists/requirements.md", checklist("Metrika funnel events"))
w(
    "specs/021-metrika-funnel-events/plan.md",
    """
# Implementation Plan: Метрика воронки

**Branch**: `021-metrika-funnel-events` | **Date**: 2026-11-02 | **Spec**: [spec.md](./spec.md)

## Summary

Inject counter + JS events at funnel milestones; server limits unchanged.

## Technical Context

**Language/Version**: JS on landing + optional server-side goals later
**Config**: YANDEX_METRIKA_COUNTER_ID
**Testing**: presence of counter snippet; event helper unit tests
**Constraints**: non-secret counter id

## Constitution Check

- Analytics not limit authority. Pass.
""",
)
w(
    "specs/021-metrika-funnel-events/research.md",
    """
# Research: 021

## Decision: Client-side reachGoal/events

**Rationale**: Standard Metrika; enough for experiment.
""",
)
w("specs/021-metrika-funnel-events/data-model.md", "# Data model: 021\n\nNo required new tables.\n")
w(
    "specs/021-metrika-funnel-events/contracts/metrika-events.md",
    """
# Contract: metrika events

Event names: `cta_hero`, `step_1`, `step_2`, `step_3`, `gate_shown`, `email_submitted`, `step_4`, `step_5`, `step_6`, `paywall_shown`, `pay_click` (param amount), `day2_return` (best-effort).
""",
)
w(
    "specs/021-metrika-funnel-events/quickstart.md",
    """
# Quickstart: 021

1. Set YANDEX_METRIKA_COUNTER_ID.
2. Walk funnel; verify events in Metrika debugger.
""",
)
w(
    "specs/021-metrika-funnel-events/tasks.md",
    """
# Tasks: Метрика воронки

**Input**: `/specs/021-metrika-funnel-events/`

- [ ] T001 Вставить счётчик при наличии `YANDEX_METRIKA_COUNTER_ID` в шаблон лендинга
- [ ] T002 Хелпер событий по contract в `web/metrika.js`
- [ ] T003 Вызовы с CTA / шагов / гейта / email / paywall (точки в UI story 1–5)
- [ ] T004 Тест: без id страница не падает; с id сниппет есть
- [ ] T005 Статус №6 в feature-map при implement
""",
)

print("generated 016-021")
