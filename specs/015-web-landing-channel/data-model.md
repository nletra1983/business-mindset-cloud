# Data model: 015-web-landing-channel

## guest_session

| Field | Meaning |
|---|---|
| id | Opaque ticket; also cookie value |
| created_at | Session start |
| windows_used_today | Count of guest windows started this calendar day (UTC+3 or server local — document in code as product TZ Europe/Moscow) |
| windows_day | Calendar date for the counter |
| current_window_id | Nullable id of open window |
| updated_at | Last touch |

Creating a row MUST NOT create a person.

## guest_window

| Field | Meaning |
|---|---|
| id | Window id |
| guest_session_id | FK |
| first_reply_at | Nullable until first human reply; starts 24h TTL |
| transcript | Ordered messages (guest + agent stubs may be empty in story 0) |
| cleared_client_at | Optional; UI clear does not delete row before TTL |
| closed_at | Optional |

Retention: delete or purge transcript when `now > first_reply_at + 24 hours` (if first_reply_at set). Windows without first reply may expire with session policy (same day / idle) — implement conservatively: purge when TTL clock started and expired.

## Config (not tables)

- `SMARTCAPTCHA_CLIENT_KEY`, `SMARTCAPTCHA_SERVER_KEY` from `secrets/smartcaptcha.env`
- `YANDEX_METRIKA_COUNTER_ID` non-secret env
- Mail remains `secrets/mail.env`
