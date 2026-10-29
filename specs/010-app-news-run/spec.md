# Feature Specification: Start and resume a news review in the app

**Feature Branch**: `010-app-news-run`

**Created**: 2026-10-29

**Status**: Draft

**Input**: User description: "Мобильное приложение" — only the ready story «Начать разбор новости в приложении и вернуться в незаконченный». Boundary: `features/mobile-app/app-news-run.md`.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Start a review from the person's own words (Priority: P1)

From the run list, a person starts a new review by writing the news or the problem in their own words. An empty or content-free formulation does not start a run.

**Why this priority**: Without a start, the list from the previous story stays empty forever.

**Independent Test**: Submit a real formulation and see one new open run. Submit an empty formulation and see no new run.

**Acceptance Scenarios**:

1. **Given** the person is on the run list, **When** they submit a formulation in their own words, **Then** a new review starts and asks one question.
2. **Given** the formulation is empty or has no content, **When** they submit it, **Then** the product asks them to formulate it again and does not invent an event.

---

### User Story 2 - Return to an unfinished review (Priority: P1)

The person returns to an unfinished review from the list. It continues at the same step. Leaving the review returns to the list and leaves the run unfinished. The same incoming answer does not move the step twice.

**Why this priority**: The list is useful only if an open run can be continued.

**Independent Test**: Open an unfinished run, see the same step, leave to the list, and see that run still unfinished.

**Acceptance Scenarios**:

1. **Given** an unfinished run, **When** the person opens it from the list, **Then** it continues at the same step with the same answers.
2. **Given** the person is inside a review, **When** they go back to the list, **Then** the run stays unfinished and no pause status appears.
3. **Given** the same answer is delivered twice, **When** the second delivery arrives, **Then** the step does not move again.
4. **Given** a review is open, **When** the person tries to start another review from inside it, **Then** the new review does not start.

### Edge Cases

- A weak answer does not advance the review.
- The review can reach the finale and the summary of this run.
- The past-review card, repeating a topic, and deleting one review are not offered.
- The app does not call a model provider itself. Account settings are not this story.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: From the run list, the person MUST be able to start a review with their own formulation.
- **FR-002**: An empty or content-free formulation MUST NOT start a run and MUST NOT invent an event.
- **FR-003**: From the list, the person MUST be able to return to an unfinished run at the same step.
- **FR-004**: Leaving to the list MUST keep an unfinished run unfinished and MUST NOT add a pause status.
- **FR-005**: A repeated delivery of the same answer MUST NOT move the step a second time.
- **FR-006**: A new run MUST NOT start from inside the current run.
- **FR-007**: A weak answer MUST NOT advance the review.
- **FR-008**: A finished review MUST be able to reach the summary of that run.
- **FR-009**: This story MUST NOT open a past-review card, repeat a topic as a new record, or delete a review.

### Key Entities

- **Run**: The same exercise record the bot already uses. This story does not create a second kind of run.
- **Formulation**: The person's own words that start a run.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A content-bearing formulation starts exactly one new open run.
- **SC-002**: An empty formulation starts zero runs.
- **SC-003**: Returning to an unfinished run shows the same step in every such return.
- **SC-004**: After leaving to the list, the run is still unfinished in every such exit.
- **SC-005**: A duplicated answer moves the step zero additional times.
- **SC-006**: The past card, topic repeat, and delete actions are offered zero times.

## Assumptions

- The news rules already specified for the bot are reused. They are not rewritten.
- The run list from `specs/008-app-email-entry/` is where start and resume are offered. That earlier screen did not include them; this story adds them.
- Account settings and the second entrance are other stories.
- The app does not call a model provider and has no offline run.
