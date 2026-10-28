# Карта фич / бэклог срезов

Один реестр для работы на ПК и для Cloud Agent.  
Статусы: `draft` → `ready-for-speckit` → `specified` → `planned` → `in-impl` → `done` | `parked`.

Перед запуском Spec Kit с телефона: статус `ready-for-speckit` (или дальше), пути заполнены, изменения **запушены** на GitHub.

| id | Срез | Бизнес-постановка | Spec Kit | Статус | Примечание |
|----|------|-------------------|----------|--------|------------|
| F-001 | telegram-author-news-loop | `features/business-idea-from-news/` (FeatureLC / FeatureArtifacts) | `specs/001-telegram-author-news-loop/` | done | Учебный/первый контур TG |
| F-002 | telegram-model-switch | `ProductArtifacts/model-switch-slice.md` | `specs/002-telegram-model-switch/` | in-impl | Ветка `002-telegram-model-switch`; довести и закрыть отдельно от нового флоу |
| F-NEXT | *(следующая фича)* | *(путь к постановке)* | — | draft | Заполнить, когда постановка готова |

## Как пользоваться

1. На ПК проработала бизнес → файл постановки в `features/…` или `ProductArtifacts/`.
2. Добавь/обнови строку здесь, статус `ready-for-speckit`, commit + push.
3. Spec Kit (ПК или телефон): укажи **id** и пути из этой таблицы.
4. После specify/plan/tasks/implement — обнови статус и путь `specs/…`.
