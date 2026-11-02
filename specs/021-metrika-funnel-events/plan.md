# Implementation Plan: Метрика воронки

**Branch**: `021-metrika-funnel-events` | **Date**: 2026-11-02 | **Spec**: [spec.md](./spec.md)

## Summary

Inject counter + JS events at funnel milestones; server limits unchanged.

## Technical Context

**Language/Version**: JS on landing + optional server-side goals later
**Config**: YANDEX_METRIKA_COUNTER_ID
**Testing**: presence of counter snippet; event helper unit tests
**Constraints**: non-secret counter id

## Constitution Check

- Analytics not limit authority. Pass.
