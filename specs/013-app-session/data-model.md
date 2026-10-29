# Data model: сессия и выход

## App session (уже есть)

- person_id
- secret_hash
- created_at
- revoked_at — заполняется при logout

Действующая сессия: `revoked_at IS NULL`. После logout тот же секрет не принимается.

## Device session store (протокол)

- одно значение: session_secret или пусто
- put после успешного confirm
- get при открытии приложения
- clear при logout (после или вместе с вызовом отзыва на сервере)

Ключ провайдера модели в этом хранилище не появляется.
