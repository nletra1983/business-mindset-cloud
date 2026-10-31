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
Статус фичи: `done`. Граница истории — эта бизнес-логика.

| История | Спека | Статус |
|---|---|---|
| Голосовое становится текстом и обрабатывается как набранное сообщение | `specs/006-voice-message-transcription/` | done |

## Мобильное приложение

Папка: `features/mobile-app/`  
Бизнес-логика: `features/mobile-app/business-logic.md`  
Статус фичи: `in-impl`. Архитектура принята: ADL-018, ADL-019, ADL-020. Вход — email, клиент — Flutter, первая поставка — APK автору.  
Колонка «№» — номер истории в этой фиче. Колонка «Спека» — папка Spec Kit или файл границы; числа вроде `007` — имя папки спеки, не номер истории.  
№2–№4 оставлены отдельными: их не сворачивать в №1 и №5. Отправитель кода на тест — личный `yandex.ru`, секреты в `secrets/mail.env`. `/check-ready-to-speckit` 2026-10-29: №2–№4 → `ready-for-speckit`, штамп `features/mobile-app/speckit-ready-stamp.json`. №9 parked. №10 — бэклог: границу не готовим, Spec Kit не берём, пока человек не вернёт.

| № | История | Спека / граница | Статус |
|---|---|---|---|
| 1 | Внедрить вход по email и необязательный Telegram в уже работающий аккаунт | `specs/007-email-account-entry/` | in-impl |
| 2 | Открыть защищённый вход модуля каналов для приложения | `specs/012-app-channel-api/` | in-impl |
| 3 | Держать сессию входа на устройстве и дать явный выход | `specs/013-app-session/` | in-impl |
| 4 | Собрать Flutter-клиент и отдать автору подписанный APK | `specs/014-app-apk-delivery/` | in-impl |
| 5 | Войти в приложение по email и работать без Telegram | `specs/008-app-email-entry/` | in-impl |
| 6 | В настройках указать второй вход, подтвердить его кодом и слить ходы | `specs/009-link-second-entrance/` | done |
| 7 | Начать разбор новости в приложении и вернуться в незаконченный | `specs/010-app-news-run/` | done |
| 8 | Открыть настройки того же входа: модель и информация о себе | `specs/011-app-settings/` | done |
| 9 | Войти по номеру телефона и коду из SMS | `specs/006-phone-account-entry/` | parked |
| 10 | Научить скилл объединять текст профиля при слиянии | — | parked |
