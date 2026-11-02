# Implementation Plan: Письмо дня 2

**Branch**: `019-day2-return-email` | **Date**: 2026-11-02 | **Spec**: [spec.md](./spec.md)

## Summary

Schedule and send one return email ~24h after web email gate using mail.env; no transcript in body.

## Technical Context

**Language/Version**: Python 3.12
**Primary Dependencies**: existing SMTP mail helper
**Storage**: day2_outbox table or equivalent
**Testing**: pytest with mail mock
**Constraints**: no agent SSH; no dialogue in mail

## Constitution Check

- Mail contour reuse. Pass. No dialogue in mail. Pass.

## Decision

Default schedule: 24 hours after successful web email gate.
