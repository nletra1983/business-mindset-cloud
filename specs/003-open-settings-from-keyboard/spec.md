# Feature Specification: Open Settings from Dialogue Keyboard

**Feature Branch**: `cursor/003-open-account-settings-8e5d`

**Created**: 2026-10-28

**Status**: Draft

**Input**: User description: "Speckit Specify for the first `ready-for-speckit` story in Account Settings: open settings from dialogue keyboard."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Open account settings from current dialogue context (Priority: P1)

As a person in the Telegram training dialogue, I can open account settings from the same keyboard where model access used to be, so I do not leave the current training context to reach settings.

**Why this priority**: This is the entry point for all remaining account-settings stories. Without it, later settings scenarios cannot be reached from the dialogue.

**Independent Test**: In each supported context, tap `настройки` and verify that the settings menu opens with the expected two options.

**Acceptance Scenarios**:

1. **Given** a person is in an unfinished dialogue run with a keyboard, **When** they tap `настройки`, **Then** the settings menu opens.
2. **Given** a person is on the runs list view with a keyboard, **When** they tap `настройки`, **Then** the settings menu opens.
3. **Given** a person just received the final dialogue message with a keyboard, **When** they tap `настройки`, **Then** the settings menu opens.

---

### User Story 2 - See clear settings options (Priority: P2)

As a person in settings, I can see the two available settings directions (`выбор модели` and `информация о себе`) so I understand what can be configured in this contour.

**Why this priority**: The feature boundary explicitly defines two settings directions, and users need that clear menu before deeper flows are implemented or expanded.

**Independent Test**: Open settings once and verify both options are visible and selectable.

**Acceptance Scenarios**:

1. **Given** settings are open, **When** the menu is displayed, **Then** it contains both options: `выбор модели` and `информация о себе`.

---

### User Story 3 - Keep current run state unchanged when opening settings (Priority: P3)

As a person in an ongoing dialogue, I can open settings without losing the current run state, so I can return and continue from the same place.

**Why this priority**: Protecting run continuity avoids regressions in the training flow and keeps settings as navigation, not a destructive action.

**Independent Test**: Open settings during an unfinished run, then return to the run and verify the same step and context remain.

**Acceptance Scenarios**:

1. **Given** a person opens settings from an unfinished run, **When** they return to the run, **Then** the run remains at the same dialogue step and context.

### Edge Cases

- User taps `настройки` multiple times quickly: the system still presents one coherent settings menu state for that user context.
- A keyboard message is stale or no longer active: tapping `настройки` does not break the dialogue and returns a recoverable user-facing response.
- Settings are opened while model selection was previously used in that context: replacing the old entry point does not remove access to model selection.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide a `настройки` button in the same keyboard contexts where model access was previously shown: unfinished run, runs list, and post-final message.
- **FR-002**: The system MUST open a settings menu when the person taps `настройки`.
- **FR-003**: The settings menu MUST include exactly two first-level options for this contour: `выбор модели` and `информация о себе`.
- **FR-004**: Choosing `выбор модели` from settings MUST preserve access to the existing model-selection flow and outcomes defined by the already active model-switch scope.
- **FR-005**: Choosing `информация о себе` MUST route the person to the dedicated entry point for the self-information story without exposing the hidden profile file.
- **FR-006**: Opening settings MUST NOT change run step, transcript history, or run completion state by itself.
- **FR-007**: If the `настройки` action arrives from an unsupported or stale interaction context, the system MUST respond with a recoverable user message and MUST NOT corrupt run state.

### Key Entities *(include if feature involves data)*

- **Interaction Context**: The user-visible dialogue state where settings access is allowed (unfinished run, runs list, post-final message).
- **Settings Menu**: The account-settings entry surface containing first-level options available in this slice.
- **Settings Entry Action**: A user action event created by tapping `настройки`, tied to a specific interaction context.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In 100% of supported contexts, users can open settings within one interaction after tapping `настройки`.
- **SC-002**: In acceptance testing, 100% of opened settings menus show both expected first-level options.
- **SC-003**: During regression testing of dialogue flow, opening settings introduces 0 cases where run step or completion state changes without an explicit settings action.
- **SC-004**: Existing model-selection acceptance scenarios remain passable when entered through settings.

## Assumptions

- The existing model-selection behavior is already defined and remains functionally unchanged in this story; this story changes entry point and menu structure.
- Full read/edit behavior for `информация о себе` is specified by a separate ready-for-speckit story and is not expanded here beyond entry-point routing.
- Settings entry is implemented for Telegram contexts already listed in the feature boundary; other channels remain out of scope.
- Product boundaries from `features/account-settings/business-logic.md` and `ProductArtifacts/skill-profile-slice.md` remain authoritative for this specification.
