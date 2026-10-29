# Карта фич

Фича — верхний уровень. Внутри неё истории. Спека режется из истории, не из фичи целиком.

Статусы: `draft` → `ready-for-speckit` → `specified` → `planned` → `in-impl` → `done` | `parked`.

Бизнес-логика фичи лежит в её папке и из неё нарезаются истории.

## Бизнес-идея из новости

Папка: `features/business-idea-from-news/`  
Бизнес-логика: `features/business-idea-from-news/FeatureLC/04 Solution Validation/08 Business Logic Design/business-logic.md`  
Статус фичи: `in-impl`. Истории текущего бота сделаны. Карточка прошлого разбора, повтор темы и удаление разбора остаются в этой фиче и стартуют отдельно, когда мобильное приложение уже есть.

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
Статус фичи: `in-impl`

| История | Спека | Статус |
|---|---|---|
| Выбрать модель | `specs/002-telegram-model-switch/` | done |
| Открыть настройки с клавиатуры разбора | `specs/003-open-settings-from-keyboard/` | done |
| Прочитать, изменить и добавить информацию о себе | `specs/004-self-info-profile/` | done |
| Обновлять скрытый файл профиля по результату задания | `specs/005-hidden-profile-update/` | done |

Истории без папки `specs/` ещё не прошли `/speckit-specify`. Их общая граница — `ProductArtifacts/skill-profile-slice.md`.

## Подключение платных моделей

Папка ещё не создана.  
Статус фичи: `draft`. Историй нет. Место входа — те же настройки аккаунта, отдельной фичей и позже.

## Расшифровка голосовых сообщений

Папка: `features/voice-messages/`  
Бизнес-логика: `features/voice-messages/business-logic.md`  
Статус фичи: `ready-for-speckit`. Граница истории — эта бизнес-логика.

| История | Спека | Статус |
|---|---|---|
| Голосовое становится текстом и обрабатывается как набранное сообщение | — | ready-for-speckit |

## Мобильное приложение

Папка: `features/mobile-app/`  
Бизнес-логика: `features/mobile-app/business-logic.md`  
Статус фичи: `ready-for-speckit`. Архитектура принята: ADL-018, уточнение ADL-019. Вход в приложение — email. Номер телефона в бэклоге. В Spec Kit уходит одна история за раз, первой — внедрение email в аккаунт. Она блокирует реализацию остальных. Чужую границу в спеку не брать.

| История | Спека | Статус |
|---|---|---|
| Внедрить вход по email и необязательный Telegram в уже работающий аккаунт | `specs/007-email-account-entry/` | in-impl |
| Войти в приложение по email и работать без Telegram | `features/mobile-app/app-email-entry.md` | ready-for-speckit |
| В настройках указать второй вход, подтвердить его кодом и слить ходы | `features/mobile-app/link-second-entrance.md` | ready-for-speckit |
| Начать разбор новости в приложении и вернуться в незаконченный | `features/mobile-app/app-news-run.md` | ready-for-speckit |
| Открыть настройки того же входа: модель и информация о себе | `features/mobile-app/app-settings.md` | ready-for-speckit |
| Войти по номеру телефона и коду из SMS | `specs/006-phone-account-entry/` | parked |
| Научить скилл объединять текст профиля при слиянии | — | draft |
