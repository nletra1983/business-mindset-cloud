# Implementation Plan: Разбор новости в приложении

**Branch**: `010-app-news-run` | **Date**: 2026-10-29 | **Spec**: [spec.md](./spec.md)

## Summary

Из списка ходов человек начинает разбор своей формулировкой и возвращается в незаконченный. Вызовы идут в уже работающий ход бота. Карточка прошлого, повтор темы и удаление не добавляются.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: `app/run_flow.py`, `app/run_list.py`

**Storage**: те же ходы

**Testing**: `pytest`

**Target Platform**: тот же процесс

**Constraints**: вторая копия правил разбора не пишется. Настройки не входят. Приложение не вызывает модель само.

## Constitution Check

- Один процесс. Pass.
- Канал не владеет ходом. Pass.
- Стек не перевыбирается. Pass.
- Граница истории соблюдена. Pass.
- Открытых `NEEDS CLARIFICATION` нет. Pass.

## Project Structure

```text
app/app_news.py
tests/test_app_news_run.py
```
