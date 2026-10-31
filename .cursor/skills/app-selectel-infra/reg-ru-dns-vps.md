# reg.ru DNS → Selectel VPS (не GitHub Pages)

## Путь в кабинете

1. https://www.reg.ru/ → Войти  
2. **Мои домены** → нужный домен  
3. **DNS-серверы и управление зоной**  
4. Серверы: **`ns1.reg.ru`**, **`ns2.reg.ru`**  
5. **Ресурсные записи**

## Что сделать

1. Удалить **парковочные** A `@` на IP reg.ru (если есть).  
2. **Не** ставить A на `185.199.108–111.153` (это GitHub Pages).  
3. Добавить:

| Тип | Subdomain | Значение |
|-----|-----------|----------|
| A | `@` | `SERVER_IP` (для Business Mindset сейчас `176.53.234.161`) |
| CNAME | `www` | `DOMAIN` (имя домена без `https://`) |

Либо второй A: subdomain `www`, тот же `SERVER_IP`.

4. Сохранить. Подождать 5–60 мин (иногда до 24 ч).

## Проверка с ПК

```powershell
ipconfig /flushdns
nslookup DOMAIN 8.8.8.8
nslookup www.DOMAIN 8.8.8.8
```

В ответе должен быть **IP сервера**, не GitHub и не парковка reg.ru.

## Чужой кабинет

Сначала частичное управление — как в личном скилле `static-site-github-pages` → `domain-access.md`. Пароль чужого кабинета не просить.

## Ссылки

- [reg.ru: ресурсные записи](https://help.reg.ru/support/dns-servery-i-nastroyka-zony/nastroyka-resursnykh-zapisey-dns/nastroyka-resursnykh-zapisey-v-lichnom-kabinete)
