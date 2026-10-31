# Инфра: get-business-idea.ru → Selectel

Заполнено по скиллу `app-selectel-infra`. Секреты сюда не входят.

| Поле | Значение |
|------|----------|
| DOMAIN | `get-business-idea.ru` |
| SERVER_IP | `176.53.234.161` |
| DEST | `/opt/business-mindset` |
| CHANNEL_BASE_URL | `https://get-business-idea.ru` |
| GitHub | `nletra1983/business-mindset-cloud` |

## 1. DNS на reg.ru

1. Войти на https://www.reg.ru/ → **Мои домены** → `get-business-idea.ru`.
2. **DNS-серверы и управление зоной** → серверы `ns1.reg.ru`, `ns2.reg.ru`.
3. Удалить парковочные A `@` (IP reg.ru), если есть.
4. **Не** ставить A на `185.199.*` (это GitHub Pages).
5. Добавить:

| Тип | Subdomain | Значение |
|-----|-----------|----------|
| A | `@` | `176.53.234.161` |
| CNAME | `www` | `get-business-idea.ru` |

6. Сохранить. Подождать 5–60 мин.

Проверка с ПК:

```powershell
ipconfig /flushdns
nslookup get-business-idea.ru 8.8.8.8
nslookup www.get-business-idea.ru 8.8.8.8
```

В ответе должен быть `176.53.234.161`.

## 2. Сервер (SSH) — вы сами

```bash
ssh root@176.53.234.161
cd /opt/business-mindset
docker compose ps
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8080/app/v1/runs
```

Ожидание: bot Up; код `401` — норма (без сессии).

Установка nginx и certbot:

```bash
apt update
apt install -y nginx certbot python3-certbot-nginx
```

Firewall / панель Selectel: открыть **22, 80, 443**. **Не** открывать **8080**.

```bash
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
```

Файл `/etc/nginx/sites-available/business-mindset-app`:

```nginx
server {
    listen 80;
    server_name get-business-idea.ru;

    location /app/ {
        proxy_pass http://127.0.0.1:8080/app/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location / {
        return 404;
    }
}
```

```bash
ln -sf /etc/nginx/sites-available/business-mindset-app /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

Когда DNS уже указывает на сервер:

```bash
certbot --nginx -d get-business-idea.ru
```

(По желанию сразу и www: `certbot --nginx -d get-business-idea.ru -d www.get-business-idea.ru`.)

## 3. Проверки с ПК

```powershell
nslookup get-business-idea.ru 8.8.8.8
curl.exe -i https://get-business-idea.ru/app/v1/runs
curl.exe -m 5 http://176.53.234.161:8080/app/v1/runs
```

Ожидание: DNS = сервер; https → **401**; порт 8080 снаружи **не** открывается.

## 4. После успеха — написать агенту

«DNS и HTTPS готовы» — пересоберём APK с  
`CHANNEL_BASE_URL=https://get-business-idea.ru`  
и снова поставите файл на телефон.

## Частые ошибки

- A как у GitHub Pages → не ваш сервер  
- 8080 открыт снаружи → небезопасный вариант  
- certbot до пропагации DNS → ошибка сертификата  
- APK со старым `127.0.0.1` → код не приходит  
