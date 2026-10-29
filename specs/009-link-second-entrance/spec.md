# Feature Specification: Add the second entrance from settings and merge runs

**Feature Branch**: `009-link-second-entrance`

**Created**: 2026-10-29

**Status**: Draft

**Input**: User description: "Мобильное приложение" — only the ready story «В настройках указать второй вход, подтвердить его кодом и слить ходы». Boundary: `features/mobile-app/link-second-entrance.md`.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Offer the second entrance in both channels (Priority: P1)

A person can type an email, a Telegram identity, or both in account settings. The same action exists in the bot and in the app.

**Why this priority**: The merge rule already exists. Nobody can use it until settings ask for the missing entrance.

**Independent Test**: Open settings in the bot and in the app and see the action to add an email and the action to add a Telegram identity, without a model change or a self-information edit starting by itself.

**Acceptance Scenarios**:

1. **Given** a person opens account settings in the bot, **When** the menu is shown, **Then** they can start adding an email and they can start adding a Telegram identity.
2. **Given** a person opens the same action in the app, **When** the screen is shown, **Then** the same two additions are offered and the rules are the same as in the bot.

---

### User Story 2 - Confirm each added entrance with its own code (Priority: P1)

The email is confirmed by a code in the letter. The Telegram identity is confirmed by a code in the bot. One confirmed value out of two does not merge runs.

**Why this priority**: A single typed value must not mix two people.

**Independent Test**: Record both values, confirm only one code, and see the runs stay apart. Confirm the second code and see both sets of runs on one person.

**Acceptance Scenarios**:

1. **Given** both an email and a Telegram identity were entered, **When** only one code is confirmed, **Then** the runs stay separate.
2. **Given** only one of the two codes is confirmed, **When** the other code is wrong or replaced, **Then** the runs still stay separate.
3. **Given** both codes are the latest codes for those links, **When** the second one is confirmed, **Then** the runs of both entrances belong to one person and both sets remain.
4. **Given** the marks of one skill differ, **When** the merge completes, **Then** that mark is «неравномерно».
5. **Given** the marks of one skill match, **When** the merge completes, **Then** that mark stays.
6. **Given** the merge completes, **When** the visible profile texts are read, **Then** they are still two texts.

### Edge Cases

- A letter or a bot code that cannot be delivered does not confirm the entrance and does not merge runs.
- Signing in is not this screen. This screen does not start a news review and does not change the model.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Account settings in the bot and in the app MUST let a person enter an email, a Telegram identity, or both.
- **FR-002**: An added email MUST be confirmed by a code sent to that mailbox. An added Telegram identity MUST be confirmed by a code in the bot.
- **FR-003**: Confirming only one of two entered values MUST NOT merge runs.
- **FR-004**: After both latest codes are confirmed, the runs of both entrances MUST belong to one person and both sets MUST remain.
- **FR-005**: Differing skill marks MUST become «неравномерно». Matching marks MUST stay.
- **FR-006**: The two visible profile texts MUST NOT be rewritten into one text.
- **FR-007**: This story MUST NOT change model choice, self-information editing, news review, or email sign-in.

### Key Entities

- **Entrance**: The email or Telegram identity being added.
- **Link code**: The latest code for that entrance.
- **Run**: Moves to the person who confirmed both codes. Its text does not change.
- **Skill mark** and **visible profile text**: Compared and kept as the account rule already states.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Both the bot settings and the app settings offer adding an email and adding a Telegram identity.
- **SC-002**: After one code of two, zero runs have moved.
- **SC-003**: After both codes, every run from both entrances is present once.
- **SC-004**: Every differing skill shows «неравномерно», and every shared mark is unchanged.
- **SC-005**: Both original profile texts are still present after the merge.

## Assumptions

- The account rules are already specified in `specs/007-email-account-entry/` and are called, not rewritten.
- The app entry screen that only shows the run list stays as specified in `specs/008-app-email-entry/`. This story adds a separate settings action.
- Model choice and self-information remain the existing bot behavior and the later app settings story.
- Phone entrance stays parked.
