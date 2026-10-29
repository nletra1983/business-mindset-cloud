# Implementation Plan: Flutter-клиент и подписанный APK автору

**Branch**: `014-app-apk-delivery` | **Date**: 2026-10-29 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/014-app-apk-delivery/spec.md`

## Summary

В репозитории появляется один Flutter-проект клиента. Release-сборка кладёт подписанный APK в каталог сборки на диске автора. Ключ подписи — вне git (`secrets/` / локальный keystore). Клиент ходит только во вход `/app/v1`. Полные экраны №5–№8 могут быть тонкими: нужен каркас, который открывает вход каналов.

## Technical Context

**Language/Version**: Dart / Flutter stable; Android release APK

**Primary Dependencies**: Flutter SDK на машине автора; Android SDK; keystore вне git

**Storage**: нет новой серверной схемы; сессия — по `013`

**Testing**: проверка структуры проекта, package id, `.gitignore` на keystore; сборка APK — скрипт для автора (на агенте Flutter может отсутствовать)

**Target Platform**: Android автора, sideload

**Project Type**: клиент в `mobile/`

**Performance Goals**: не задаются

**Constraints**: один package id; без iOS/магазинов; без второго бэкенда; ADL-020

**Scale/Scope**: один автор, один APK

## Constitution Check

- Клиент не вызывает модель. Pass.
- Flutter уже принят (ADL-020), стек не перевыбираем. Pass.
- Секреты подписи не в git. Pass.
- Selectel агент не трогает. Pass.
- Нет `NEEDS CLARIFICATION`. Pass.

### Post-design

Проект `mobile/`, applicationId `ru.businessmindset.app`, скрипт `mobile/tool/build_author_apk.ps1`, пример `key.properties.example`.

## Project Structure

### Documentation

```text
specs/014-app-apk-delivery/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── apk-delivery.md
└── tasks.md
```

### Source Code

```text
mobile/
├── pubspec.yaml
├── lib/
│   ├── main.dart
│   ├── channel_client.dart
│   └── session_store.dart
├── android/
└── tool/
    └── build_author_apk.ps1
```

**Structure Decision**: один каталог `mobile/` в корне репозитория.
