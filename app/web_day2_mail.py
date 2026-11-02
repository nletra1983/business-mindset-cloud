"""Day-2 return invite: enqueue ~24h after web email gate; send via mail.env."""

from __future__ import annotations

import logging
import threading
import time
import uuid
from datetime import datetime, timedelta, timezone
from typing import Callable

from app.db import connect
from app.mail import MailNotConfigured, send_message

log = logging.getLogger("bot")

SUBJECT = "Вернитесь к разбору на Get Business Idea"
BODY = (
    "Здравствуйте!\n\n"
    "Вчера вы начали разбор предпринимательского мышления на get-business-idea.ru. "
    "Загляните снова: продолжите с того же места по своему email или возьмите новый факт.\n\n"
    "Открыть: https://get-business-idea.ru/#demo\n\n"
    "Это одно напоминание, не рассылка-серия.\n"
)
DELAY = timedelta(hours=24)


def day2_body() -> str:
    return BODY


def enqueue_day2(conn, *, email: str, person_id: str | None, run_id: str | None) -> str | None:
    """Schedule one pending invite. Idempotent per email while pending. Never raises to caller path."""
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id FROM day2_mail
                WHERE email = %s AND status = 'pending'
                LIMIT 1
                """,
                (email,),
            )
            existing = cur.fetchone()
            if existing:
                return str(existing[0])
            due = datetime.now(timezone.utc) + DELAY
            mail_id = str(uuid.uuid4())
            cur.execute(
                """
                INSERT INTO day2_mail (id, email, person_id, run_id, due_at, status)
                VALUES (%s, %s, %s, %s, %s, 'pending')
                """,
                (mail_id, email, person_id, run_id, due),
            )
        return mail_id
    except Exception:
        log.exception("day2 enqueue failed for %s", email)
        return None


def process_due(
    conn,
    *,
    now: datetime | None = None,
    send: Callable[[str, str, str], None] | None = None,
) -> int:
    """Send due pending letters. Returns count sent. Failures marked failed; no crash."""
    send_fn = send or send_message
    now = now or datetime.now(timezone.utc)
    sent = 0
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, email FROM day2_mail
            WHERE status = 'pending' AND due_at <= %s
            ORDER BY due_at
            LIMIT 50
            """,
            (now,),
        )
        rows = list(cur.fetchall())
    for mail_id, email in rows:
        try:
            send_fn(email, SUBJECT, BODY)
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE day2_mail
                    SET status = 'sent', sent_at = %s
                    WHERE id = %s
                    """,
                    (now, mail_id),
                )
            sent += 1
        except MailNotConfigured:
            log.warning("day2 mail not configured; leave pending id=%s", mail_id)
        except Exception:
            log.exception("day2 send failed id=%s email=%s", mail_id, email)
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE day2_mail SET status = 'failed' WHERE id = %s",
                    (mail_id,),
                )
    return sent


def start_day2_ticker(interval_sec: int = 300) -> None:
    def loop() -> None:
        while True:
            try:
                conn = connect()
                try:
                    n = process_due(conn)
                    if n:
                        conn.commit()
                        log.info("day2 mail sent=%s", n)
                    else:
                        conn.rollback()
                finally:
                    conn.close()
            except Exception:
                log.exception("day2 tick failed")
            time.sleep(interval_sec)

    thread = threading.Thread(target=loop, name="day2-mail", daemon=True)
    thread.start()
