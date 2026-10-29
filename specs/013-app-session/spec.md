# Feature Specification: Keep the login session on the device and offer explicit logout

**Feature Branch**: `013-app-session`

**Created**: 2026-10-29

**Status**: Draft

**Input**: User description: «Держать сессию входа на устройстве и дать явный выход». Boundary: `features/mobile-app/app-session.md`. Feature: Мобильное приложение.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Stay signed in after a correct code (Priority: P1)

After a successful email code the person keeps a session secret on the device in the platform's secure store, not in an open file. The model provider key never lands on the device. The next time they open the app they stay signed in and see their entrance's run list without asking for a new code. The service does not sign them out on a timer.

**Why this priority**: Without a durable session every reopen forces a new letter, which breaks everyday use.

**Independent Test**: Finish email entry once, store the session, reopen the app flow without a new code, and see the run list for that entrance.

**Acceptance Scenarios**:

1. **Given** a person confirmed an email code and received a session secret, **When** they open the app again with that secret still present, **Then** they see their entrance's run list without requesting a new code.
2. **Given** a stored session secret, **When** it is inspected as product data on the device, **Then** it is held in the platform secure store and the model provider key is not present on the device.
3. **Given** a person who stayed signed in for a long time without using logout, **When** they open the app again, **Then** the service has not signed them out only because time passed.

---

### User Story 2 - Explicit logout revokes the server and clears the device (Priority: P1)

Logout happens only when the person chooses it. On logout the server revokes that session so the same secret is no longer accepted, and the device erases the secret. After logout a new letter code is required. Clearing the secret only on the phone is not enough.

**Why this priority**: A copied secret would stay valid if the server did not revoke it.

**Independent Test**: Log out once, then call a person-bound action with the old secret and see refusal. Confirm the device no longer holds the secret and that a new code is required to enter again.

**Acceptance Scenarios**:

1. **Given** a signed-in person, **When** they choose logout, **Then** the server rejects that session secret on the next person-bound call.
2. **Given** logout completed, **When** the device session store is checked, **Then** the secret is gone.
3. **Given** logout completed, **When** the person wants to use the product again, **Then** they must confirm a fresh email code before a new session secret is issued.

### Edge Cases

- Logout without a current secret is a safe no-op for the person: they are treated as signed out.
- A secret that was already revoked stays rejected.
- Requesting the first email code and the HTTPS channels entrance itself are other stories.
- Packaging the install file is another story; this story defines stay-signed-in and logout behaviour the client and server must honour.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: After a successful email code the product MUST keep the session secret on the device in the platform secure store, not in an open file.
- **FR-002**: The model provider key MUST NOT be stored on the device.
- **FR-003**: On the next open with a still-valid stored secret the person MUST stay signed in and MUST see their entrance's run list without a new code.
- **FR-004**: The service MUST NOT sign the person out solely because time passed.
- **FR-005**: Explicit logout MUST be available and MUST happen only on the person's initiative.
- **FR-006**: On logout the server MUST revoke that session so the same secret is no longer accepted for person-bound calls.
- **FR-007**: On logout the device MUST erase the session secret.
- **FR-008**: After logout the person MUST need a new email code before receiving a new session secret.
- **FR-009**: Clearing the secret only on the device MUST NOT be treated as sufficient logout by itself; server revoke is required.
- **FR-010**: This story MUST NOT redefine email code rules, merge, model choice, HTTPS host/path setup, or APK packaging.

### Key Entities

- **Session secret**: Proof issued after a successful email code. Stored on the device while signed in. Revoked on the server at logout.
- **Device session store**: Platform secure place on the phone that holds the secret while signed in and is empty after logout.
- **Revoked session**: Server record that makes a former secret unusable even if a copy remains elsewhere.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: After one successful email entry, 100% of reopen attempts with an unrevoked stored secret reach the run list without a new code letter.
- **SC-002**: After logout, 100% of person-bound calls using the old secret are refused.
- **SC-003**: After logout, the device session store contains zero session secrets for that person.
- **SC-004**: Zero automatic sign-outs occur solely because a timer expired while the person did not choose logout.
- **SC-005**: A person who only wiped the secret on the phone still cannot rely on that secret at the server if they later restore a copy — only server revoke makes logout complete (verified by attempting the old secret after server-side logout).

## Assumptions

- Email code request and first confirm live in neighbouring stories; this story starts after a session secret already exists.
- The protected channels entrance (`specs/012-app-channel-api/`) is the server seam that issues and checks the secret.
- Flutter project layout and signed APK delivery are story №4; this story still requires the stay-signed-in and logout behaviour, including server revoke now and device secure-store behaviour the client must honour.
- No idle timeout is introduced for sessions.
