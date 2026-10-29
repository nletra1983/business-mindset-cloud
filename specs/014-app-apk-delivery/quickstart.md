# Quickstart: Flutter APK автору

## Проверки без сборки

```text
py -3.12 -m pytest tests/test_apk_delivery.py
```

## Сборка на машине автора

1. Установить Flutter stable и Android SDK.
2. Скопировать `mobile/android/key.properties.example` → `key.properties`, указать путь к своему keystore (не в git).
3. Из корня репозитория:

```text
powershell -File mobile/tool/build_author_apk.ps1
```

4. APK: `mobile/build/app/outputs/flutter-apk/app-release.apk` — поставить на телефон автора без магазина.
