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
