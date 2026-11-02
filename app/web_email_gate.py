"""Web email gate without code: bind guest → person, continue smoke steps 4–6, resume."""

from __future__ import annotations

import json
import uuid
from typing import Any

from app.config import ACCESS_MODE, MODEL_REQUESTED, SKILL_VERSION
from app.entrances import normalize_email
from app.web_day2_mail import enqueue_day2
from app.web_guest_smoke import _load_state, _window_row

EMAIL_STEPS_LIMIT = 3

_STEP_PROMPTS = (
    "Кто уже платит или теряет из‑за этого сдвига — назовите конкретнее, как думаешь?",
    "Какую короткую проверку за неделю вы бы сделали, чтобы не строить впустую — как по‑твоему?",
    "Соберите черновик своими словами: для кого, какая боль, кто платит, какая проверка.",
)


def _guest_messages(conn, session: dict[str, Any]) -> tuple[str, list[dict[str, str]]]:
    wid = session.get("current_window_id")
    topic = ""
    messages: list[dict[str, str]] = []
    if wid:
        row = _window_row(conn, wid)
        if row:
            state = _load_state(row["transcript"])
            topic = state.get("topic") or ""
            messages = list(state.get("messages") or [])
    return topic, messages


def _ensure_person_for_email(conn, email: str) -> str:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT person_id FROM email_link WHERE email = %s",
            (email,),
        )
        row = cur.fetchone()
        if row:
            person_id = row[0]
            cur.execute(
                """
                UPDATE email_link
                SET confirmed = true, updated_at = now()
                WHERE email = %s
                """,
                (email,),
            )
            return str(person_id)
        person_id = uuid.uuid4()
        cur.execute(
            "INSERT INTO person (id, accepting_new) VALUES (%s, false)",
            (str(person_id),),
        )
        cur.execute(
            """
            INSERT INTO email_link (id, person_id, email, confirmed)
            VALUES (%s, %s, %s, true)
            """,
            (str(uuid.uuid4()), str(person_id), email),
        )
        return str(person_id)


def _create_run_with_transcript(
    conn,
    person_id: str,
    topic: str,
    messages: list[dict[str, str]],
) -> str:
    run_id = str(uuid.uuid4())
    topic_text = topic or "веб-разбор"
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO run (
                id, person_id, status, step, skill_version, topic_text,
                access_mode, model_requested, telegram_chat_id, in_window
            ) VALUES (
                %s, %s, 'open', 'finalizing', %s, %s,
                %s, %s, 0, false
            )
            """,
            (run_id, person_id, SKILL_VERSION, topic_text, ACCESS_MODE, MODEL_REQUESTED),
        )
        for msg in messages:
            role = msg.get("role") or "agent"
            speaker = "human" if role == "human" else "agent"
            cur.execute(
                """
                INSERT INTO utterance (id, run_id, speaker, text)
                VALUES (%s, %s, %s, %s)
                """,
                (str(uuid.uuid4()), run_id, speaker, msg.get("text") or ""),
            )
    return run_id


def _save_continue(
    conn,
    session_id: str,
    *,
    person_id: str,
    email: str,
    run_id: str,
    transcript: list[dict[str, str]],
    email_steps_done: int,
) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE guest_session
            SET person_id = %s,
                last_email = %s,
                continue_run_id = %s,
                continue_transcript = %s::jsonb,
                email_steps_done = %s,
                updated_at = now()
            WHERE id = %s
            """,
            (
                person_id,
                email,
                run_id,
                json.dumps(transcript, ensure_ascii=False),
                email_steps_done,
                session_id,
            ),
        )


def _load_continue(conn, session_id: str) -> dict[str, Any] | None:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT person_id, last_email, continue_run_id, email_steps_done, continue_transcript
            FROM guest_session WHERE id = %s
            """,
            (session_id,),
        )
        row = cur.fetchone()
    if not row or not row[2]:
        return None
    transcript = row[4]
    if isinstance(transcript, str):
        transcript = json.loads(transcript)
    if not isinstance(transcript, list):
        transcript = []
    return {
        "person_id": str(row[0]) if row[0] else None,
        "last_email": row[1],
        "continue_run_id": str(row[2]),
        "email_steps_done": int(row[3] or 0),
        "continue_transcript": transcript,
    }


def submit_email(conn, session: dict[str, Any], raw_email: str) -> tuple[int, dict[str, Any]]:
    email = normalize_email(raw_email)
    if email is None:
        return 400, {
            "error": "invalid_email",
            "message": "Укажите обычный email, например name@example.com",
        }

    topic, messages = _guest_messages(conn, session)
    if not messages and not session.get("current_window_id"):
        # allow resume path to use submit? no — resume is separate
        existing = _load_continue(conn, session["id"])
        if existing and existing.get("last_email") == email:
            return resume_email(conn, session, email)

    person_id = _ensure_person_for_email(conn, email)
    run_id = _create_run_with_transcript(conn, person_id, topic, messages)
    prompt = _STEP_PROMPTS[0]
    continued = list(messages) + [{"role": "agent", "text": prompt}]
    _save_continue(
        conn,
        session["id"],
        person_id=person_id,
        email=email,
        run_id=run_id,
        transcript=continued,
        email_steps_done=0,
    )
    session["person_id"] = person_id
    enqueue_day2(conn, email=email, person_id=person_id, run_id=run_id)
    return 200, {
        "ok": True,
        "email": email,
        "person_id": person_id,
        "run_id": run_id,
        "agent_reply": prompt,
        "email_steps_done": 0,
        "email_steps_limit": EMAIL_STEPS_LIMIT,
        "messages": continued,
        "code_required": False,
    }


def resume_email(conn, session: dict[str, Any], raw_email: str) -> tuple[int, dict[str, Any]]:
    email = normalize_email(raw_email)
    if email is None:
        return 400, {
            "error": "invalid_email",
            "message": "Укажите обычный email, например name@example.com",
        }

    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, person_id, last_email, continue_run_id, email_steps_done, continue_transcript
            FROM guest_session
            WHERE last_email = %s AND continue_run_id IS NOT NULL
            ORDER BY updated_at DESC
            LIMIT 1
            """,
            (email,),
        )
        row = cur.fetchone()
    if not row:
        return 404, {
            "error": "not_found",
            "message": "Сохранённого разбора для этого email пока нет. Начните с гостевых шагов.",
        }

    source_id, person_id, last_email, run_id, steps_done, transcript = row
    if isinstance(transcript, str):
        transcript = json.loads(transcript)
    if not isinstance(transcript, list):
        transcript = []
    steps_done = int(steps_done or 0)

    # Attach continue state to current cookie session (do not guess by IP alone).
    _save_continue(
        conn,
        session["id"],
        person_id=str(person_id),
        email=last_email,
        run_id=str(run_id),
        transcript=transcript,
        email_steps_done=steps_done,
    )
    session["person_id"] = str(person_id)

    if steps_done >= EMAIL_STEPS_LIMIT:
        return 200, {
            "ok": True,
            "email": email,
            "resumed": True,
            "email_steps_done": steps_done,
            "email_steps_limit": EMAIL_STEPS_LIMIT,
            "payment_gate": True,
            "messages": transcript,
            "agent_reply": "Разбор до оплаты уже пройден. Дальше — экран суммы (следующая история).",
        }

    next_prompt = _STEP_PROMPTS[min(steps_done, len(_STEP_PROMPTS) - 1)]
    return 200, {
        "ok": True,
        "email": email,
        "resumed": True,
        "email_steps_done": steps_done,
        "email_steps_limit": EMAIL_STEPS_LIMIT,
        "agent_reply": next_prompt,
        "messages": transcript,
        "code_required": False,
    }


def post_continue_message(
    conn,
    session: dict[str, Any],
    *,
    text: str,
) -> tuple[int, dict[str, Any]]:
    """Steps 4–6 after email; no mailbox wait; captcha already done on guest path optional here."""
    state = _load_continue(conn, session["id"])
    if not state:
        return 400, {
            "error": "no_continue",
            "message": "Сначала введите email, чтобы продолжить.",
        }
    steps = state["email_steps_done"]
    if steps >= EMAIL_STEPS_LIMIT:
        return 403, {
            "error": "payment_gate",
            "message": "Три шага после email использованы. Дальше — экран оплаты.",
            "payment_gate": True,
            "email_steps_done": steps,
        }
    answer = (text or "").strip()
    if not answer:
        return 400, {
            "error": "blank_answer",
            "message": "Напишите ответ своими словами.",
        }

    transcript = list(state["continue_transcript"])
    transcript.append({"role": "human", "text": answer})
    steps += 1
    payment_gate = steps >= EMAIL_STEPS_LIMIT
    if payment_gate:
        agent_reply = (
            "Черновик принят. Три шага после email готовы — дальше экран с суммой "
            "(фейковая оплата в следующей истории)."
        )
    else:
        agent_reply = _STEP_PROMPTS[steps]
    transcript.append({"role": "agent", "text": agent_reply})

    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO utterance (id, run_id, speaker, text)
            VALUES (%s, %s, 'human', %s), (%s, %s, 'agent', %s)
            """,
            (
                str(uuid.uuid4()),
                state["continue_run_id"],
                answer,
                str(uuid.uuid4()),
                state["continue_run_id"],
                agent_reply,
            ),
        )
        if payment_gate:
            cur.execute(
                "UPDATE run SET status = 'completed', updated_at = now() WHERE id = %s",
                (state["continue_run_id"],),
            )

    _save_continue(
        conn,
        session["id"],
        person_id=state["person_id"],
        email=state["last_email"],
        run_id=state["continue_run_id"],
        transcript=transcript,
        email_steps_done=steps,
    )
    return 200, {
        "ok": True,
        "agent_reply": agent_reply,
        "email_steps_done": steps,
        "email_steps_limit": EMAIL_STEPS_LIMIT,
        "payment_gate": payment_gate,
        "messages": transcript,
    }
