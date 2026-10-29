# Клиент Business Mindset (Flutter)

Один клиент для автора. Первая поставка — подписанный APK без магазина.

## Окружение на этой машине автора

Уже разложено на диск `D:` (на `C:` мало места):

| Что | Путь |
|---|---|
| Flutter 3.47.8 stable | `D:\flutter` |
| Android SDK | `D:\Android\Sdk` |
| JDK 17 | `C:\Program Files\Microsoft\jdk-17.0.21.21-hotspot` |
| Keystore (не в git) | `secrets/businessmindset-upload.jks` |
| Подпись Gradle (не в git) | `mobile/android/key.properties` |

Переменные `JAVA_HOME`, `ANDROID_HOME`, `Path` записаны в **User** env. Новый терминал подхватит их сам. В текущей сессии:

```powershell
. .\mobile\tool\setup_author_env.ps1
```

## Сборка APK

1. Keystore и `key.properties` уже должны существовать локально (не коммитить).
2. `powershell -File mobile/tool/build_author_apk.ps1`
3. Файл: `mobile/build/app/outputs/flutter-apk/app-release.apk`

Базовый URL каналов: `CHANNEL_BASE_URL` (тот же хост, что у бота).

iOS и магазины в эту историю не входят.

Visual Studio для Windows-desktop Flutter не нужен, если собираете только APK.
