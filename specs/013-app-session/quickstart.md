# Quickstart: сессия и выход

```text
py -3.12 -m pytest tests/test_app_session.py tests/test_channel_api.py
```

## Ожидание

1. После confirm секрет в vault; повторный `/runs` без нового кода.
2. Logout отзывает сессию; старый Bearer — отказ.
3. После logout vault пуст.
4. Таймер сам не выкидывает.
