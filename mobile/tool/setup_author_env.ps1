# Persistent-ish session env for author APK builds on this PC.
# Run once per PowerShell session before build_author_apk.ps1, or set User env vars below.

$ErrorActionPreference = "Stop"

$flutter = "D:\flutter"
$android = "D:\Android\Sdk"
$java = "C:\Program Files\Microsoft\jdk-17.0.21.21-hotspot"

if (-not (Test-Path "$flutter\bin\flutter.bat")) {
    Write-Error "Flutter not found at $flutter"
}
if (-not (Test-Path $android)) {
    Write-Error "Android SDK not found at $android"
}
if (-not (Test-Path $java)) {
    Write-Error "JDK not found at $java"
}

$env:JAVA_HOME = $java
$env:ANDROID_HOME = $android
$env:ANDROID_SDK_ROOT = $android
$env:Path = "$flutter\bin;$java\bin;$android\platform-tools;$env:Path"

Write-Host "JAVA_HOME=$env:JAVA_HOME"
Write-Host "ANDROID_HOME=$env:ANDROID_HOME"
flutter --version
flutter config --android-sdk $android | Out-Null
flutter doctor
