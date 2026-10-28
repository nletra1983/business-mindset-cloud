# Implementation Plan: Обновлять скрытый файл профиля по результату задания

**Branch**: `005-hidden-profile-update` | **Date**: 2026-10-28 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/005-hidden-profile-update/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

История добавляет обновление скрытого профиля навыка по итогам завершённого или поставленного на паузу упражнения: сохраняются только наблюдаемые характеристики с доказательствами, применяются правила слияния статусов между ходами, поддерживается выбор одного `сейчас тренировать`, и сохраняется приватная граница между скрытым профилем и пользовательским `информация о себе`.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: `httpx`, `psycopg` (v3, binary), существующий Telegram long-poll контур

**Storage**: Postgres текущего контура; hidden профиль, история свидетельств и dedup по результатам хода

**Testing**: `pytest` (новые тесты hidden-profile merge + регрессия run_flow/settings)

**Target Platform**: Linux-контур Selectel, тот же контейнер `bot`

**Project Type**: один серверный процесс (Telegram-бот + бизнес-логика + профиль)

**Performance Goals**: обновление профиля выполняется в том же пользовательском цикле завершения хода без заметной задержки финального сообщения

**Constraints**: стек и топология не меняются; hidden профиль не показывается пользователю; статус `устойчиво` не ставится одним ходом; правка visible-профиля не меняет hidden-статусы

**Scale/Scope**: текущий Telegram MVP-контур (сотни пользователей); только история автообновления hidden-профиля по результату задания

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Один продукт/один процесс: изменения остаются в `app/*` и `tests/*`, без новых сервисов. Pass.
- Telegram остаётся первым каналом; логика упражнения и профиля остаётся на сервере. Pass.
- Хранение в текущем контуре Postgres РФ, без выноса данных профиля за контур. Pass.
- Стек не перевыбирается: Python + Postgres + существующий контур вызова модели. Pass.
- Граница истории соблюдена: hidden profile update-by-exercise; не объединяется с новыми аккаунтными и платёжными задачами. Pass.
- Открытых `NEEDS CLARIFICATION` в spec нет. Pass.

### Post-design

После Phase 1 артефакты сохраняют ту же границу: отдельная hidden-модель профиля, внутренний контракт обновления по результату хода, и проверка, что visible-flow не влияет на hidden-статусы.

## Project Structure

### Documentation (this feature)

```text
specs/005-hidden-profile-update/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── hidden-profile-update.md
└── tasks.md              # /speckit-tasks, этим шагом не создаётся
```

### Source Code (repository root)
```text
app/
├── run_flow.py               # финализация хода и точка вызова profile update
├── person.py                 # операции чтения/записи hidden profile и merge-правила
├── schema.sql                # hidden profile tables и ограничения
├── summary.py                # текущая сводка хода как вход для profile update
└── telegram_poll.py          # route safety: visible profile flow не трогает hidden status

tests/
├── test_hidden_profile_update.py
├── test_run_flow.py
└── test_account_settings_state.py
```

**Structure Decision**: используем существующий single-process layout. Логику обновления hidden-профиля добавляем в текущий контур завершения хода (`run_flow`) и слой профиля (`person`), с персистенцией в Postgres и тестами в `tests/`.

## Complexity Tracking

Нарушений конституции, требующих отдельного обоснования, нет.
