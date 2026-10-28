# Feature Specification: Read and Update Self Information

**Feature Branch**: `cursor/003-open-account-settings-8e5d`

**Created**: 2026-10-28

**Status**: Draft

**Input**: User description: "Speckit Specify for story: Прочитать, изменить и добавить информацию о себе."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Read current self information from settings (Priority: P1)

As a person in the Telegram dialogue, I can open `информация о себе` from settings and read what is already stored about me, so I can understand my current profile text.

**Why this priority**: Reading existing self information is the minimum useful capability of the story and the safe entry point before any edits.

**Independent Test**: Open settings, choose `информация о себе`, and verify the user-visible profile text is shown without hidden evaluator fields.

**Acceptance Scenarios**:

1. **Given** a person opens settings, **When** they choose `информация о себе`, **Then** the system shows the current user-visible profile file content.
2. **Given** a person has no recorded self-information entries yet, **When** they open `информация о себе`, **Then** the system shows the default empty representation for that file.

---

### User Story 2 - Update strengths, weaknesses, and add facts (Priority: P2)

As a person, I can update what is written about my strengths and weaknesses and add extra facts about myself, so the visible profile stays accurate.

**Why this priority**: Editing is the core value of this story and must follow the read flow.

**Independent Test**: Open `информация о себе`, provide new values for strengths and weaknesses, add an additional fact, then reopen and verify those values persist in the visible file.

**Acceptance Scenarios**:

1. **Given** a person is in `информация о себе`, **When** they provide new strengths text, **Then** the visible profile file stores and shows the updated strengths text.
2. **Given** a person is in `информация о себе`, **When** they provide new weaknesses text, **Then** the visible profile file stores and shows the updated weaknesses text.
3. **Given** a person is in `информация о себе`, **When** they add another self-reported fact, **Then** the visible profile file includes that fact in the user-said section.

---

### User Story 3 - Keep hidden evaluator profile private and unchanged by direct edits (Priority: P3)

As a person, I can edit only my visible self-information file, while the hidden evaluator profile remains private and is not directly overwritten by this edit flow.

**Why this priority**: Privacy and separation between user-provided text and evaluator status are mandatory product constraints.

**Independent Test**: Edit visible self information and verify hidden profile-only fields are not shown to the user and are not directly replaced by those edits.

**Acceptance Scenarios**:

1. **Given** a person uses `информация о себе`, **When** profile data is shown, **Then** evaluator-only statuses and internal characteristic ids are not displayed.
2. **Given** a person edits visible self-information text, **When** save is completed, **Then** hidden evaluator statuses are not directly rewritten by this flow.

### Edge Cases

- Person sends empty or whitespace-only update text for strengths/weaknesses: the system keeps existing value and returns a clear correction prompt.
- Person sends a long free-text fact: the system stores it safely as user-said content without exposing hidden profile internals.
- Person interrupts profile update and returns later: previously saved values remain readable and editable.
- Callback/message for `информация о себе` arrives from stale context: the system returns a recoverable response and does not corrupt stored profile data.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide access to `информация о себе` from the settings menu.
- **FR-002**: The system MUST show the user-visible self-information file when `информация о себе` is opened.
- **FR-003**: The shown self-information content MUST include only user-visible sections (strengths, weaknesses, and user-said facts) and MUST NOT include hidden evaluator statuses or internal ids.
- **FR-004**: The system MUST allow a person to update strengths and weaknesses as separate inputs in the `информация о себе` flow.
- **FR-005**: The system MUST allow a person to add additional self-reported facts in the same flow.
- **FR-006**: Saved updates from this flow MUST persist and be visible on subsequent reads of `информация о себе`.
- **FR-007**: Direct edits in this flow MUST NOT overwrite hidden evaluator characteristic statuses.
- **FR-008**: Empty or invalid profile-edit inputs MUST produce a recoverable user prompt and MUST NOT erase previously saved valid values.
- **FR-009**: Stale or unsupported profile-edit callbacks/messages MUST produce a recoverable response and MUST NOT modify stored profile data.

### Key Entities *(include if feature involves data)*

- **Visible Self Information File**: User-readable and user-editable profile text containing strengths, weaknesses, and self-reported facts.
- **Hidden Evaluator Profile File**: Internal profile with six characteristics, statuses, and evidence, used by the agent for training guidance and not shown directly to the user.
- **Profile Edit Session**: The interaction state in which strengths, weaknesses, and additional facts are read/updated through Telegram.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In acceptance testing, 100% of `информация о себе` opens from settings and shows a user-visible profile response.
- **SC-002**: In acceptance testing, 100% of valid profile edits (strengths, weaknesses, additional fact) are persisted and visible after reopen.
- **SC-003**: In acceptance testing, 0 hidden evaluator status fields are exposed in user-visible profile responses.
- **SC-004**: In acceptance testing, stale/unsupported profile-edit callbacks modify 0 persisted profile records and always return a recoverable response.

## Assumptions

- Settings entry flow from story `Открыть настройки с клавиатуры разбора` is already available and reused by this story.
- Hidden evaluator profile continues to be updated only by exercise-result logic, not by direct user profile editing.
- This story is limited to Telegram flow in the existing server contour and does not introduce new channels.
- Payment model settings, paid model access, and full mentor-facing profile views remain out of scope for this story.
