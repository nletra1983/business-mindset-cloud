# Implementation Plan: Веб-канал лендинга на Selectel

**Branch**: `015-web-landing-channel` | **Date**: 2026-11-02 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/015-web-landing-channel/spec.md`

## Summary

В том же процессе `bot` на Selectel открывается раздача каркаса лендинга `get-business-idea.ru` и шов HTTP для будущих гостевых/smoke-вызовов, без второго процесса. Появляется гостевая сессия (cookie) с лимитом окон и TTL ленты 24 ч. В compose подключается `secrets/smartcaptcha.env`; Метрика — non-secret env; get-news бэклог обновляется с периодом 4 ч. Полная воронка (копирайт, email без кода, оплата) — следующие истории.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: существующий `http.server` / `channel_http` в том же процессе; `psycopg`; без нового веб-фреймворка

**Storage**: Postgres (гостевые сессии); файл бэклога get-news на диске/в репо-пути как в скилле

**Testing**: `pytest` на выдаче cookie/сессии и статике/маршруте лендинга без живого DNS

**Target Platform**: контейнер `bot` на Selectel; TLS и server_name для домена — на nginx хоста (ручной/инфра шаг оператора)

**Project Type**: один серверный процесс

**Performance Goals**: новый порог не задаётся

**Constraints**: стек не перевыбирается; `/app/v1` и Telegram не ломать; секретные значения не в git; агент не ходит на Selectel

**Scale/Scope**: история №0; каркас + шов

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Один процесс, без нового сервиса. Pass.
- ADL-023: веб-лендинг на том же хосте; гость без person. Pass.
- Записи в РФ (Postgres Selectel). Pass.
- Стек не перевыбирается. Pass.
- Спеки `001`–`014` не переписываем. Pass.
- Полная воронка вне этой истории. Pass.

### Post-design

Статика/каркас и guest API под префиксом лендинга (не `/app/v1`). TLS снаружи. Cron/фоновый тик get-news в том же процессе.

## Project Structure

### Documentation (this feature)

```text
specs/015-web-landing-channel/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── web-landing-v1.md
└── tasks.md
```

### Source Code (repository root)

```text
app/
├── schema.sql
├── channel_http.py
├── main.py
├── web_landing.py          # NEW: static shell + guest session helpers
└── get_news_backlog.py     # NEW or extend: 4h refresh hook

web/                        # NEW: minimal landing shell assets
└── index.html

docker-compose.yml          # env_file smartcaptcha
```

**Structure Decision**: расширить существующий HTTP-слушатель; не поднимать второй порт без нужды (тот же CHANNEL_HTTP_PORT / отдельный path на том же listener).
