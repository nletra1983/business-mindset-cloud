# nginx + Let's Encrypt для `/app/` на Selectel

Делает **человек на сервере** (агент по конституции на Selectel по SSH не заходит).  
Порт приложения в Docker остаётся `127.0.0.1:8080`.

## Перед nginx

На сервере:

```bash
cd DEST   # /opt/business-mindset
docker compose ps
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8080/app/v1/runs
```

Ожидание: контейнер bot Up; код **401** (без сессии) — норма.

## Установка

```bash
apt update
apt install -y nginx certbot python3-certbot-nginx
```

## Firewall / панель Selectel

Открыть входящие: **22**, **80**, **443**.  
**Не** открывать **8080** с интернета.

```bash
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
```

## Конфиг nginx

Файл: `/etc/nginx/sites-available/APP` (имя на выбор).

Подставить `DOMAIN`:

```nginx
server {
    listen 80;
    server_name DOMAIN;

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
ln -sf /etc/nginx/sites-available/APP /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

## Сертификат

DNS A уже должен указывать на сервер.

```bash
certbot --nginx -d DOMAIN
```

## Проверка с домашнего ПК

```powershell
curl.exe -i https://DOMAIN/app/v1/runs
# 401 — ок

curl.exe -m 5 http://SERVER_IP:8080/app/v1/runs
# не должно открыться
```

## Частые ошибки

| Симптом | Что проверить |
|---------|----------------|
| certbot failed | DNS ещё не на SERVER_IP; закрыт порт 80 |
| 502 Bad Gateway | bot не слушает 8080; `docker compose ps` |
| 404 на /app/v1 | опечатка в `proxy_pass` или старый образ без channel API |
