# Feature Specification: Phone entrance without required Telegram

**Feature Branch**: `006-phone-account-entry`

**Created**: 2026-10-28

**Status**: Draft

**Input**: User description: "Мобильное приложение" — only the ready story «Внедрить вход с телефона и необязательный Telegram в уже работающий аккаунт». Boundary: `features/mobile-app/arch-change.md`.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Start with a phone and no Telegram (Priority: P1)

A person can begin with a phone number, receive a code by SMS, and use the product without ever opening Telegram.

**Why this priority**: Today a person can appear only from Telegram. The mobile channel cannot exist until a phone alone is enough.

**Independent Test**: Enter a phone number, submit the SMS code, and complete a product action without a Telegram chat. The unfinished run belongs to that phone entrance.

**Acceptance Scenarios**:

1. **Given** a person has no product record, **When** they submit a phone number and the matching SMS code, **Then** they are inside the product and are not asked to open Telegram.
2. **Given** a person submits a phone number, **When** the SMS arrives, **Then** the message contains the entrance code and does not contain the exercise dialogue.
3. **Given** a person submits a code that is not the code last issued for that phone, **When** they try to enter, **Then** they are not admitted and no second person record is created.

---

### User Story 2 - Keep using Telegram without a phone (Priority: P1)

A person who already uses the bot continues without being asked for a phone. Their existing runs stay where they are.

**Why this priority**: The current bot is the working product. This story must not make Telegram depend on a phone.

**Independent Test**: Open the existing bot with a person who has no phone, return to an unfinished run, and confirm no phone is requested.

**Acceptance Scenarios**:

1. **Given** a person uses only Telegram, **When** they continue an unfinished run, **Then** the run continues and the product does not ask for a phone.
2. **Given** a person uses only Telegram, **When** they look at account settings, **Then** the phone is empty and their runs are unchanged.

---

### User Story 3 - Merge only from settings after both entrances are confirmed (Priority: P2)

A person adds the missing entrance in account settings. The second entrance is confirmed by a code in the channel being added. Until both are confirmed, the two entrances do not share runs. After both are confirmed, the runs of both belong to one person.

**Why this priority**: Silent linking would mix two people. Merge is valuable only after each entrance is proven.

**Independent Test**: Create a phone-only person and a Telegram-only person, confirm both entrances in settings, and check that both sets of runs are listed once and that unconfirmed pairs stay separate.

**Acceptance Scenarios**:

1. **Given** a person has only a phone, **When** they type a Telegram identity in settings but have not entered the code sent in the bot, **Then** the entrances stay separate and runs are not combined.
2. **Given** a person has only Telegram, **When** they type a phone in settings but have not entered the SMS code, **Then** the entrances stay separate and runs are not combined.
3. **Given** both a phone and a Telegram identity are entered together in settings, **When** each is confirmed by its own code, **Then** the runs of both entrances belong to one person.
4. **Given** two entrances are merged, **When** the same skill has different marks, **Then** that skill's mark becomes «неравномерно».
5. **Given** two entrances are merged, **When** the same skill has the same mark, **Then** that mark stays as it was.
6. **Given** two entrances are merged, **When** the person reads the visible profile text, **Then** the two texts are not rewritten into one combined text.
7. **Given** a phone or a Telegram identity is already confirmed on another person, **When** someone tries to confirm it again, **Then** the product refuses and does not move runs.

### Edge Cases

- A wrong or replaced code does not admit the person and does not merge entrances.
- Confirming only one of the two values, even if both were typed, does not merge.
- «не наблюдалось» and any other mark on the same skill count as different, so the merged mark is «неравномерно».
- The SMS is only an entrance code. It is not a copy of the exercise, the profile, or the model choice.
- The bot's existing model choice, self-information file, and hidden profile stay on the Telegram entrance until a merge.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The product MUST admit a person by a phone number and an SMS code without requiring Telegram.
- **FR-002**: The SMS MUST carry the entrance code and MUST NOT carry the exercise dialogue, the profile, or the model choice.
- **FR-003**: A person who uses only Telegram MUST be able to continue the existing bot without a phone, and their existing runs MUST stay unchanged.
- **FR-004**: Phone and Telegram MUST be optional links to one internal person. Neither link MUST be required for the other to work.
- **FR-005**: The product MUST NOT merge two entrances at sign-in.
- **FR-006**: The person MUST be able to enter a phone, a Telegram identity, or both in account settings.
- **FR-007**: A newly added phone MUST be confirmed by an SMS code. A newly added Telegram identity MUST be confirmed by a code in the bot.
- **FR-008**: Until both links are confirmed, each entrance MUST keep its own runs, model choice, and profile.
- **FR-009**: After both links are confirmed, the runs of both entrances MUST belong to one person and both sets MUST remain.
- **FR-010**: After a merge, a skill whose marks differ MUST be marked «неравномерно». A skill whose marks are the same MUST keep that mark.
- **FR-011**: A merge MUST NOT rewrite the two visible profile texts into one text.
- **FR-012**: The product MUST refuse to confirm a phone or a Telegram identity that is already confirmed for a different person.
- **FR-013**: A code that is not the latest code issued for that link MUST NOT admit the person and MUST NOT complete a merge.

### Key Entities

- **Person**: The internal identity. Phone and Telegram are links on the person, not the identity itself.
- **Entrance**: A confirmed phone or a confirmed Telegram identity. Before a merge, an entrance has its own runs, model choice, and profile.
- **Link code**: The latest code issued for one phone or one Telegram identity. A newer code replaces the previous one.
- **Run**: An exercise record that stays intact and moves with its entrance into the merged person.
- **Skill mark**: One of «не наблюдалось», «слабо», «проявляется», «устойчиво», «неравномерно» on one skill.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A new person can finish phone entry and reach the product without opening Telegram.
- **SC-002**: A Telegram-only person can continue an unfinished run, and the product asks for a phone in zero of those continuations.
- **SC-003**: Before both links are confirmed, a person sees only the runs of the entrance they are using.
- **SC-004**: After both links are confirmed, every run from both entrances is present once on the single person.
- **SC-005**: After a merge, every skill with two different marks shows «неравномерно», and every skill with one shared mark shows that same mark.
- **SC-006**: After a merge, both original visible profile texts are still present and neither has been replaced by a combined text.
- **SC-007**: The SMS for an entrance contains no sentence from the exercise dialogue.

## Assumptions

- This specification is only the account change in the product that already runs. The Android application, continuing a news review inside that application, and the application settings screens are later stories and are not specified here.
- Teaching the skill to delete duplicate profile sentences, generalize similar ones, and flag conflicts is a backlog story and is not specified here.
- Past-review, redo, and delete stories of the news feature stay parked.
- Voice dictation inside the application is out of scope. Telegram voice messages stay as they are.
- The SMS sender is an external delivery of the code. Which company sends the SMS is not a product choice in this story.
- The latest issued code is the only valid code for that link. The product does not accept an older code after a newer one was issued.
- A phone or Telegram identity already confirmed on another person is not taken over.
- The first audience remains the author. Store publication is out of scope.
- iOS is a later client of the same entrance rules and is not specified here.
