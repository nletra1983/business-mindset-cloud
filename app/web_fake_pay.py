"""Fake paywall: amount field, persist intent, no payment provider."""

from __future__ import annotations

import uuid
from decimal import Decimal, InvalidOperation
from typing import Any

PAYWALL_COPY = (
    "Хочешь качать своё предпринимательское мышление регулярно и на результат? "
    "Внеси небольшую оплату, чтоб мы смогли продолжить предлагать тебе лучшие ответы."
)
DEFAULT_AMOUNT = Decimal("100")
CONFIRMATION = (
    "Записали. Когда оплата заработает — напишем на email. Сейчас деньги не списываем."
)


def parse_amount(raw) -> Decimal | None:
    if raw is None:
        return None
    try:
        value = Decimal(str(raw).replace(",", ".").strip())
    except (InvalidOperation, ValueError):
        return None
    if value <= 0:
        return None
    return value.quantize(Decimal("0.01"))


def last_amount_for(conn, *, email: str | None, person_id: str | None) -> Decimal | None:
    with conn.cursor() as cur:
        if person_id:
            cur.execute(
                """
                SELECT amount_rub FROM fake_payment_intent
                WHERE person_id = %s
                ORDER BY created_at DESC
                LIMIT 1
                """,
                (person_id,),
            )
            row = cur.fetchone()
            if row:
                return Decimal(str(row[0]))
        if email:
            cur.execute(
                """
                SELECT amount_rub FROM fake_payment_intent
                WHERE email = %s
                ORDER BY created_at DESC
                LIMIT 1
                """,
                (email,),
            )
            row = cur.fetchone()
            if row:
                return Decimal(str(row[0]))
    return None


def paywall_state(conn, session: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    email = None
    person_id = session.get("person_id")
    with conn.cursor() as cur:
        cur.execute(
            "SELECT last_email, person_id, email_steps_done FROM guest_session WHERE id = %s",
            (session["id"],),
        )
        row = cur.fetchone()
    if row:
        email = row[0]
        person_id = str(row[1]) if row[1] else person_id
        steps = int(row[2] or 0)
    else:
        steps = 0
    prior = last_amount_for(conn, email=email, person_id=person_id)
    amount = prior if prior is not None else DEFAULT_AMOUNT
    return 200, {
        "copy": PAYWALL_COPY,
        "default_amount": float(amount),
        "currency": "RUB",
        "ready": steps >= 3,
        "email": email,
        "has_prior_amount": prior is not None,
    }


def record_click(conn, session: dict[str, Any], raw_amount) -> tuple[int, dict[str, Any]]:
    amount = parse_amount(raw_amount)
    if amount is None:
        return 400, {
            "error": "invalid_amount",
            "message": "Укажите сумму больше нуля.",
        }
    email = None
    person_id = session.get("person_id")
    with conn.cursor() as cur:
        cur.execute(
            "SELECT last_email, person_id FROM guest_session WHERE id = %s",
            (session["id"],),
        )
        row = cur.fetchone()
        if row:
            email = row[0]
            person_id = str(row[1]) if row[1] else person_id
        intent_id = str(uuid.uuid4())
        cur.execute(
            """
            INSERT INTO fake_payment_intent (id, person_id, email, amount_rub)
            VALUES (%s, %s, %s, %s)
            """,
            (intent_id, person_id, email, amount),
        )
    return 200, {
        "ok": True,
        "intent_id": intent_id,
        "amount": float(amount),
        "confirmation": CONFIRMATION,
        "charged": False,
    }
