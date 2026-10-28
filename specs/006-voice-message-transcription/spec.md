# Feature Specification: Voice Message Becomes Text in Existing Flows

**Feature Branch**: `cursor/003-open-account-settings-8e5d`

**Created**: 2026-10-28

**Status**: Draft

**Input**: User description: "расшифровка голосовых сообщений"

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.

  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - Voice reply enters the same dialogue flow as typed text (Priority: P1)

As a person in Telegram, I can send a voice message from the microphone where text input is already accepted, and the bot converts it to text and processes it exactly as a typed message in the same flow.

**Why this priority**: This is the core value of the feature: voice input must become usable text without changing existing exercise/profile flows.

**Independent Test**: Send one valid voice message in an open dialogue context and verify the bot shows recognized text, then advances through the same rules as typed text.

**Acceptance Scenarios**:

1. **Given** a context where typed messages are accepted, **When** the person sends a microphone voice message, **Then** the system converts speech to text, shows that text as a separate bot message without signature, and processes it by the same dialogue rules as typed input.
2. **Given** recognized text from a voice message, **When** it is handled, **Then** step progression, duplicate Telegram update handling, and profile-edit prompts behave identically to typed text handling.

---

### User Story 2 - Unsupported voice capability does not move dialogue state (Priority: P2)

As a person, if my currently selected model does not support voice-to-text for this flow, I get a clear message and my dialogue step does not move.

**Why this priority**: Without this guardrail, users lose control and may accidentally change run state with unusable voice input.

**Independent Test**: Select a model without confirmed voice support and send a voice message; verify no step change and the message `Эта модель не разбирает голос.`

**Acceptance Scenarios**:

1. **Given** the selected model cannot accept voice in this flow, **When** a voice message is sent, **Then** no user utterance is recorded from that voice, step does not move, and the bot responds `Эта модель не разбирает голос.`

---

### User Story 3 - Empty recognition result is recoverable and preserves state (Priority: P3)

As a person, if voice recognition returns no text, I receive a recoverable message and the current dialogue remains unchanged.

**Why this priority**: Recognition failures are expected and must not corrupt run state or profile flows.

**Independent Test**: Send a voice message that yields no text; verify no state movement and the message `Голос не разобран.`

**Acceptance Scenarios**:

1. **Given** a voice message is accepted for recognition but no text is produced, **When** processing completes, **Then** no reply text enters dialogue logic, step remains unchanged, and the bot responds `Голос не разобран.`

### Edge Cases

- The message is an audio file or round video instead of a microphone voice message: it is out of scope and must not be treated as this feature’s voice input.
- A duplicate Telegram delivery of the same voice update arrives: state must not move twice, matching existing duplicate-update handling.
- Voice content includes words that look like commands (for example model names or settings labels): voice input is treated only as human text utterance, not as button presses or navigation.
- The selected model supports dialogue text but voice path is not confirmed: the bot returns `Эта модель не разбирает голос.` and keeps state unchanged.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST accept microphone voice messages in the same contexts where it currently accepts typed text from the person.
- **FR-002**: The system MUST treat voice message conversion as an input step only: it extracts words and does not answer exercise questions or move step before text is produced.
- **FR-003**: When conversion produces text, the system MUST send that recognized text as a separate bot message without signature, then process it with the same rules as typed text in the current flow.
- **FR-004**: Voice-derived text MUST pass through existing dialogue behavior unchanged, including run step logic, duplicate-update protection, and profile-edit prompts.
- **FR-005**: Product record for this feature MUST remain text-based; source audio MUST NOT be stored after recognition.
- **FR-006**: Voice input MUST NOT press buttons, open settings, or change model selection; only explicit callbacks/buttons may do that.
- **FR-007**: If the currently selected model does not support voice-to-text for this flow, the system MUST respond `Эта модель не разбирает голос.`, MUST NOT create a text utterance from that voice, and MUST NOT move step.
- **FR-008**: If recognition path is supported but returns no text, the system MUST respond `Голос не разобран.`, MUST NOT create a text utterance from that voice, and MUST NOT move step.
- **FR-009**: This feature MUST NOT change boundaries of exercise flow, account settings behavior, keyboard behavior, or model-choice logic already implemented.
- **FR-010**: This feature MUST include only microphone voice messages; standalone audio files and round videos remain out of scope.

### Key Entities *(include if feature involves data)*

- **Voice Message Input**: Incoming Telegram microphone voice message authored by the person in a context where typed text is already accepted.
- **Recognized Text Utterance**: Text extracted from a voice message and forwarded into existing typed-message handling flow.
- **Voice Recognition Outcome**: Conversion result with three business outcomes: unsupported voice capability, no recognized text, or recognized text ready for normal processing.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In acceptance testing, 100% of supported microphone voice inputs produce text that is processed by the same path and state rules as typed text.
- **SC-002**: In acceptance testing, 100% of unsupported-voice cases return `Эта модель не разбирает голос.` and change 0 dialogue steps.
- **SC-003**: In acceptance testing, 100% of empty-recognition cases return `Голос не разобран.` and change 0 dialogue steps.
- **SC-004**: In acceptance testing, recognized-voice path introduces 0 regressions in existing typed-message flows (exercise step handling, duplicate-update behavior, profile-edit prompts).

## Assumptions

- The selected model remains the authority for processing this person’s input in the current run context, including voice-to-text capability checks for this slice.
- Existing typed-message flow is already stable and reused; this feature only adds entry of text via voice conversion.
- This slice does not introduce new channels, new exercise type, or separate speech-recognition service.
- Voice conversion result is transient for processing; long-term product storage continues to be text records only.
