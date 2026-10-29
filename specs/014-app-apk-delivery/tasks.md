# Tasks: Flutter-клиент и подписанный APK

**Input**: Design documents from `/specs/014-app-apk-delivery/`

**Prerequisites**: plan.md, spec.md, research.md, contracts/

**Tests**: quickstart structure tests; APK binary on author machine after script.

## Phase 1: Setup

- [x] T001 Создать Flutter-проект `mobile/` с package id `ru.businessmindset.app`
- [x] T002 Добавить игнор keystore/APK и `key.properties.example`

## Phase 2: Foundational

- [x] T003 Каркас клиента: канал `/app/v1` и session store в `mobile/lib/`
- [x] T004 Скрипт `mobile/tool/build_author_apk.ps1` для release APK

## Phase 3: User Story 1 — файл установки (P1)

- [x] T005 [US1] Настроить Android release signing из `key.properties`
- [x] T006 [US1] Проверить пути и package id в `tests/test_apk_delivery.py`

## Phase 4: User Story 2 — секрет и только вход каналов (P1)

- [x] T007 [US2] Убедиться, что keystore не в git; клиент бьёт только в `/app/v1`
- [x] T008 [US2] Запустить `py -3.12 -m pytest tests/test_apk_delivery.py`

## Phase 5: Polish

- [x] T009 Если Flutter доступен — прогнать `build_author_apk.ps1`; иначе оставить скрипт автору
- [x] T010 Отметить историю в `features/feature-map.md` как `in-impl`

## Dependencies

T001 → остальное. Полный UI входа — не блокирует APK.

## Implementation strategy

Сначала проект и подпись, потом тонкий клиент и тесты структуры.
