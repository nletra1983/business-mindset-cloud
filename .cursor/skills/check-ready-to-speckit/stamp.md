# Штамп готовности к Spec Kit

Файл: `features/<slug>/speckit-ready-stamp.json` (в git, не секрет).

## Зачем

Статус `ready-for-speckit` в карте — ярлык. Штамп держит **отпечаток** файлов на момент успешной `/check-ready-to-speckit`. Если после проверки границу или бизнес-логику поменяли (в том числе допиской из чата), отпечаток не совпадёт — проверку нужно пройти снова. Так не полагаемся на память чата и не гоняем проверку зря, пока файлы те же.

## Формат

```json
{
  "checked_at": "2026-10-29T11:15:00+03:00",
  "feature_files": {
    "business-logic.md": "<sha256 hex>",
    "arch-change.md": "<sha256 hex>"
  },
  "stories": [
    {
      "no": 2,
      "title": "Открыть защищённый вход модуля каналов для приложения",
      "boundary": "features/mobile-app/app-channel-api.md",
      "sha256": "<sha256 hex of boundary file utf-8>"
    }
  ]
}
```

- `feature_files` — только существующие файлы в папке фичи из списка: `business-logic.md`, `arch-change.md`.
- `boundary` — путь из карты. Если граница — раздел только в `business-logic.md`, `boundary` = путь к `business-logic.md`, а в `stories[].sha256` тот же хеш, что у `feature_files["business-logic.md"]`.
- Хеш — SHA-256 содержимого файла в UTF-8 без нормализации вне самого файла.

## Свежесть

Штамп **свеж** для истории, если:

1. в карте у неё `ready-for-speckit`;
2. запись есть в `stories`;
3. текущий sha256 файла границы совпадает;
4. текущие sha256 всех ключей в `feature_files` совпадают с файлами на диске.

Иначе штамп **протух** или отсутствует → нужна `/check-ready-to-speckit` по этой фиче/истории.

## Сброс при правке

Любая команда или правка, которая меняет `business-logic.md`, `arch-change.md` или файл границы истории со статусом `ready-for-speckit`:

1. Статус этой истории (для правки границы) или всех `ready-for-speckit` фичи (для правки `business-logic.md` / `arch-change.md`) вернуть в `draft` в `features/feature-map.md`.
2. Удалить соответствующие записи из штампа; если `stories` пуст — удалить файл штампа.

Не ждать следующей проверки: сброс в том же заходе, где правили артефакт.
