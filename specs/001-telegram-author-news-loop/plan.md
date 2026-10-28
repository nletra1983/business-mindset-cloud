# Implementation Plan: Короткий разбор автора в Telegram

**Branch**: `001-telegram-author-news-loop` | **Date**: 2026-10-23 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-telegram-author-news-loop/spec.md`

## Summary

Один Python-процесс заменяет эхо-бот на уже существующем контуре Selectel `/opt/business-mindset`. Процесс ведёт smoke-ход в Telegram, пишет человека, ход, транскрипт и сводку хода в уже существующий Postgres и вызывает DeepSeek с сервера. Второй бот-процесс не запускается. Детали стека — в [research.md](./research.md).

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: `httpx`, `psycopg` (v3); без тяжёлого bot-framework

**Storage**: Postgres, уже есть

**Testing**: `pytest` (логика хода; живой Telegram не обязателен в автотестах)

**Target Platform**: один контейнер Docker на Selectel, каталог `/opt/business-mindset`

**Project Type**: одно серверное приложение, бот Telegram

**Performance Goals**: числовые SLO не заданы. Час недоступности прерывает тренировку. Отдельного офлайн-хода нет. Повтор того же update id не сдвигает шаг.

**Constraints**: Telegram только через `TELEGRAM_API_BASE`, long poll `getUpdates`. Токен бота — `TG_GETBUSINESSIDEA_TOKEN`. Ключ DeepSeek — `DEEPSEEK_API_KEY` из `secrets/deepseek.env` (в контейнере под `/opt/business-mindset/secrets/`). Модель запроса `deepseek-chat`; человек в этом срезе модель не выбирает (единственная разрешённая). Оценка и диалог — одной моделью. Новый ход только из списка после кнопки «к другим вопросам». Отдельного статуса «пауза» нет. Возврат — клик по незавершённому ходу в списке. Эхо-бот этим приложением заменяется, второй бот-процесс не держится. Код в репозитории: `app/`.

**Scale/Scope**: один канал Telegram и один smoke-скилл `business-idea-from-news.smoke`. Порядок пользователей на год в спеке не задан.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Один процесс, без нового сервиса. Сотни пользователей и один smoke-скилл причиной делить процесс не являются. Pass.
- Канал среза — Telegram. Веб, мобильное приложение и Макс не проектируются. Канал ходом не владеет. Pass.
- Записи среза остаются в Postgres на Selectel. Снимок новости и профиль навыка в срез не входят и в план не добавляются. Pass.
- DeepSeek вызывает сервер. Отдельный шлюз данных для модели не вводится: в спеке DeepSeek уже проверен с хоста. Telegram идёт через заданный CF-прокси и диалоги там не хранит. Pass.
- Версия скилла `business-idea-from-news.smoke` пишется в ход. Pass.
- Облако, Postgres и прокси заново не выбираются. Pass.
- Код продукта — в этом репозитории. `specs/` не заменяет `features/` и `ProductLC/`. Pass.
- Внутренний идентификатор — ключ человека. Telegram user id только привязка. Сводка хода — отдельная запись от транскрипта. Pass.
- Агент не платит, не публикует и не пишет третьим лицам. Этих сценариев в плане нет. Pass.
- Повтор update id не сдвигает шаг. Час недоступности не стирает уже принятый ход. Pass.
- Конституция: оценка моделью «выбора человека». Срез: единственная разрешённая — DeepSeek (`service_free`); выбор UI не делается. Закрыто в research.md. Pass.
- Конституция: три способа доступа. В данных хода — поле режима, значение `service_free`; другие значения зарезервированы. Pass.
- Конституция запрещает считать пробу echo_bot конституцией стека. Python назван во входе plan; версия 3.12 совпала с уже использованным образом — зафиксировано в research, не как «закон пробы». См. Complexity Tracking.

### Post-design

Гейты выше не изменились. `data-model.md` не добавляет сервис, шлюз модели, профиль навыка и карточку истории. Незакрытые маркеры из Technical Context в `research.md` не подменены выбором библиотеки.

## Project Structure

### Documentation (this feature)

```text
specs/001-telegram-author-news-loop/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── telegram-dialogue.md
└── tasks.md              # /speckit-tasks, этим шагом не создаётся
```

### Source Code (repository root)

```text
app/                    # код приложения (деплой → /opt/business-mindset/app)
features/...            # скиллы, в т.ч. smoke
specs/001-...           # эта фича Spec Kit
# На сервере: один процесс bot в docker-compose, вместо echo.
```

**Structure Decision**: пакет в `app/` репозитория `D:\Business_mindset`, один процесс на `/opt/business-mindset`.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Python взят от пробы echo_bot, хотя конституция запрещает считать пробу конституцией стека | Человек в этом `/speckit-plan` назвал Python и запретил менять его без дыры в спеке | Новый язык этим вызовом запрещён; в архитектуре и конституции другого языка нет |
