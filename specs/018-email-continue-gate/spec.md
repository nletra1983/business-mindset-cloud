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
