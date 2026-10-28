# Implementation Plan: Переключение модели в разборе

**Branch**: `002-telegram-model-switch` | **Date**: 2026-10-28 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/002-telegram-model-switch/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

Человек кнопкой с именем текущей модели выбирает одну из трёх уже подключённых моделей. Следующий вызов и оценка ответа идут этой моделью. Выбор помнится за человеком. Если выбранная модель не ответила и после одного повтора, разбор не завершается: человеку сказано, что модель недоступна, и в том же сообщении снова три кнопки. Если раньше отвечала другая модель, текущей становится она.

Технический контур не меняется: один процесс Python, Postgres, Selectel, Telegram через `TELEGRAM_API_BASE`. DeepSeek остаётся прежним вызовом. GigaChat и GLM вызываются их официальными HTTP-адресами через тот же `httpx`. Текущая модель — зелёная кнопка.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: `httpx`, `psycopg` (v3, binary). Отдельный SDK GigaChat или Z.ai не добавляется.

**Storage**: Postgres уже рабочего контура. На человека добавляются текущая модель и последняя ответившая модель.

**Testing**: `pytest` для выбора, отметки кнопки и отката после двух неудач, без живого Telegram. Сквозная проверка — `quickstart.md`.

**Target Platform**: тот же контейнер `bot` на Selectel, каталог `/opt/business-mindset`.

**Project Type**: один серверный процесс, диалог в Telegram.

**Performance Goals**: спека отдельный показатель не задаёт. Этот срез новый показатель не вводит.

**Constraints**: стек и облако не перевыбираются. Клиент провайдера не вызывает. Один повтор того же вызова. Статуса «пауза» нет. Уже принятые ответы не переписываются. Значения ключей не попадают в git, спеку и чат. Режим доступа остаётся `service_free`.

**Scale/Scope**: три модели в одном списке. Масштаб контура — порядок сотен пользователей, один человек собирает продукт.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Один процесс. Отдельный сервис моделей не добавляется. Pass.
- Канал не владеет ходом. Кнопка только меняет, какая модель сделает следующий вызов. Pass.
- Записи остаются в текущем контуре Selectel / Postgres. Вызов DeepSeek, GigaChat и GLM — вызов модели с сервера, не новое хранилище диалога. Pass.
- Оценку делает та же модель, которую человек выбрал для этого вызова. Pass.
- Скилл и его версия этим срезом не меняются. Pass.
- Стек не перевыбирается: Python 3.12, Postgres, Selectel, `TELEGRAM_API_BASE`. Pass.
- Код остаётся в `app/` этого репозитория. Pass.
- Telegram user id остаётся привязкой. Выбор модели пишется на внутреннего человека. Pass.
- Сводка и транскрипт не сливаются. Этот срез их не трогает. Pass.
- Три способа доступа не ломаются: в ходе по-прежнему `service_free`. `user_key` и `service_paid` не реализуются. Pass.
- Повтор того же update id не двигает шаг и не меняет модель второй раз. Берётся уже существующая запись `processed_telegram_update`. Pass.
- Протоколы GigaChat и GLM и зелёная кнопка закрыты ответом человека 2026-10-28, не догадкой. Открытых NEEDS CLARIFICATION нет. Pass.

### Post-design

Гейты выше не изменились. `data-model.md` добавляет два поля человеку и не добавляет сервис, шлюз и статус «пауза». Контракт описывает кнопки и три вызова. Scope GigaChat пока `GIGACHAT_API_PERS`; смена доступа — отдельное решение, не этот срез.

## Project Structure

### Documentation (this feature)

```text
specs/002-telegram-model-switch/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── telegram-model-switch.md
└── tasks.md              # /speckit-tasks, этим шагом не создаётся
```

### Source Code (repository root)

```text
app/                    # тот же пакет; вызов модели и клавиатура хода
specs/002-telegram-model-switch/
tests/                  # проверки выбора и отката без живого Telegram
# На сервере: тот же сервис bot. В контейнер дополнительно читаются
# secrets/sber.env и secrets/zai.env. Второй процесс не поднимается.
```

**Structure Decision**: пакет `app/` репозитория `D:\Business_mindset`, один процесс на `/opt/business-mindset`.

## Complexity Tracking

Нарушений конституции, которые нужно оправдывать, нет.
