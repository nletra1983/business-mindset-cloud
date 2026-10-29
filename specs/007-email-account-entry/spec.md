# Feature Specification: Email entrance without required Telegram

**Feature Branch**: `007-email-account-entry`

**Created**: 2026-10-29

**Status**: Draft

**Input**: User description: "Мобильное приложение" — only the ready story «Внедрить вход по email и необязательный Telegram в уже работающий аккаунт». Boundary: `features/mobile-app/arch-change.md`.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Start with an email and no Telegram (Priority: P1)

A person can begin with an email address, receive a code in that mailbox, and be inside the product without ever opening Telegram.

**Why this priority**: Today a person can appear only from Telegram. The mobile channel cannot exist until an email alone is enough.

**Independent Test**: Submit an email and the matching code, and reach the product without a Telegram chat. A wrong or replaced code does not admit them and does not create a second person.

**Acceptance Scenarios**:

1. **Given** a person has no product record, **When** they submit an email and the matching code from that mailbox, **Then** they are inside the product and are not asked to open Telegram.
2. **Given** a person submits an email, **When** the letter arrives, **Then** it contains the entrance code and does not contain the exercise dialogue, the profile, or the model choice.
3. **Given** a person submits a code that is not the code last issued for that email, **When** they try to enter, **Then** they are not admitted and no second person record is created.
4. **Given** an email is already confirmed on a person, **When** someone enters with the latest code for that email, **Then** they arrive in that same person and no second person is created and no runs are merged.

---

### User Story 2 - Keep using Telegram without an email (Priority: P1)

A person who already uses the bot continues without being asked for an email. Their existing runs stay where they are.

**Why this priority**: The current bot is the working product. This story must not make Telegram depend on an email.

**Independent Test**: Continue an unfinished run for a Telegram-only person and confirm no email is requested and the run is unchanged.

**Acceptance Scenarios**:

1. **Given** a person uses only Telegram, **When** they continue an unfinished run, **Then** the run continues and the product does not ask for an email.
2. **Given** a person uses only Telegram, **When** they keep using the bot, **Then** their runs stay on that entrance.

---

### User Story 3 - Merge only after both entrances are confirmed (Priority: P2)

The account can hold an email and a Telegram identity as two optional links. They become one person only after both are confirmed. The screens that collect those values are a later story. This story is the rule those screens call.

**Why this priority**: Silent linking would mix two people. The later settings story cannot merge correctly until this rule exists.

**Independent Test**: Confirm an email entrance and a Telegram entrance with both codes and check that both sets of runs belong to one person. Confirming only one of two values leaves the runs separate.

**Acceptance Scenarios**:

1. **Given** a person has only an email, **When** a Telegram identity is recorded but its code has not been confirmed, **Then** the entrances stay separate and runs are not combined.
2. **Given** a person has only Telegram, **When** an email is recorded but its code has not been confirmed, **Then** the entrances stay separate and runs are not combined.
3. **Given** both an email and a Telegram identity are recorded, **When** each is confirmed by its own latest code, **Then** the runs of both entrances belong to one person and both sets remain.
4. **Given** two entrances are merged, **When** the same skill has different marks, including «не наблюдалось» against any other mark, **Then** that skill's mark becomes «неравномерно».
5. **Given** two entrances are merged, **When** the same skill has the same mark, **Then** that mark stays as it was.
6. **Given** two entrances are merged, **When** the visible profile texts are read, **Then** the two texts are not rewritten into one combined text.
7. **Given** a code is wrong or has been replaced, **When** someone tries to finish a merge with it, **Then** the runs do not move.

### Edge Cases

- A wrong or replaced code does not admit the person and does not merge entrances.
- Confirming only one of the two values, even if both were recorded, does not merge.
- Signing in with an email that already belongs to a person does not take that person's runs onto someone else.
- The letter is only an entrance code. It is not a copy of the exercise, the profile, or the model choice.
- The bot's existing model choice, self-information file, and hidden profile stay on the Telegram entrance until a merge.
- If the letter cannot be sent, the person is told the code was not sent, and no confirmed person is created.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The product MUST admit a person by an email address and a code sent to that mailbox without requiring Telegram.
- **FR-002**: The letter MUST carry the entrance code and MUST NOT carry the exercise dialogue, the profile, or the model choice.
- **FR-003**: A person who uses only Telegram MUST be able to continue the existing bot without an email, and their existing runs MUST stay unchanged.
- **FR-004**: Email and Telegram MUST be optional links to one internal person. Neither link MUST be required for the other to work.
- **FR-005**: The product MUST NOT merge two entrances at sign-in.
- **FR-006**: A newly added email MUST be confirmed by a code sent to that mailbox. A newly added Telegram identity MUST be confirmed by a code in the bot.
- **FR-007**: Until both links are confirmed, each entrance MUST keep its own runs, model choice, and profile.
- **FR-008**: After both links are confirmed, the runs of both entrances MUST belong to one person and both sets MUST remain.
- **FR-009**: After a merge, a skill whose marks differ MUST be marked «неравномерно». A skill whose marks are the same MUST keep that mark.
- **FR-010**: A merge MUST NOT rewrite the two visible profile texts into one text.
- **FR-011**: A code that is not the latest code issued for that link MUST NOT admit the person and MUST NOT complete a merge.
- **FR-012**: Signing in with an email that is already confirmed MUST open that existing person and MUST NOT create a second person.
- **FR-013**: If the code letter cannot be sent, the product MUST NOT leave a confirmed person for that attempt.

### Key Entities

- **Person**: The internal identity. Email and Telegram are links on the person, not the identity itself.
- **Entrance**: A confirmed email or a confirmed Telegram identity. Before a merge, an entrance has its own runs, model choice, and profile.
- **Link code**: The latest code issued for one email or one Telegram identity. A newer code replaces the previous one.
- **Run**: An exercise record that stays intact and moves with its entrance into the merged person.
- **Skill mark**: One of «не наблюдалось», «слабо», «проявляется», «устойчиво», «неравномерно» on one skill.
- **Visible profile text**: The person's own words. A merge keeps both original texts.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A new person can finish email entry and reach the product without opening Telegram.
- **SC-002**: A Telegram-only person can continue an unfinished run, and the product asks for an email in zero of those continuations.
- **SC-003**: Before both links are confirmed, a person sees only the runs of the entrance they are using.
- **SC-004**: After both links are confirmed, every run from both entrances is present once on the single person.
- **SC-005**: After a merge, every skill with two different marks shows «неравномерно», and every skill with one shared mark shows that same mark.
- **SC-006**: After a merge, both original visible profile texts are still present and neither has been replaced by a combined text.
- **SC-007**: The letter for an entrance contains no sentence from the exercise dialogue.
- **SC-008**: An email that is already confirmed never produces a second person when its latest code is entered.

## Assumptions

- This specification is only the account change in the product that already runs. The Android application, the run list after login, the settings screens that collect the second entrance, continuing a news review, and the application settings for model and self-information are later stories and are not specified here.
- Teaching the skill to merge profile text is a backlog story and is not specified here.
- Phone-number entrance stays parked and is not specified here.
- Past-review, redo, and delete stories of the news feature stay parked.
- Which mailbox service sends the letter is not a product choice. The letter is sent from the product's server.
- The latest issued code is the only valid code for that link.
- The first audience remains the author. Store publication is out of scope.
- iOS is a later client of the same entrance rules and is not specified here.
