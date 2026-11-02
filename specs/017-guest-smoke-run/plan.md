# Implementation Plan: Гостевой тренажёр smoke

**Branch**: `017-guest-smoke-run` | **Date**: 2026-11-02 | **Spec**: [spec.md](./spec.md)

## Summary

Guest API + UI in demo zone: get-news fact, smoke ≤3 steps, captcha, window limit, clear UI, gate placeholder.

## Technical Context

**Language/Version**: Python 3.12 + landing JS/HTML
**Primary Dependencies**: existing model gateway; SmartCaptcha verify; get-news backlog
**Storage**: guest_session / guest_window from story 0
**Testing**: pytest for limits/captcha gate; manual UI
**Constraints**: one process; no `/app` rewrite

## Constitution Check

- Server-side model calls. Pass. Smoke skill versioned. Pass. Captcha before call. Pass.

## Project Structure

```text
app/web_landing.py / app/web_guest_smoke.py
web/demo.js (or inline)
tests/test_guest_smoke.py
```
