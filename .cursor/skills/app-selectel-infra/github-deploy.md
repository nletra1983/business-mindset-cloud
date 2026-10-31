# GitHub репозиторий и деплой на Selectel

## Репозиторий

- Владелец: `GITHUB_USER` (для этого продукта обычно `nletra1983`)
- Имя: `REPO` (сейчас `business-mindset-cloud`)
- Remote: `https://github.com/GITHUB_USER/REPO.git`
- Рабочая ветка деплоя: **`main`**
- Новый продукт → новый репо в том же пространстве; сервер пока может быть тот же VPS с другим `DEST`

Репозиторий **может быть private** (в отличие от бесплатного GitHub Pages).

## Deploy Action

В репо уже есть (или копируется) workflow: push в `main` → SSH → `/usr/local/sbin/deploy-business-mindset` (или аналог).

Нужен секрет Actions:

- Имя: **`DEPLOY_SSH_KEY`**
- Значение: приватный ключ деплоя (в чат и в git не писать)

Путь в GitHub: **Settings → Secrets and variables → Actions → New repository secret**.

## Что на сервере уже должно быть (человек)

- Каталог `DEST` с `secrets/` и `data/postgres/`
- Скрипт деплоя установлен (как в `deploy/update-bot.sh`)
- Docker + compose
- Публичный ключ деплоя в `authorized_keys` у пользователя SSH

Агент **не** заходит на сервер и не кладёт секреты.

## Push в main

Только по явной просьбе человека («запушь в main»). После push проверить вкладку Actions: workflow Deploy bot зелёный.

## Не путать

| Статический сайт (Pages) | Это приложение |
|--------------------------|----------------|
| Public repo обязателен для бесплатного Pages | Private ок |
| Custom domain + Enforce HTTPS в Pages | HTTPS на nginx VPS |
| A → 185.199.* | A → SERVER_IP |
