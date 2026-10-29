# Contract: поставка APK

## Артефакт

- Путь сборки: `mobile/build/app/outputs/flutter-apk/app-release.apk`
- Подпись: release keystore из `mobile/android/key.properties` (файл не в git)
- Package: `ru.businessmindset.app`

## Сеть

Базовый URL каналов задаётся конфигурацией клиента (тот же хост сервиса бота). Пути только под `/app/v1` из `012`.

## Игнор секретов

В git не попадают: `key.properties`, `*.jks`, `*.keystore`, `*.apk` (опционально крупные бинарники — APK у автора локально; в git APK не коммитить).
