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
