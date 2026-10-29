# Data model: поставка APK

Новых серверных сущностей нет.

## Client build identity

- **package id**: `ru.businessmindset.app` — стабилен между версиями
- **versionName / versionCode**: из `pubspec.yaml` / Android Gradle
- **signing key**: локальный keystore автора, не сущность git

## Session on device

Секрет сессии — по протоколу `013` (`device_session` / secure store). В этой истории только каркас хранилища под Flutter.
