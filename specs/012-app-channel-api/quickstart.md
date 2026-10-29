# Quickstart: вход каналов `/app/v1`

Живой Selectel и TLS-край в этой проверке не трогаем. Смотрим обработчики.

```text
py -3.12 -m pytest tests/test_channel_api.py tests/test_email_entrances.py tests/test_app_email_entry.py
```

## Что должно пройти

1. Запрос кода и верный код выдают секрет. Неверный код — нет.
2. С секретом доступен список ходов; без секрета — отказ.
3. Повтор того же `Idempotency-Key` на ответ не двигает шаг второй раз.
4. Путь контракта — `/app/v1`, не long poll Telegram.
5. Письмо по-прежнему только с кодом.
