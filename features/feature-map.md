# Карта фич

Фича — верхний уровень. Внутри неё истории. Спека режется из истории, не из фичи целиком.

Статусы: `draft` → `ready-for-speckit` → `specified` → `planned` → `in-impl` → `done` | `parked`.

Бизнес-логика фичи лежит в её папке и из неё нарезаются истории.

## Бизнес-идея из новости

Папка: `features/business-idea-from-news/`  
Бизнес-логика: `features/business-idea-from-news/FeatureLC/04 Solution Validation/08 Business Logic Design/business-logic.md`  
Статус фичи: `in-impl`. Истории текущего бота сделаны. Остальные истории этой фичи ждут мобильное приложение.

| История | Спека | Статус |
|---|---|---|
| Начать разбор со своей формулировки | `specs/001-telegram-author-news-loop/` | done |
| Вести ход по скиллу: вопрос, слабый ответ не пускает, финал | `specs/001-telegram-author-news-loop/` | done |
| Вернуться в незаконченный ход из списка | `specs/001-telegram-author-news-loop/` | done |
| Записать сводку этого хода | `specs/001-telegram-author-news-loop/` | done |
| Повтор той же реплики из Telegram не двигает шаг | `specs/001-telegram-author-news-loop/` | done |
| Открыть прошлый разбор: сводка и диалог | — | parked |
| Разобрать ту же тему ещё раз отдельной записью | — | parked |
| Удалить один разбор | — | parked |

Выбор модели и профиль навыка в эту фичу не входят. Они в «Настройке аккаунта».

## Настройка аккаунта

Папка: `features/account-settings/`  
Бизнес-логика: `features/account-settings/business-logic.md`  
Статус фичи: `ready-for-speckit`

| История | Спека | Статус |
|---|---|---|
| Выбрать модель | `specs/002-telegram-model-switch/` | in-impl |
| Открыть настройки с клавиатуры разбора | `ProductArtifacts/skill-profile-slice.md` | ready-for-speckit |
| Прочитать, изменить и добавить информацию о себе | `ProductArtifacts/skill-profile-slice.md` | ready-for-speckit |
| Обновлять скрытый файл профиля по результату задания | `ProductArtifacts/skill-profile-slice.md` | ready-for-speckit |

Истории без папки `specs/` ещё не прошли `/speckit-specify`. Их общая граница — `ProductArtifacts/skill-profile-slice.md`.

## Подключение платных моделей

Папка ещё не создана.  
Статус фичи: `draft`. Историй нет. Место входа — те же настройки аккаунта, отдельной фичей и позже.

## Расшифровка голосовых сообщений

Папка ещё не создана.  
Статус фичи: `draft`. Историй нет. Пока только в бэклоге.
