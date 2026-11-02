# Implementation Plan: Гейт email без кода

**Branch**: `018-email-continue-gate` | **Date**: 2026-11-02 | **Spec**: [spec.md](./spec.md)

## Summary

Web gate: bind guest session to person by email without code; continue smoke 3 steps; resume by email. App code login untouched.

## Technical Context

**Language/Version**: Python 3.12
**Primary Dependencies**: entrances/person model; guest_session; smoke
**Storage**: Postgres person + run + guest link
**Testing**: pytest continue without mail mock code
**Constraints**: do not alter app `/app/v1` code challenge

## Constitution Check

- Web may continue without code (ADL-023). Pass.
- Mobile code unchanged. Pass.

## Project Structure

```text
app/web_email_gate.py
tests/test_web_email_gate.py
```
