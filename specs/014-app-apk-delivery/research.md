# Research: APK автору

## Decision: каталог `mobile/` и package id `ru.businessmindset.app`

**Decision**: Один Flutter-проект в `mobile/`. Android `applicationId` / namespace — `ru.businessmindset.app`. Версия растёт в `pubspec.yaml`.

**Rationale**: Один идентификатор пакета для обновления поверх. Имя отражает продукт, не магазинный бренд.

**Alternatives considered**: `com.example.*`. Отклонено: не для release автору.

## Decision: ключ вне git, как `secrets/`

**Decision**: `mobile/android/key.properties` и `*.jks` / `*.keystore` в `.gitignore`. В репо — `key.properties.example` с именами полей. Автор кладёт keystore рядом с другими секретами или локально вне git.

**Rationale**: Граница и distribution.md. Потеря ключа = новое приложение.

**Alternatives considered**: Debug-подпись для «первого файла». Отклонено: обновление поверх требует стабильный release-ключ.

## Decision: тонкий каркас UI, сеть только `/app/v1`

**Decision**: Экран-заглушка «вход» + клиент к базовому URL каналов. Полный UI email/разбора — истории №5–№8.

**Rationale**: Граница явно отделяет файл установки от экранов входа.

## Decision: сборка на машине автора

**Decision**: Скрипт `mobile/tool/build_author_apk.ps1` запускает `flutter build apk --release`. Агент создаёт проект и проверки структуры; если Flutter SDK нет в PATH агента, готовый `.apk` появляется у автора после скрипта.

**Rationale**: На агенте Flutter может отсутствовать; продукт требует файл на диске автора.
