# Флоу: бизнес на ПК → Spec Kit на ПК или с телефона

Репозиторий один: этот (`Business_mindset`). GitHub — зеркало и вход для Cloud Agent.

## Скрипты Spec Kit

Канон: **bash** (`.specify/scripts/bash/`, `init-options.json` → `"script": "sh"`).  
На Windows агент вызывает их через Git Bash. На Cloud (Linux) — системный bash. PowerShell-скрипты могут остаться в репо, skills на них не опираются.

## На ПК (бизнес-логика)

1. Открыть этот проект в Cursor.
2. Писать постановку в FeatureLC / FeatureArtifacts / ProductArtifacts (как принято для фичи).
3. Обновить [features/feature-map.md](../features/feature-map.md): путь + статус `ready-for-speckit`.
4. `git add` / `commit` / `push`.
5. При необходимости локально: `/speckit-specify` … (или сразу с телефона).

Контекст «что уже сделано»: `features/feature-map.md`, `specs/`, `app/`.

## С телефона (Cloud Agent)

1. [cursor.com/agents](https://cursor.com/agents) или приложение Cursor iOS.
2. Репозиторий = этот на GitHub, ветка актуальная (часто `main` или рабочая).
3. Первое сообщение — явно команда и ссылки, например:

```text
/speckit-specify
Срез из feature-map: F-NEXT
Бизнес-постановка: <путь из таблицы>
Дыры не закрывать — спрашивай меня в этом чате.
В конце ответа: списки «Проверить» и «Не читать» (только новое / вопросы / вердикт).
```

Дальше по очереди: `/speckit-plan` → `/speckit-tasks` → `/speckit-implement` (с паузами на твои ответы).

4. На ПК: `git pull` (или принять PR) → обновить статус в feature-map.

## Что должно быть на GitHub до Cloud

- постановка по пути из feature-map;
- строка со статусом `ready-for-speckit` или дальше;
- `.cursor/skills/speckit-*` и `.specify/` (уже в репо);
- незапушенные файлы с `D:\` Cloud **не** видит.
