# Research: Переключение модели в разборе

Решения ниже взяты из спеки этого среза, конституции 1.1.0, уже работающего контура и ответов человека 2026-10-28. Стек заново не выбирался. Открытых NEEDS CLARIFICATION нет.

## Язык и процесс

- Decision: Python 3.12, один процесс, каталог `app/`, сервис `bot` в уже существующем `docker-compose`.
- Rationale: конституция фиксирует рабочий контур автора. Образ `python:3.12-slim` уже используется.
- Alternatives considered: не рассматривались.

## Библиотеки

- Decision: HTTP — `httpx`. Postgres — `psycopg` v3 binary. Проверка логики — `pytest`.
- Rationale: так уже собран рабочий бот. Новая библиотека не нужна для DeepSeek и для кнопок Telegram.
- Alternatives considered: отдельные SDK GigaChat и Z.ai — не нужны, оба вызова выражаются через `httpx`.

## Telegram

- Decision: long poll `getUpdates` через `TELEGRAM_API_BASE`. Клавиатура — inline-кнопки, как у «к другим вопросам».
- Rationale: прямой Bot API с Selectel недоступен. Отдельной команды и ввода имени спека запрещает.
- Alternatives considered: команда `/model` и ответ текстом — запрещены спекой.

## Три модели, которые уже названы

- Decision: DeepSeek, запрос `deepseek-chat`, ключ `DEEPSEEK_API_KEY` в `secrets/deepseek.env`. GigaChat, запрос `GigaChat-2`, переменная `GIGACHAT_AUTH_KEY` в `secrets/sber.env`. GLM, запрос `glm-5.3-flash`, переменная `ZAI_API_KEY` в `secrets/zai.env`. Значения ключей сюда не входят.
- Rationale: имена запроса названы в спеке. Имена переменных прочитаны из файлов на сервере, без значений. Файлы `sber.env` и `zai.env` на сервере уже есть; в `docker-compose` сервиса `bot` их ещё нет, их нужно передать в тот же контейнер.
- Alternatives considered: другие id DeepSeek, включая `deepseek-flash` из пробы 2026-10-22, — не используются. Рабочий контур ходит в `deepseek-chat`.

## Вызов DeepSeek

- Decision: тот же вызов, что уже в контуре: `https://api.deepseek.com/chat/completions`, модель `deepseek-chat`. В ход писать запрошенный id и `model_returned` из ответа, если он есть.
- Rationale: успешный вызов с хоста 2026-10-23 и текущий `app/deepseek.py`.
- Alternatives considered: не рассматривались.

## Вызов GigaChat

- Decision: официальный вызов для физлица. `POST https://ngw.devices.sberbank.ru:9443/api/v2/oauth` с `Authorization: Basic` и ключом `GIGACHAT_AUTH_KEY`, заголовок `RqUID` — новый uuid, тело `scope=GIGACHAT_API_PERS`. Затем `POST https://api.giga.chat/v1/chat/completions` с `Authorization: Bearer` и полученным токеном, модель `GigaChat-2`. Токен человеку не показывается и в Postgres не пишется. Проверка TLS не отключается.
- Rationale: человек 2026-10-28 назвал доступ физлица и сказал, что позже его сменят. Адреса взяты из документации GigaChat, не из нового выбора стека.
- Alternatives considered: `GIGACHAT_API_B2B` и `GIGACHAT_API_CORP` — отложены до явной смены. Прежний хост `gigachat.devices.sberbank.ru` — не для нового подключения.

## Вызов GLM

- Decision: `POST https://api.z.ai/api/paas/v4/chat/completions`, заголовок `Authorization: Bearer` и ключ `ZAI_API_KEY`, модель `glm-5.3-flash`.
- Rationale: человек 2026-10-28 подтвердил GLM. Адрес — общий endpoint Z.ai из документации провайдера.
- Alternatives considered: отдельный coding-endpoint Z.ai — спека его не называет.

## Что считается ответившей моделью

- Decision: последняя ответившая модель — та из трёх запрошенных id, чей вызов вернул текст. Подставлять при сбое нужно её, а не сырое имя из поля ответа провайдера, если оно отличается.
- Rationale: спека говорит о трёх моделях, которые видит человек, и о предыдущей, которая уже отвечала.
- Alternatives considered: хранить только `model_returned` провайдера — человек тогда может не совпасть с кнопкой.

## Отметка текущей кнопки

- Decision: у текущей модели стиль кнопки `success` (зелёная). У двух остальных стиль не задаётся. Текст кнопок остаётся DeepSeek, GigaChat, GLM. Жирный шрифт на кнопке Telegram не применяется: разметка действует на текст сообщения, не на подпись кнопки.
- Rationale: человек 2026-10-28 попросил зелёную кнопку активной модели. Отдельная фраза с именем по спеке не требуется.
- Alternatives considered: синий `primary` и красный `danger` — не выбраны. Знак в тексте кнопки не нужен.
- Поправка 2026-10-28 после проверки в Telegram: кнопка, которая открывает этот список, подписана именем текущей модели (DeepSeek, GigaChat или GLM), а не словом «модель». Пока человек не выбирал, подпись DeepSeek. После нажатия имени то же сообщение становится «Модель изменена.» без кнопок. Список повторно не показывается.

## Пока человек не выбирал

- Decision: текущая модель `deepseek-chat`.
- Rationale: FR-009 и рабочий контур.
- Alternatives considered: пустой выбор до первого нажатия — спека это запрещает.

## Доступ

- Decision: `service_free`. `user_key` и `service_paid` в схеме хода остаются зарезервированными и в этом срезе не включаются.
- Rationale: спека и конституция.
- Alternatives considered: не рассматривались.
