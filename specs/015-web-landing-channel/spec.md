# Feature Specification: Web landing channel on Selectel

**Feature Branch**: `015-web-landing-channel`

**Created**: 2026-11-02

**Status**: Draft

**Input**: История №0 фичи «Главная сайта: лендинг-тренажёр (веб)». Граница: `features/website-idea-assess/web-guest-channel.md`. ADL-023.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Open the landing host without breaking the bot (Priority: P1)

A visitor opens `get-business-idea.ru` (and `www` that leads there) on the same product service that already runs the Telegram bot. They see at least a landing shell. Telegram long poll and the existing app path keep working as before.

**Why this priority**: Without a live host and shell, later landing stories have nowhere to attach.

**Independent Test**: Resolve DNS to the Selectel server, load the landing URL over HTTPS, see a page shell, and confirm the bot and `/app/` entrance still accept their usual traffic.

**Acceptance Scenarios**:

1. **Given** DNS for `get-business-idea.ru` points at the same Selectel host as the bot, **When** a visitor opens that domain, **Then** they receive a landing page shell from the same product process.
2. **Given** `www.get-business-idea.ru` is configured, **When** a visitor opens www, **Then** they end on `get-business-idea.ru` (redirect or equivalent).
3. **Given** the landing channel is live, **When** Telegram and the app entrance are used as before, **Then** they still work and are not replaced by a second process or second public product host.

---

### User Story 2 - Hold a guest ticket for later funnel stories (Priority: P1)

A first-time visitor gets a guest ticket (browser cookie) so the product can count daily guest windows and keep a guest transcript for up to 24 hours from the first reply. Clearing the on-screen window does not have to wipe the server copy before that TTL ends. Full guest chat UX is a later story; this story only establishes the session place.

**Why this priority**: Email continue and smoke steps need a server-side guest session; inventing it later would reopen architecture.

**Independent Test**: Open the landing, receive a guest cookie, see the product store a guest session with day-window counter and TTL fields, and confirm no person account is created yet.

**Acceptance Scenarios**:

1. **Given** a visitor with no prior ticket, **When** they hit the landing channel, **Then** the product issues a guest cookie and a guest session record without creating a person account.
2. **Given** a guest session exists, **When** the calendar day rolls or windows are counted, **Then** the session can hold “windows used today” and “current window” for a limit of three windows per day (enforcement UX may complete in a later story).
3. **Given** a guest transcript is stored, **When** 24 hours pass from the first reply of that window, **Then** that window’s transcript is no longer kept for continue-after-email; clearing the UI alone does not require immediate server wipe before TTL.

---

### User Story 3 - Leave hooks for news backlog, smoke, captcha, mail, and Metrika (Priority: P2)

The same process has a place to refresh the get-news backlog every four hours and to accept future smoke / guest API calls. SmartCaptcha secret file names are wired into the bot service env list. Mail for day-2 uses the existing mail secret contour. Metrika counter id is named as non-secret config. Full captcha checks, smoke dialogue, email gate, day-2 letter, and fake pay are out of scope.

**Why this priority**: Later stories must plug into named seams without rewriting deploy layout.

**Independent Test**: Confirm compose/env lists `secrets/smartcaptcha.env`, mail contour remains `secrets/mail.env`, Metrika id is configurable without secrets/, and a scheduled or equivalent hook exists for get-news backlog age of four hours.

**Acceptance Scenarios**:

1. **Given** the service configuration, **When** operators place `SMARTCAPTCHA_CLIENT_KEY` and `SMARTCAPTCHA_SERVER_KEY` in `secrets/smartcaptcha.env`, **Then** the bot service loads that file via env_file alongside existing secrets.
2. **Given** the get-news backlog file, **When** more than four hours passed since its “Создан” line (or the file is missing), **Then** the product can refresh the backlog on the four-hour cadence without a second process.
3. **Given** Metrika is configured, **When** pages are served, **Then** a non-secret `YANDEX_METRIKA_COUNTER_ID` can be supplied from app config (embedding events is a later story).

### Edge Cases

- Missing SmartCaptcha values must not be invented; operator places them outside git.
- Agent must not SSH to Selectel; deploy follows existing main/publish path.
- Specs `001`–`014` must not be rewritten by this story.
- Full marketing blocks, email-without-code gate, day-2 email body, fake payment UI, and captcha challenge UX are later stories.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The product MUST serve the landing for `get-business-idea.ru` from the same process and Selectel host as the bot.
- **FR-002**: `www` MUST resolve to the same landing site (redirect or equivalent to the apex domain).
- **FR-003**: Opening the landing channel MUST NOT break Telegram long poll or the existing `/app/` entrance.
- **FR-004**: The product MUST NOT introduce a second process or second public product host solely for this landing.
- **FR-005**: The product MUST issue and recognize a guest cookie session for visitors who are not logged in as a person.
- **FR-006**: A guest session MUST be able to store daily window count (max three windows per calendar day), current window state, and guest transcript with TTL of 24 hours from the first reply of that window.
- **FR-007**: Clearing the on-screen window MUST NOT be required to delete the server transcript before TTL ends.
- **FR-008**: Creating a guest session MUST NOT create a person account by itself.
- **FR-009**: The service MUST load SmartCaptcha keys from `secrets/smartcaptcha.env` (`SMARTCAPTCHA_CLIENT_KEY`, `SMARTCAPTCHA_SERVER_KEY`) via docker-compose env_file on the bot service.
- **FR-010**: Day-2 / landing mail MUST reuse the existing `secrets/mail.env` contour (no dialogue text in mail for this story).
- **FR-011**: Metrika counter MUST be configurable as non-secret `YANDEX_METRIKA_COUNTER_ID`.
- **FR-012**: The product MUST support refreshing the get-news backlog on a four-hour period consistent with `get-news.md`.
- **FR-013**: The product MUST expose a place (HTTP API or equivalent channel adapter) for later guest/smoke calls without implementing the full funnel UX in this story.
- **FR-014**: This story MUST NOT implement full landing copy blocks, email gate without code, day-2 send, fake payment, or end-user captcha challenge flow (those are stories 1–6).
- **FR-015**: This story MUST NOT rewrite specs `001`–`014`.

### Key Entities

- **Guest session**: Cookie-bound ticket; day window counter; current window; transcript TTL.
- **Landing channel**: Same-process HTTP surface for pages and future guest/smoke API on `get-business-idea.ru`.
- **News backlog**: File maintained by get-news on a four-hour refresh period.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A visitor can open `https://get-business-idea.ru/` and see a landing shell without using Telegram.
- **SC-002**: After deploy of this story, Telegram bot and `/app/` continue to serve their existing successful paths (no regression smoke failure attributable to this change).
- **SC-003**: A first visit creates exactly one guest session for that cookie without creating a person record.
- **SC-004**: Guest transcript retention policy of 24 hours from first reply is documented in behavior and observable in storage rules for a test window.
- **SC-005**: Bot service configuration lists `secrets/smartcaptcha.env` so operators can supply keys without code changes to secret names.
- **SC-006**: get-news backlog older than four hours is eligible for refresh without manual file rename or a second service.

## Assumptions

- DNS A-record and TLS for `get-business-idea.ru` are applied by the operator following existing Selectel/nginx practice; the agent does not log into the server.
- Landing “shell” may be minimal HTML until story 1 fills marketing blocks.
- Model name for the showcase remains a gateway setting; this story does not pick a model on screen.
- Full funnel (smoke steps, email without code, fake pay) builds on this seam in later stories of the same feature.
