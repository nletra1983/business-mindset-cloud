# Feature Specification: Update Hidden Skill Profile from Exercise Results

**Feature Branch**: `cursor/003-open-account-settings-8e5d`

**Created**: 2026-10-28

**Status**: Draft

**Input**: User description: "Speckit Specify for story: Обновлять скрытый файл профиля по результату задания."

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.

  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - Save evidence-based characteristic updates after an exercise (Priority: P1)

As a person completing a training exercise, my hidden skill profile is updated only with characteristics that the exercise actually observed, so future guidance reflects my real answers.

**Why this priority**: This is the core purpose of the story: profile updates must be tied to exercise evidence, not guesses.

**Independent Test**: Finish or pause an exercise with known observed characteristics and verify those characteristics are updated with status and evidence in the hidden profile.

**Acceptance Scenarios**:

1. **Given** an exercise run produces observation results for one or more characteristics, **When** the run is completed or paused, **Then** the hidden profile stores updates only for those observed characteristics.
2. **Given** an exercise run has no observation for a characteristic, **When** the run is completed or paused, **Then** that characteristic is not marked weak by default and is not changed by absence of evidence.

---

### User Story 2 - Merge status across runs using profile rules (Priority: P2)

As a person progressing through multiple runs, profile status changes follow consistent merge rules, so strengths and weaknesses are tracked over time instead of being overwritten by one answer.

**Why this priority**: Without deterministic merge rules, profile history becomes inconsistent and cannot guide next training focus.

**Independent Test**: Run two or more exercise outcomes for the same characteristic and verify status transitions follow first evidence, repeated sign, and contradiction rules.

**Acceptance Scenarios**:

1. **Given** a characteristic is `не наблюдалось`, **When** first evidence arrives with either positive or weak signal, **Then** the characteristic status becomes the provided signal and stores its evidence.
2. **Given** a characteristic already has one signal from a prior completed run, **When** a second completed run repeats the same signal, **Then** the status becomes `устойчиво`.
3. **Given** a characteristic has prior evidence with one signal, **When** a new run provides opposite signal, **Then** both evidences are retained and the status becomes `неравномерно`.

---

### User Story 3 - Keep hidden profile private while selecting current training focus (Priority: P3)

As a person using account settings and training dialogue, I do not see internal characteristic ids or hidden statuses, while the system still updates one current focus characteristic for the next exercise.

**Why this priority**: Privacy and internal coaching quality must both hold: internal profile is needed for guidance but must not leak to user-facing profile flows.

**Independent Test**: Update visible self-information and complete exercise updates; verify hidden status is not exposed in user-facing content and one relevant current focus is selected internally.

**Acceptance Scenarios**:

1. **Given** hidden profile updates are applied, **When** user-facing self-information is shown or edited, **Then** hidden characteristic ids and statuses are not displayed and not directly changed by that edit flow.
2. **Given** hidden profile statuses include weak, uneven, or not-observed characteristics relevant to upcoming training, **When** profile update is finalized, **Then** exactly one current training focus characteristic is selected according to profile rules.

---

[Add more user stories as needed, each with an assigned priority]

### Edge Cases

- Exercise outcome contains only `замечать возможность` evidence from short "event and scale" flow: only this characteristic is updated; the other five remain `не наблюдалось` until separate evidence appears.
- A profile update payload references unknown or unsupported characteristic id: update is rejected safely and existing hidden profile remains unchanged.
- Duplicate delivery of the same completed run arrives again: characteristic history is not duplicated and status does not drift from idempotent replay.
- Visible profile edits happen between two exercise updates: hidden status transitions are still computed only from exercise evidence and not from visible self-description text.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST maintain a hidden skill profile with six characteristics: spotting opportunities, holding multiple response types, distinguishing who pays for measurable loss, acting under incomplete information, using available means, and learning from checks.
- **FR-002**: For each characteristic update, the system MUST store both status and evidence payload that includes quoted or paraphrased user answer, source exercise, and run reference.
- **FR-003**: Hidden profile updates MUST be applied only when an exercise run is completed or paused and provides explicit observation evidence.
- **FR-004**: Characteristics that have no evidence in a run MUST remain unchanged and MUST NOT be marked weak by default.
- **FR-005**: First evidence for a characteristic currently marked `не наблюдалось` MUST set status to the observed signal (`проявляется` or `слабо`) and store the evidence.
- **FR-006**: Repeated same-direction signal for the same characteristic across two completed runs MUST set status to `устойчиво`.
- **FR-007**: Contradictory signals across runs for the same characteristic MUST preserve both evidences and set status to `неравномерно`.
- **FR-008**: A single run MUST NOT set status `устойчиво`.
- **FR-009**: The system MUST keep hidden profile content separate from user-visible self-information content; editing visible self-information MUST NOT directly change hidden characteristic statuses.
- **FR-010**: The system MUST maintain one `сейчас тренировать` focus that references one of the six characteristics and is chosen from weak, uneven, or not-yet-observed candidates relevant to near-term training.
- **FR-011**: If short "event and scale" analysis is used, only the spotting-opportunity characteristic MAY be updated by that flow; all other characteristics MUST stay `не наблюдалось` until explicit evidence is produced.
- **FR-012**: Hidden profile update processing MUST be idempotent for duplicate delivery of the same run result.

### Key Entities *(include if feature involves data)*

- **Hidden Skill Profile**: Internal, non-user-visible profile with six characteristics, their statuses, evidence history, and one current training focus.
- **Characteristic Evidence Record**: One observation record for a characteristic containing user quote/paraphrase, exercise identity, run reference, and resulting signal direction.
- **Exercise Outcome Summary**: Finalized result produced by a training run (completion or pause) that carries only observed characteristics eligible for hidden profile updates.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In acceptance testing, 100% of finalized exercise outcomes with evidence update only the referenced characteristics and leave non-referenced characteristics unchanged.
- **SC-002**: In acceptance testing, 100% of two-run transition scenarios match merge rules (`не наблюдалось`→signal, repeated signal→`устойчиво`, contradiction→`неравномерно`).
- **SC-003**: In acceptance testing, 0 hidden characteristic statuses or ids are exposed through user-visible self-information responses.
- **SC-004**: In acceptance testing, duplicate delivery of the same run outcome produces 0 duplicate evidence records and no unintended status drift.

## Assumptions

- Exercise logic provides finalized observed signals (`проявляется` or `слабо`) with enough evidence context to write profile updates.
- This story is limited to the existing Telegram-first server contour and does not introduce new channels or external profile viewers.
- User-visible profile editing flow from the previous story remains separate and is reused as-is for privacy boundary checks.
- Paid model settings, new provider onboarding, and mentor-facing analytics are out of scope for this story.
