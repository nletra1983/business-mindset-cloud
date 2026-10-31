# Инструкция: инфра приложения (заполнить плейсхолдеры)

Агент подставляет: `DOMAIN`, `SERVER_IP`, `GITHUB_USER`, `REPO`, `DEST`, `CHANNEL_BASE_URL`.

## 1. Domains (reg.ru)

1. Войти в reg.ru → домен **`DOMAIN`**.
2. DNS-серверы: `ns1.reg.ru`, `ns2.reg.ru`.
3. Удалить парковочные A.
4. Добавить A `@` → **`SERVER_IP`**.
5. Добавить CNAME `www` → **`DOMAIN`** (или A `www` → тот же IP).
6. Подождать пропагации. Проверка: `nslookup DOMAIN 8.8.8.8` → `SERVER_IP`.

## 2. Сервер (Selectel) — вы сами по SSH

```bash
ssh root@SERVER_IP
cd DEST
docker compose ps
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8080/app/v1/runs
```

Дальше nginx + certbot по файлу скилла `nginx-https.md` для домена **`DOMAIN`**.

Firewall: 22, 80, 443 открыты; **8080 снаружи закрыт**.

## 3. GitHub

- Репо: `https://github.com/GITHUB_USER/REPO`
- Secret **`DEPLOY_SSH_KEY`** задан
- После merge в `main` — зелёный Deploy в Actions

## 4. Проверки с ПК

```powershell
nslookup DOMAIN 8.8.8.8
curl.exe -i https://DOMAIN/app/v1/runs
curl.exe -m 5 http://SERVER_IP:8080/app/v1/runs
```

Ожидание: DNS = сервер; https → 401; :8080 снаружи недоступен.

## 5. APK

```powershell
$env:CHANNEL_BASE_URL = "CHANNEL_BASE_URL"
powershell -File mobile\tool\build_author_apk.ps1
```

Поставить `app-release.apk` на телефон поверх предыдущей версии.

## Частые ошибки

- A-записи как у GitHub Pages → сайт/API не на вашем VPS  
- Открыли 8080 в интернет → не наш безопасный вариант  
- APK со старым `127.0.0.1` → код «не приходит»  
- certbot до пропагации DNS → ошибка выпуска сертификата  
- На сервере нет свежего `main` → нет `/app/v1` (смотреть Actions)
