# Feature Specification: Open a protected channels entrance for the app

**Feature Branch**: `012-app-channel-api`

**Created**: 2026-10-29

**Status**: Draft

**Input**: User description: «Открыть защищённый вход модуля каналов для приложения». Boundary: `features/mobile-app/app-channel-api.md`. Feature: Мобильное приложение.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Reach the product from the phone without Telegram API (Priority: P1)

The phone talks only to the product over a protected entrance. It does not call Telegram and does not call a model provider. After a successful email code, it receives a session secret and can use the product through that entrance.

**Why this priority**: Without this entrance the Flutter screens have nowhere to send email login, the run list, the review, or settings.

**Independent Test**: Request a code for an email, confirm it through the entrance, receive a session secret, and complete one product action that the bot already allows for that person. Confirm that no Telegram chat was required.

**Acceptance Scenarios**:

1. **Given** a person has no open Telegram chat, **When** they request an email code and confirm it through the channels entrance, **Then** they receive a session secret and are inside the product for that email entrance.
2. **Given** a code letter is sent through this entrance, **When** the person reads it, **Then** it contains the entrance code and does not contain the exercise dialogue, the profile, or the model choice.
3. **Given** a wrong or replaced code, **When** they try to confirm it through this entrance, **Then** they receive no session secret and no second person is created.

---

### User Story 2 - Use the same host with a separate path (Priority: P1)

The entrance lives on the same host as the already running bot service in the Russian contour. It uses a separate path and its own request contract. It does not open a second process, a second database, or a second public host.

**Why this priority**: A second host or process would split the product the architecture forbids splitting.

**Independent Test**: Call the entrance on the bot service host at a path that is not the Telegram long poll, and see the email and product actions succeed there. Confirm no second process was started for the app alone.

**Acceptance Scenarios**:

1. **Given** the bot service is running, **When** the app uses the channels entrance, **Then** the host is the same service host and the path is distinct from Telegram long poll.
2. **Given** the entrance is open, **When** the app requests code, confirm, run list, review, settings, or merge, **Then** those actions reuse the already accepted account and bot rules and do not invent a second copy of them.

---

### User Story 3 - Keep product steps idempotent through the entrance (Priority: P2)

The same incoming operation sent twice through the entrance does not move a review step twice. After the session secret is issued, later calls that need the person use that secret.

**Why this priority**: The bot already forbids double-moving a step. The phone channel must not weaken that.

**Independent Test**: Deliver the same answer twice for an open run through the entrance and see the step advance only once.

**Acceptance Scenarios**:

1. **Given** an open run and a session secret, **When** the same answer is submitted twice through the entrance, **Then** the step moves only on the first accepted delivery.
2. **Given** a call that needs the person after login, **When** it arrives without a valid session secret, **Then** the product refuses it and does not move a run.

### Edge Cases

- Failed letter delivery does not leave a confirmed person or a session secret.
- An already confirmed email opens that same person; sign-in does not merge another entrance.
- Flutter screens, APK packaging, and how the phone stores the secret are other stories.
- Choosing a mail vendor is not this story; letter content rules stay as already accepted.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The product MUST accept application requests over a protected HTTPS entrance into the existing channels module.
- **FR-002**: That entrance MUST use the same host as the running bot service and MUST use a path and request contract distinct from Telegram long poll.
- **FR-003**: The entrance MUST NOT start a second process, a second database, or a second public host for the application alone.
- **FR-004**: Through the entrance the application MUST be able to request an email code, confirm the code, and receive a session secret after a successful confirmation.
- **FR-005**: With a valid session secret the application MUST be able to list that entrance's runs, continue a news review, open settings, and start the second-entrance merge using already accepted rules.
- **FR-006**: The phone MUST NOT need Telegram API access and MUST NOT call a model provider through this entrance.
- **FR-007**: The code letter sent for this entrance MUST carry only the entrance code and MUST NOT carry exercise dialogue, profile text, or model choice.
- **FR-008**: A wrong or replaced code MUST NOT issue a session secret and MUST NOT create a second person.
- **FR-009**: A repeated delivery of the same incoming operation MUST NOT move a review step a second time.
- **FR-010**: A call that needs the person after login and arrives without a valid session secret MUST be refused without moving a run.
- **FR-011**: This story MUST NOT build Flutter screens, package an APK, or define how the device stores the session secret.

### Key Entities

- **Channels entrance**: The protected way the application reaches the same product the bot already uses.
- **Session secret**: Proof issued after a successful email code. Later person-bound calls carry it. How the phone stores it is another story.
- **Person / Entrance / Run**: Unchanged meanings from the email-account and bot stories. This story exposes them; it does not redefine them.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A person can finish email entry through the entrance and receive a session secret without opening Telegram in any of those successful entries.
- **SC-002**: Every successful entrance call uses the same bot-service host and a path that is not Telegram long poll.
- **SC-003**: Zero second processes and zero second public hosts are required for the application entrance alone.
- **SC-004**: After a valid session secret, the person can complete at least one already accepted product action (run list, review step, settings, or merge start) through the entrance.
- **SC-005**: A duplicated answer through the entrance moves the review step zero additional times.
- **SC-006**: Calls without a valid session secret after login leave run steps unchanged in every refusal.

## Assumptions

- Account rules for email, merge marks, and profile text stay as specified in `specs/007-email-account-entry/` and are called, not rewritten.
- Screen-level stories `specs/008`–`specs/011` describe what the person sees; this story opens the server seam those screens will call.
- Device session storage and explicit logout are story №3 (`features/mobile-app/app-session.md`).
- Flutter client and signed APK are story №4.
- Exact path name is an implementation choice. Product requires one host and a separate path (ADL-021).
- Mail sender for the author test remains as already recorded for the feature; this story does not choose a new vendor.
