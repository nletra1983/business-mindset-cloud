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
