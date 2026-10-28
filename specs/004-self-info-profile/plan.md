# Implementation Plan: Прочитать, изменить и добавить информацию о себе

**Branch**: `004-self-info-profile` | **Date**: 2026-10-28 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/004-self-info-profile/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

История добавляет пользовательский поток `информация о себе` в Telegram-настройках: показать видимый профиль, отдельно принять обновление сильных и слабых сторон, дать добавить факты о себе, и сохранить изменения для следующего чтения. При этом скрытый оценочный профиль остаётся приватным и не перезаписывается прямыми правками пользователя.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: `httpx`, `psycopg` (v3, binary), существующий Telegram long-poll поток

**Storage**: Postgres существующего контура; разделение видимого пользовательского профиля и скрытого профиля в отдельных записях

**Testing**: `pytest` (новые тесты профиля + регрессия текущих тестов Telegram потока)

**Target Platform**: Linux-контур Selectel, тот же контейнер `bot`

**Project Type**: один серверный процесс (Telegram-бот + бизнес-логика)

**Performance Goals**: отдельный новый KPI не вводится; профильный ответ должен оставаться в текущем UX-ритме Telegram-диалога

**Constraints**: стек/топология не перевыбираются; личные данные остаются в текущем контуре; hidden profile не показывается пользователю; прямые правки пользователя не изменяют evaluator-статусы

**Scale/Scope**: текущий Telegram-MVP контур (сотни пользователей); только история read/edit/add для видимого профиля, без истории автообновления скрытого профиля по результатам заданий

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Один процесс и тот же репозиторий: изменения в `app/*` и `tests/*`, без нового сервиса. Pass.
- Канал Telegram остаётся первым и не владеет ходом упражнения. Pass.
- Данные профиля остаются в Postgres текущего контура Selectel, без выноса хранилища наружу. Pass.
- Стек не перевыбирается: Python + Postgres + Telegram через `TELEGRAM_API_BASE`. Pass.
- Граница истории соблюдена: read/edit user-visible profile; hidden profile update-by-exercise не объединяется в этот срез. Pass.
- Открытых `NEEDS CLARIFICATION` в spec нет. Pass.

### Post-design

После Phase 1 артефакты остаются в рамках той же границы: отдельные сущности для visible/hidden профилей, Telegram-контракт только для user-visible редактирования, без смены стека и без расширения на платные модели или мобильный контур.

## Project Structure

### Documentation (this feature)

```text
specs/004-self-info-profile/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── telegram-self-info-profile.md
└── tasks.md              # /speckit-tasks, этим шагом не создаётся
```

### Source Code (repository root)

```text
app/
├── telegram_poll.py        # callback/message routing settings/profile
├── account_settings.py     # settings menu and profile actions
├── person.py               # person-related reads/writes
├── db.py / schema.sql      # profile storage schema and migration hooks
└── run_flow.py             # existing exercise flow; no direct profile-edit overwrite

tests/
├── test_account_settings_entry.py
├── test_account_settings_state.py
└── (new) test_self_info_profile.py
```

**Structure Decision**: используем существующую single-process структуру `app/`; добавляем профильный read/edit поток в текущие модули настроек и Postgres-схему, с тестами в `tests/`.

## Complexity Tracking

Нарушений конституции, требующих отдельного обоснования, нет.
