# Feature Specification: Open the same account settings in the app

**Feature Branch**: `011-app-settings`

**Created**: 2026-10-29

**Status**: Draft

**Input**: User description: "Мобильное приложение" — only the ready story «Открыть настройки того же входа: модель и информация о себе». Boundary: `features/mobile-app/app-settings.md`.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Open settings at the same moments as the bot (Priority: P1)

The person can open account settings during an unfinished run, from the run list, and after the finale.

**Why this priority**: The bot already offers settings at those moments. The app must not invent a different set of moments.

**Independent Test**: Look for settings during an unfinished run, on the list, and after the finale, and find them each time. Look during none of those moments and do not find a new moment invented by this story.

**Acceptance Scenarios**:

1. **Given** an unfinished run, the run list, or a finished finale, **When** the person looks for settings, **Then** settings are available.
2. **Given** settings are open, **When** the person looks at the actions, **Then** they see model choice and self-information, and they do not start the second-entrance merge from this story.

---

### User Story 2 - Choose a model and edit the visible profile (Priority: P1)

Model choice behaves as it already does in the bot. Self-information shows the visible file, asks strengths and weaknesses separately, and can add a fact. The hidden profile is not shown and is not changed by this edit.

**Why this priority**: These are the two settings the person already trusts in the bot.

**Independent Test**: Choose a model and see «Модель изменена.». Read the visible profile, save strengths, then weaknesses, and do not see a hidden skill mark.

**Acceptance Scenarios**:

1. **Given** the person opens model choice, **When** they pick a model, **Then** they see «Модель изменена.» and the current model is that choice.
2. **Given** the chosen model is unavailable, **When** the product reports it, **Then** the existing bot rule applies and this story does not invent a new one.
3. **Given** the person opens self-information, **When** the file is shown, **Then** it is the visible file and no hidden skill mark is shown.
4. **Given** the person edits self-information, **When** they answer, **Then** strengths are asked separately from weaknesses, and they may add a fact.
5. **Given** the person saves visible text, **When** the hidden profile is read, **Then** its marks are unchanged.

### Edge Cases

- Settings do not add the second entrance and do not start a news review.
- Screens may look different from the bot. The order of strengths then weaknesses stays.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Settings MUST be available during an unfinished run, from the run list, and after the finale.
- **FR-002**: Settings MUST offer model choice and self-information.
- **FR-003**: Choosing a model MUST show «Модель изменена.» and MUST make that model current.
- **FR-004**: An unavailable model MUST follow the bot's existing unavailable-model rule.
- **FR-005**: Self-information MUST show only the visible file.
- **FR-006**: Strengths and weaknesses MUST be asked separately, and the person MUST be able to add a fact.
- **FR-007**: Editing the visible file MUST NOT change hidden skill marks and MUST NOT show them.
- **FR-008**: This story MUST NOT collect a second entrance and MUST NOT start a news review.

### Key Entities

- **Visible profile**: The person's own words. Shown and editable.
- **Hidden profile**: The agent's marks. Not shown and not edited here.
- **Model choice**: The person's current model. The same three names as in the bot.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Settings are present in all three moments: unfinished run, list, and after the finale.
- **SC-002**: After a successful choice, the person sees «Модель изменена.» and the current model matches the choice in every such choice.
- **SC-003**: The visible profile screen contains zero hidden skill marks.
- **SC-004**: A visible-file edit changes zero hidden marks.
- **SC-005**: The settings screen offers zero actions that add a second entrance.

## Assumptions

- Model behavior and the visible/hidden split are already specified for the bot and are reused.
- The second entrance remains `specs/009-link-second-entrance/`.
- The news review remains `specs/010-app-news-run/`.
- Screens may differ in appearance. The meaning of the steps does not.
