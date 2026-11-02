# Research: 015-web-landing-channel

## Decision: Same HTTP listener, new path prefix

**Rationale**: `/app/v1` already serves the Flutter channel on `CHANNEL_HTTP_PORT`. Landing pages and future guest API attach as another prefix (e.g. `/` for host `get-business-idea.ru` or `/web/`) on the same listener. Nginx `server_name` routes the public domain to that port.

**Alternatives considered**: Second process / GitHub Pages — rejected by ADL-023.

## Decision: Guest session in Postgres

**Rationale**: Cookie id maps to a row with day counters and JSON/text transcript; TTL cleanup by `first_reply_at + 24h`. No `person_id` until a later story binds email.

**Alternatives considered**: Cookie-only client storage — fails continue-after-email and TTL server policy.

## Decision: get-news refresh in-process

**Rationale**: Skill period is 4 hours. A lightweight periodic check in the bot process (or on first guest need) rewrites `features/business-idea-from-news/FeatureArtifacts/get-news-backlog.md` when stale. No second worker container.

**Alternatives considered**: External cron container — extra process, rejected for now.

## Decision: SmartCaptcha env wiring only

**Rationale**: Story 0 names secrets and compose `env_file`; challenge verification is story 2+.

## Decision: DNS/TLS are operator steps

**Rationale**: Constitution forbids agent SSH to Selectel; quickstart documents manual DNS A + nginx `server_name`.
