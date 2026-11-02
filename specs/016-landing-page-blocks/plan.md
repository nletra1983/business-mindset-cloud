# Implementation Plan: Лендинг — hero и блоки

**Branch**: `016-landing-page-blocks` | **Date**: 2026-11-02 | **Spec**: [spec.md](./spec.md)

## Summary

Секции лендинга и mobile-first стили на каркасе story 0; якорь демо; без агента.

## Technical Context

**Language/Version**: HTML/CSS served by existing Python HTTP process
**Primary Dependencies**: static `web/`
**Storage**: N/A
**Testing**: HTTP/html contains section ids
**Target Platform**: get-business-idea.ru via bot HTTP
**Project Type**: static landing
**Constraints**: no new framework; do not break `/app/v1`

## Constitution Check

- One process. Pass. Russian. Pass. No fake social proof. Pass.

## Project Structure

```text
web/index.html
web/styles.css
tests/test_landing_page.py
```
