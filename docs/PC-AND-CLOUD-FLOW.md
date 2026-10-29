# Флоу: бизнес на ПК → Spec Kit на ПК или с телефона

Репозиторий один: этот (`Business_mindset`). GitHub — зеркало и вход для Cloud Agent.

## Скрипты Spec Kit

Канон: **bash** (`.specify/scripts/bash/`, `init-options.json` → `"script": "sh"`).  
На Windows агент вызывает их через Git Bash. На Cloud (Linux) — системный bash. PowerShell-скрипты могут остаться в репо, skills на них не опираются.

## На ПК (бизнес-логика)

1. Открыть этот проект в Cursor.
2. Новая фича: `/po-new-feature` и описание своими словами. Агент пишет `features/<фича>/business-logic.md`, строку в [features/feature-map.md](../features/feature-map.md) и при необходимости зовёт `/arch-new-feature`, затем `/po-new-story`. Пока есть `NEEDS CLARIFICATION` или невыбранный `ARH-CHANGE`, к Spec Kit не переходить.
3. Граница истории для спеки лежит в папке фичи. Карта хранит фичу, её истории и статус каждой.
4. После бизнес-уточнений: `/check-ready-to-speckit` и название фичи или историй. Проверка идёт по файлам; ответы из чата сначала дописываются в артефакты. Успех пишет `ready-for-speckit` и `speckit-ready-stamp.json` (отпечатки границ). Правка этих файлов снова сбрасывает готовность в `draft`.
5. `git add` / `commit` / `push`.
6. `/speckit-specify` … — если штамп протух или его нет, сначала сам прогоняет `/check-ready-to-speckit`; пока красное, спеку не пишет.

Контекст «что уже сделано»: `features/feature-map.md`, `specs/`, `app/`.

## С телефона (Cloud Agent)

1. [cursor.com/agents](https://cursor.com/agents) или приложение Cursor iOS.
2. Репозиторий = этот на GitHub, ветка актуальная (часто `main` или рабочая).
3. Новую фичу начать так: `/po-new-feature` и описание своими словами. Когда карта показывает `ready-for-speckit`, первое сообщение Spec Kit — команда и название фичи. Пути, истории и оговорки агент берёт из конституции. Например:

```text
/speckit-specify
Настройка аккаунта
```

Дальше по очереди: `/speckit-plan` → `/speckit-tasks` → `/speckit-implement` (с паузами на твои ответы). К каждой команде достаточно того же названия фичи.

4. Когда фича готова к проверке в боте, влить её ветку в `main`. GitHub сам заходит на сервер и пересобирает бота. Агент на сервер не заходит. Секреты и база при этом не копируются.

## Что должно быть на GitHub до Cloud

- постановка по пути из feature-map;
- строка со статусом `ready-for-speckit` или дальше;
- `.cursor/skills/speckit-*` и `.specify/` (уже в репо);
- незапушенные файлы с `D:\` Cloud **не** видит.
