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
