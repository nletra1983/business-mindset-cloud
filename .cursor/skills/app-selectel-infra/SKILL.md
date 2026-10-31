---
name: app-selectel-infra
description: >-
  Настраивает инфру приложения на Selectel VPS: домен reg.ru (A на сервер),
  nginx + Let's Encrypt для /app/, GitHub repo/Actions deploy, CHANNEL_BASE_URL
  для Flutter APK. Use when the user says «настрой инфру», домен, DNS, nginx,
  HTTPS, Selectel, вход каналов, CHANNEL_BASE_URL, или готовит похожее
  приложение-бота с мобильным клиентом.
---

# Инфра приложения — Selectel + reg.ru + GitHub Deploy

Скилл для **бота/API на VPS** и мобильного клиента, который ходит в `/app/v1` по HTTPS.
Не путать со статическим сайтом на GitHub Pages (личный скилл `static-site-github-pages`) — там A-записи на IP GitHub; **здесь A-запись на IP Selectel**.

Не подставляй чужие домены и логины. Значения — только из чата или из [inventory.md](inventory.md) этого репо (если файл уже заполнен).

## Стек (по умолчанию)

| Что | Выбор | Зачем |
|-----|--------|--------|
| Сервер | **Selectel VPS** (один на тестовые проекты, пока так) | Бот + Postgres в Docker |
| Деплой | **GitHub Actions → SSH** на push в `main` | Агент на сервер по SSH не заходит |
| Домен | **reg.ru**, NS `ns1.reg.ru` / `ns2.reg.ru` | DNS в кабинете reg.ru |
| Публичный вход API | **nginx + certbot** на 443, путь `/app/` | TLS снаружи; `8080` только `127.0.0.1` |
| Клиент | Flutter APK, `CHANNEL_BASE_URL=https://DOMAIN` | Без открытого 8080 в интернет |

**Не делать по умолчанию:** публиковать `0.0.0.0:8080`; ставить A `@` на IP GitHub Pages; предлагать Netlify.

**Не делать агенту:** `ssh` на Selectel, читать/печатать значения из `secrets/*.env`.

## Переменные (спросить, если нет)

| Плейсхолдер | Смысл | Пример для этого репо |
|-------------|--------|------------------------|
| `DOMAIN` | Домен без `https://` и без `/` | *(спросить — новый на reg.ru)* |
| `SERVER_IP` | Публичный IPv4 VPS | `176.53.234.161` |
| `GITHUB_USER` | Владелец репо | `nletra1983` |
| `REPO` | Имя репозитория | `business-mindset-cloud` |
| `DEST` | Каталог на сервере | `/opt/business-mindset` |
| `APP_PATH` | Путь API за прокси | `/app/` |
| `CHANNEL_BASE_URL` | База для Flutter | `https://DOMAIN` (без `/app`) |
| `SSH_HOST` | Куда деплой | `root@SERVER_IP` |

Если пользователь говорит «как в Business Mindset» — бери известные значения из таблицы, **DOMAIN всё равно спроси**.

После первого заполнения предложи записать факты в [inventory.md](inventory.md) (без секретов).

## Порядок

```
0. Доступ к домену в reg.ru (свой кабинет / частичное управление)
1. Уточнить переменные; при необходимости создать/указать GitHub repo
2. DNS: A @ → SERVER_IP (и www → DOMAIN или A www → SERVER_IP)
3. На сервере (делает человек): бот слушает 127.0.0.1:8080; nginx /app/ → :8080; certbot
4. Firewall/панель: 22, 80, 443 открыты; 8080 снаружи закрыт
5. GitHub: Actions secret DEPLOY_SSH_KEY; workflow пушит main → deploy
6. Проверки: DNS, https://DOMAIN/app/v1/runs → 401, :8080 снаружи недоступен
7. Пересобрать APK с CHANNEL_BASE_URL; поставить поверх на телефон
```

Почта кода входа — отдельно (`secrets/mail.env` на сервере / SMTP). Платный ящик на домене reg.ru — по желанию, см. личный скилл static-site (почта), **не ломая** A на Selectel.

## Когда пользователь говорит «настрой инфру»

1. Прочитай этот файл и [inventory.md](inventory.md), если есть.
2. Уточни недостающие переменные (минимум `DOMAIN`; остальное — из таблицы или чата).
3. Заполни [DEPLOY-TEMPLATE.md](DEPLOY-TEMPLATE.md) → выведи по-русски пошаговую инструкцию (чат и/или `docs/INFRA-MANUAL.md` — спроси куда).
4. DNS-клики — [reg-ru-dns-vps.md](reg-ru-dns-vps.md). Nginx/certbot — [nginx-https.md](nginx-https.md). GitHub — [github-deploy.md](github-deploy.md).
5. Код/compose/workflow меняй в репо только с согласия; **push в main** — только по явной просьбе.
6. Когда человек напишет, что клики сделаны — проверь DNS/HTTPS командами ниже (с ПК агента, без SSH).

## Проверка (агент с ПК)

```powershell
nslookup DOMAIN 8.8.8.8
# должен быть SERVER_IP

curl.exe -i https://DOMAIN/app/v1/runs
# ожидаем 401 (нужна сессия) — вход жив

curl.exe -m 5 http://SERVER_IP:8080/app/v1/runs
# timeout / refused — хорошо (8080 не снаружи)
```

## APK после инфры

```powershell
$env:CHANNEL_BASE_URL = "https://DOMAIN"
. .\mobile\tool\setup_author_env.ps1
powershell -File mobile\tool\build_author_apk.ps1
```

Файл: `mobile/build/app/outputs/flutter-apk/app-release.apk`. Keystore не в git.

## Правила для агента

- Ответы пользователю — **русский**, по шагам как для человека без DevOps-опыта
- Не путать с GitHub Pages: **нет** четырёх A `185.199.*`
- Не открывать 8080 в интернет «для скорости»
- Не печатать пароли keystore, SMTP, SSH-ключей
- Плейсхолдеры в инструкции заменить реальными значениями; не оставлять `DOMAIN` как есть
