# Data Model: Прочитать, изменить и добавить информацию о себе

История добавляет доменную модель user-visible профиля и фиксирует разделение с hidden-профилем. Ниже — логические сущности и ограничения.

## VisibleProfileDocument

Показывается пользователю и редактируется через `информация о себе`.

## Fields

- `person_id` — ссылка на внутренний id человека (обязательное поле).
- `strengths_text` — строка сильных сторон, задаётся человеком.
- `weaknesses_text` — строка слабых сторон, задаётся человеком.
- `self_facts` — список фактов о себе, сказанных человеком.
- `updated_at` — время последнего обновления видимого профиля.

## Constraints

- `person_id` уникален в visible-профиле (один профиль на человека).
- `strengths_text` при обновлении MUST содержать непустой текст после trim.
- `weaknesses_text` при обновлении MUST содержать непустой текст после trim.
- Каждый элемент `self_facts` MUST содержать непустой текст после trim.
- Пустой/пробельный ввод MUST NOT удалять ранее сохранённое валидное значение.

## HiddenEvaluatorProfileDocument

Не показывается пользователю, обновляется упражнением (не этой историей).

## Fields

- `person_id` — ссылка на внутренний id человека.
- `spotting_status`, `creativity_status`, `valuing_status`, `uncertainty_status`, `resources_status`, `learning_status` — статусы характеристик.
- `current_focus` — какая характеристика сейчас тренируется.
- `evidence_log` — список свидетельств (цитата/краткий пересказ, задание, ход, дата).
- `updated_at` — время последнего изменения hidden-профиля.

## Constraints

- Hidden-профиль не отдаётся в user-visible ответах этой истории.
- Прямые правки visible-профиля MUST NOT изменять поля статусов hidden-профиля.

## ProfileEditSession (interaction state)

Состояние шагов диалога редактирования в Telegram.

## Fields

- `person_id` — человек, который редактирует профиль.
- `step` — текущий шаг (`awaiting_strengths`, `awaiting_weaknesses`, `awaiting_extra_fact`, `idle`).
- `started_at` / `updated_at` — отметки времени сессии.

## Constraints

- Одновременно активна не более одной сессии редактирования на человека.
- Stale callback/message по сессии MUST NOT менять persisted profile данные.
