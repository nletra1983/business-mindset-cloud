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
