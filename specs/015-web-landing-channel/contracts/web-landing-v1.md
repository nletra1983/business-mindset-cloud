# Contract: web landing v1 (story 0)

Base: same host/port as channel HTTP (`CHANNEL_HTTP_PORT`). Public name: `get-business-idea.ru` via nginx.

## GET / (or landing index)

- Serves minimal HTML shell (placeholder for story 1 blocks).
- Sets `Set-Cookie` guest ticket if missing (`HttpOnly`, `Secure` when HTTPS, `SameSite=Lax`).
- Does not create a person.

## GET /web/v1/guest/session (illustrative)

- Returns JSON: `{ "guest_id": "...", "windows_used_today": N, "windows_limit": 3 }` for the cookie.
- 401/empty guest if cookie unknown → mint new session.

## POST /web/v1/guest/ping (optional stub)

- Ensures session exists; no smoke call yet.

## Out of scope paths

- Smoke turns, email gate, payment, captcha verify — later stories; may reserve `/web/v1/...` namespace.

## Non-interference

- `/app/v1/*` unchanged.
- Telegram long poll unchanged.
