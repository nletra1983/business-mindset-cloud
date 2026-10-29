# Feature Specification: Enter the app by email and see one's runs

**Feature Branch**: `008-app-email-entry`

**Created**: 2026-10-29

**Status**: Draft

**Input**: User description: "Мобильное приложение" — only the ready story «Войти в приложение по email и работать без Telegram». Boundary: `features/mobile-app/app-email-entry.md`.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Enter by email without Telegram (Priority: P1)

A person opens the app, enters an email, enters the code from that mailbox, and is inside. The app never asks them to open Telegram.

**Why this priority**: The account can already accept an email. This story is the first screen that uses it.

**Independent Test**: Open the app, submit an email and the matching code, and see no Telegram prompt.

**Acceptance Scenarios**:

1. **Given** a person opens the app, **When** they enter an email and the matching latest code, **Then** they are inside and the app does not mention Telegram.
2. **Given** a person enters a code that is not the latest code for that email, **When** they try to continue, **Then** they stay out and no second person is created.
3. **Given** the code letter cannot be sent, **When** they submit an email, **Then** they are told the code was not sent and they are not inside.

---

### User Story 2 - See only this entrance's runs (Priority: P1)

After a successful code, the person sees the list of runs that belong to this entrance. The list may be empty. They cannot open a run, start a review, open settings, or add a second entrance from this story.

**Why this priority**: Being inside has to show the person's own work, and must not pull in another entrance.

**Independent Test**: Enter with an email that has two runs, while another entrance has a different run, and see only the two runs. Enter with an email that has no runs and see an empty list.

**Acceptance Scenarios**:

1. **Given** this entrance has runs, **When** the person finishes email entry, **Then** each of those runs appears once in the list.
2. **Given** this entrance has no runs, **When** the person finishes email entry, **Then** the list is empty and the person remains inside.
3. **Given** another entrance has runs and the two entrances are not merged, **When** the person finishes email entry, **Then** the other entrance's runs are absent.
4. **Given** the person sees the list, **When** they look for a way to open a run, start a new review, change the model, edit self-information, or add Telegram, **Then** this screen does not offer those actions.

### Edge Cases

- A replaced code does not reveal the list.
- An email that is already confirmed opens that same person and shows that person's runs, without merging another entrance.
- The letter still contains only the entrance code.
- The app does not call a model provider and does not work offline.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The app MUST let a person enter with an email and the latest code sent to that mailbox.
- **FR-002**: The app MUST NOT ask the person to open Telegram or to link a Telegram identity on this screen.
- **FR-003**: A wrong or replaced code MUST keep the person out and MUST NOT create a second person.
- **FR-004**: After a successful code, the app MUST show the list of runs belonging to this entrance.
- **FR-005**: The list MUST be allowed to be empty, and an empty list MUST still mean the person is inside.
- **FR-006**: Before a merge, the list MUST NOT include runs of another entrance.
- **FR-007**: This screen MUST NOT open a run, start a review, open model or self-information settings, or collect a second entrance.
- **FR-008**: If the code letter cannot be sent, the person MUST be told and MUST NOT be shown the list.

### Key Entities

- **Person**: The internal identity reached by the email code. Unchanged by this story.
- **Run**: An exercise record shown by its topic. Opening it is out of scope.
- **Entrance**: The email used to sign in. The list is limited to its runs until a merge, which this story does not perform.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A person with a valid email code reaches the run list without seeing a Telegram prompt in any of those entries.
- **SC-002**: A wrong code shows the run list in zero of those attempts.
- **SC-003**: For an entrance with N runs, the list shows N items, and runs of a separate unmerged entrance contribute zero items.
- **SC-004**: An entrance with no runs shows an empty list and still leaves the person inside.
- **SC-005**: The entry screen offers zero actions for opening a run, starting a review, changing the model, editing self-information, or adding Telegram.

## Assumptions

- Account rules, including the letter, the latest code, and the refusal to merge at sign-in, are already specified in `specs/007-email-account-entry/` and are not rewritten here.
- The first build is Android for the author, without a store. iOS is a later client of the same screen rules.
- Starting a review, returning inside a run, settings, and the second entrance are later stories.
- The app talks only to the product. It does not call a model provider.
