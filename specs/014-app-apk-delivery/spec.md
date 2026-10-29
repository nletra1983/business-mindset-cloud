# Feature Specification: Build a Flutter client and give the author a signed APK

**Feature Branch**: `014-app-apk-delivery`

**Created**: 2026-10-29

**Status**: Draft

**Input**: User description: «Собрать Flutter-клиент и отдать автору подписанный APK». Boundary: `features/mobile-app/app-apk-delivery.md`. Feature: Мобильное приложение.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Install the product on the author's Android phone (Priority: P1)

The author receives a signed install file for an ordinary current Android phone. They install it without a store. The next build with the same package id and the same signing key installs over the previous one.

**Why this priority**: Without an install file, later screen stories cannot be checked on a real phone.

**Independent Test**: Place a signed APK on the author's computer in the project's build folder, install it on the author's Android phone without a store, and open the app.

**Acceptance Scenarios**:

1. **Given** the Flutter client project exists in this repository, **When** a release build finishes, **Then** a signed APK file appears on the author's computer in the project's build folder.
2. **Given** that APK, **When** the author installs it on their ordinary current Android phone without a store, **Then** the app opens.
3. **Given** a later build with the same package id and the same signing key and a higher version, **When** the author installs it, **Then** it replaces the previous install instead of sitting beside it as a second app.

---

### User Story 2 - Keep the signing key and talk only to the product entrance (Priority: P1)

The signing key stays with the author outside git, like other secrets. The app reaches the product only through the already opened channels entrance. Full review screens beyond a thin entry shell can arrive in later stories after install.

**Why this priority**: A leaked key or a second backend would break trust and the accepted architecture.

**Independent Test**: Confirm the signing key is not in git. Confirm the client is configured to call only the channels entrance host/path already accepted for the app.

**Acceptance Scenarios**:

1. **Given** the repository, **When** secrets and ignore rules are checked, **Then** the signing key material is absent from git and is expected to live with the author like other secrets.
2. **Given** the installed app, **When** it talks to the product, **Then** it uses only the channels entrance already opened for the application, not Telegram API and not a model provider.
3. **Given** this delivery story, **When** scope is checked, **Then** iOS, store listings, and messenger redistribution of the APK are out of scope.

### Edge Cases

- First build may use a local author keystore that never enters git.
- If the key is lost, a new package id (or a new key with a clean install) is required — not silently swapped under the same install.
- Email login screens and full review UI may be thin in this delivery and completed by neighbouring stories after the file exists.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The repository MUST contain one Flutter client project for this product.
- **FR-002**: A release build MUST produce a signed APK on the author's computer in the project's build folder.
- **FR-003**: The APK MUST use one stable application package id across builds intended to update in place.
- **FR-004**: The signing key MUST be stored with the author outside git, following the same secrecy practice as other product secrets.
- **FR-005**: A later signed build with the same package id, the same key, and a higher version MUST be installable over the previous version.
- **FR-006**: The client MUST reach the product only through the already accepted application channels entrance.
- **FR-007**: The first supported phone class MUST be an ordinary current Android device; a separate legacy Android line MUST NOT be maintained.
- **FR-008**: This story MUST NOT deliver iOS builds, store listings, paid store accounts, or redistribution of the APK through messengers.
- **FR-009**: Full screens for later mobile stories MAY remain thin here; this story MUST still deliver an installable signed APK and a client shell that can open the channels entrance.

### Key Entities

- **Flutter client project**: The single cross-platform client source tree in this repository.
- **Signed APK**: The install file for the author's Android phone.
- **Package id**: Stable application identity so updates replace the previous install.
- **Signing key**: Author-held secret used to sign release builds; not in git.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: After a release build, the author can point to one signed APK file under the project's build folder on their computer.
- **SC-002**: The author can install that APK on their ordinary current Android phone without using a store.
- **SC-003**: A second higher-version build signed with the same key and the same package id installs over the first (one app icon, not two).
- **SC-004**: Zero signing-key files are present in git history for this delivery.
- **SC-005**: The installed client performs product network calls only toward the accepted channels entrance, not toward Telegram API or a model provider.

## Assumptions

- Channels entrance from `specs/012-app-channel-api/` and session rules from `specs/013-app-session/` already exist on the server side.
- Email entry and later screens (`specs/008`–`011`) may deepen UI after this install file exists.
- Concrete `minSdk` follows current Flutter stable defaults for an ordinary current Android phone.
- Host for the channels entrance is the same bot-service host already used in production; the path is the accepted `/app/v1` entrance.
- Author creates or already holds the keystore outside git; the repo only documents required file names and ignore rules, never key material.
