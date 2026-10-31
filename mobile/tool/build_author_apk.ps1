# Builds a signed release APK for the author. Requires Flutter stable and Android SDK.
# Keystore: copy android/key.properties.example -> android/key.properties (not in git).

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

if (-not (Get-Command flutter -ErrorAction SilentlyContinue)) {
    Write-Error "Flutter SDK not in PATH. Install Flutter stable, then re-run this script."
}

$props = Join-Path $root "android\key.properties"
if (-not (Test-Path $props)) {
    Write-Warning "android/key.properties missing - release may fall back to debug signing. Copy key.properties.example and point to your keystore."
}

$base = $env:CHANNEL_BASE_URL
if (-not $base) {
    Write-Warning "CHANNEL_BASE_URL not set; default in app is http://127.0.0.1:8080"
    flutter build apk --release
} else {
    flutter build apk --release --dart-define=CHANNEL_BASE_URL=$base
}

$apk = Join-Path $root "build\app\outputs\flutter-apk\app-release.apk"
if (-not (Test-Path $apk)) {
    Write-Error "APK not found at $apk"
}
Write-Host "APK ready: $apk"
