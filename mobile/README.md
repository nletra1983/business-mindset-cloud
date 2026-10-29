# Клиент Business Mindset (Flutter)

Один клиент для автора. Первая поставка — подписанный APK без магазина.

## Сборка APK

1. Flutter stable + Android SDK в PATH.
2. `android/key.properties.example` → `android/key.properties` (keystore вне git).
3. `powershell -File mobile/tool/build_author_apk.ps1`
4. Файл: `mobile/build/app/outputs/flutter-apk/app-release.apk`

Базовый URL каналов: переменная `CHANNEL_BASE_URL` (тот же хост, что у бота).

iOS и магазины в эту историю не входят.
