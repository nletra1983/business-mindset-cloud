# Quickstart: 015-web-landing-channel

## Local

1. Add empty placeholders locally (no real secrets in git): `secrets/smartcaptcha.env` with the two key names.
2. `docker compose` / existing bot run with `CHANNEL_HTTP_PORT`.
3. `curl -i http://127.0.0.1:8080/` (or landing path) — expect 200 HTML and `Set-Cookie`.
4. Second curl with cookie — same guest id; `windows_used_today` readable via guest session endpoint.
5. `curl http://127.0.0.1:8080/app/v1/...` health/smoke from existing tests still passes.

## Operator (Selectel) — manual

1. DNS A `get-business-idea.ru` → IP сервера Selectel (тот же, что у бота); `www` → редирект на apex.
2. В nginx: `server_name get-business-idea.ru www.get-business-idea.ru;` TLS (Let's Encrypt) → `proxy_pass` на порт `CHANNEL_HTTP_PORT` (часто 8080 на localhost контейнера/хоста).
3. На сервере файл `secrets/smartcaptcha.env` с ключами (как `smartcaptcha.env.example`); `mail.env` уже для писем.
4. При необходимости: `YANDEX_METRIKA_COUNTER_ID` в environment compose (не секрет).
5. Агент на сервер по SSH не заходит — выкладка через `main` / `/publish`.

## Tests

`py -3.12 -m pytest tests/test_web_landing.py` (to be added) plus existing `tests/test_channel_api.py`.
