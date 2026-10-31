# Inventory инфры (без секретов)

Заполняет агент вместе с человеком. Значения секретов сюда не писать.

| Поле | Значение |
|------|----------|
| DOMAIN | get-business-idea.ru |
| SERVER_IP | 176.53.234.161 |
| SSH_HOST | root@176.53.234.161 |
| GITHUB_USER | nletra1983 |
| REPO | business-mindset-cloud |
| DEST | /opt/business-mindset |
| APP_PATH | /app/ |
| CHANNEL_BASE_URL | https://get-business-idea.ru |
| DNS registrar | reg.ru |
| TLS | nginx + Let's Encrypt на VPS |
| Deploy | GitHub Actions → main → deploy script |
| Notes | Один Selectel VPS на тестовые проекты; новый продукт → новый DOMAIN и/или REPO; 8080 только localhost |
