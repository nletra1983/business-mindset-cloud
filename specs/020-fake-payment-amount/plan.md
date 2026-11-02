# Implementation Plan: Фейковая оплата

**Branch**: `020-fake-payment-amount` | **Date**: 2026-11-02 | **Spec**: [spec.md](./spec.md)

## Summary

Paywall UI + persist intent amount; no acquiring.

## Technical Context

**Language/Version**: Python 3.12 + landing UI
**Storage**: fake_payment_intent table
**Testing**: pytest persist/default amount
**Constraints**: no payment provider SDK

## Constitution Check

- Fake pay without provider allowed. Pass.
