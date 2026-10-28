# Флоу: бизнес на ПК → Spec Kit на ПК или с телефона

Репозиторий один: этот (`Business_mindset`). GitHub — зеркало и вход для Cloud Agent.

## Скрипты Spec Kit

Канон: **bash** (`.specify/scripts/bash/`, `init-options.json` → `"script": "sh"`).  
На Windows агент вызывает их через Git Bash. На Cloud (Linux) — системный bash. PowerShell-скрипты могут остаться в репо, skills на них не опираются.

## На ПК (бизнес-логика)

1. Открыть этот проект в Cursor.
2. Писать бизнес-логику фичи в `features/<фича>/business-logic.md`. Из неё нарезаются истории. Граница истории для спеки может лежать в ProductArtifacts.
3. Обновить [features/feature-map.md](../features/feature-map.md): фича, её истории, статус каждой.
4. `git add` / `commit` / `push`.
5. При необходимости локально: `/speckit-specify` … (или сразу с телефона).

Контекст «что уже сделано»: `features/feature-map.md`, `specs/`, `app/`.

## С телефона (Cloud Agent)

1. [cursor.com/agents](https://cursor.com/agents) или приложение Cursor iOS.
2. Репозиторий = этот на GitHub, ветка актуальная (часто `main` или рабочая).
3. Первое сообщение — команда и название фичи из карты. Пути, истории и оговорки агент берёт из конституции. Например:

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
