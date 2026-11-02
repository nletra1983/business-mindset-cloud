"""Guest smoke trainer: windows, get-news fact, captcha before model, 3 steps → gate."""

from __future__ import annotations

import json
import random
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from app.config import MODEL_REQUESTED
from app.deepseek import ModelDown, finale, judge_block
from app.get_news_backlog import BACKLOG
from app.skill import blank_topic, event_prompt, scale_prompt
from app import smartcaptcha
from app.web_landing import WINDOWS_LIMIT, moscow_today

VerifyFn = Callable[[str | None, str | None], bool]

_ITEM_RE = re.compile(r"^\d+\.\s+(.+)$")


def pick_news_fact(backlog_path: Path | None = None) -> str | None:
    path = backlog_path or BACKLOG
    if not path.is_file():
        return None
    items: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        m = _ITEM_RE.match(line.strip())
        if m:
            text = m.group(1).strip()
            if text:
                items.append(text)
    if not items:
        return None
    return random.choice(items)


def _empty_state(topic: str) -> dict[str, Any]:
    return {
        "topic": topic,
        "phase": "event",
        "event_answer": "",
        "scale_answer": "",
        "messages": [],
        "gate_shown": False,
    }


def _load_state(raw) -> dict[str, Any]:
    if raw is None:
        return _empty_state("")
    if isinstance(raw, str):
        raw = json.loads(raw)
    if isinstance(raw, list):
        return _empty_state("")
    if isinstance(raw, dict):
        state = _empty_state(str(raw.get("topic") or ""))
        state.update(
            {
                "phase": raw.get("phase") or "event",
                "event_answer": raw.get("event_answer") or "",
                "scale_answer": raw.get("scale_answer") or "",
                "messages": list(raw.get("messages") or []),
                "gate_shown": bool(raw.get("gate_shown")),
            }
        )
        return state
    return _empty_state("")


def _append(state: dict[str, Any], role: str, text: str) -> None:
    state["messages"].append({"role": role, "text": text})


def _window_row(conn, window_id: str) -> dict[str, Any] | None:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, guest_session_id, transcript, step_count, first_reply_at, closed_at
            FROM guest_window WHERE id = %s
            """,
            (window_id,),
        )
        row = cur.fetchone()
    if not row:
        return None
    return {
        "id": str(row[0]),
        "guest_session_id": str(row[1]),
        "transcript": row[2],
        "step_count": int(row[3] or 0),
        "first_reply_at": row[4],
        "closed_at": row[5],
    }


def _save_window(conn, window_id: str, state: dict[str, Any], step_count: int, *, touch_first: bool) -> None:
    with conn.cursor() as cur:
        if touch_first:
            cur.execute(
                """
                UPDATE guest_window
                SET transcript = %s::jsonb, step_count = %s,
                    first_reply_at = COALESCE(first_reply_at, %s)
                WHERE id = %s
                """,
                (json.dumps(state, ensure_ascii=False), step_count, datetime.now(timezone.utc), window_id),
            )
        else:
            cur.execute(
                """
                UPDATE guest_window
                SET transcript = %s::jsonb, step_count = %s
                WHERE id = %s
                """,
                (json.dumps(state, ensure_ascii=False), step_count, window_id),
            )


def start_window(
    conn,
    session: dict[str, Any],
    *,
    fact: str | None = None,
    use_news: bool = True,
) -> tuple[int, dict[str, Any]]:
    """Create guest window under daily limit; attach news or own fact; first question without model."""
    used = int(session.get("windows_used_today") or 0)
    if used >= WINDOWS_LIMIT:
        return 403, {
            "error": "window_limit",
            "message": "На сегодня лимит гостевых окон исчерпан (3). Зайдите завтра или продолжите с email позже.",
            "windows_used_today": used,
            "windows_limit": WINDOWS_LIMIT,
        }

    own = (fact or "").strip()
    topic = ""
    source = "own"
    if own:
        if blank_topic(own):
            return 400, {
                "error": "blank_fact",
                "message": "Сформулируйте факт своими словами. Новость я не выдумываю.",
            }
        topic = own
    elif use_news:
        picked = pick_news_fact()
        if not picked:
            return 400, {
                "error": "no_news",
                "message": "В бэклоге пока нет новости. Напишите свой факт.",
            }
        topic = picked
        source = "get-news"
    else:
        return 400, {
            "error": "blank_fact",
            "message": "Сформулируйте факт своими словами. Новость я не выдумываю.",
        }

    window_id = str(uuid.uuid4())
    state = _empty_state(topic)
    question = event_prompt(topic)
    _append(state, "agent", question)
    today = moscow_today()
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO guest_window (id, guest_session_id, transcript, step_count)
            VALUES (%s, %s, %s::jsonb, 0)
            """,
            (window_id, session["id"], json.dumps(state, ensure_ascii=False)),
        )
        cur.execute(
            """
            UPDATE guest_session
            SET windows_used_today = windows_used_today + 1,
                windows_day = %s,
                current_window_id = %s,
                updated_at = now()
            WHERE id = %s
            """,
            (today, window_id, session["id"]),
        )
    session["windows_used_today"] = used + 1
    session["current_window_id"] = window_id
    return 200, {
        "window_id": window_id,
        "topic": topic,
        "source": source,
        "agent_reply": question,
        "step_count": 0,
        "steps_limit": 3,
        "gate_required": False,
        "windows_used_today": session["windows_used_today"],
        "windows_limit": WINDOWS_LIMIT,
    }


def clear_window(conn, session: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    """Mark client clear; do not delete server transcript (TTL policy)."""
    wid = session.get("current_window_id")
    if not wid:
        return 200, {"ok": True, "cleared": False, "message": "Нет открытого окна"}
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE guest_window
            SET cleared_client_at = now()
            WHERE id = %s
            """,
            (wid,),
        )
        cur.execute(
            """
            UPDATE guest_session
            SET current_window_id = NULL, updated_at = now()
            WHERE id = %s
            """,
            (session["id"],),
        )
    session["current_window_id"] = None
    return 200, {"ok": True, "cleared": True}


def post_message(
    conn,
    session: dict[str, Any],
    *,
    text: str,
    captcha_token: str | None,
    ip: str | None = None,
    verify: VerifyFn | None = None,
    model_id: str | None = None,
) -> tuple[int, dict[str, Any]]:
    """One human smoke turn; SmartCaptcha required before any model call."""
    wid = session.get("current_window_id")
    if not wid:
        return 400, {"error": "no_window", "message": "Сначала начните окно тренажёра"}

    row = _window_row(conn, wid)
    if not row:
        return 400, {"error": "no_window", "message": "Окно закрыто. Начните новое."}

    step_count = row["step_count"]
    if step_count >= 3 or row["closed_at"]:
        return 403, {
            "error": "gate_required",
            "message": "Три шага гостя использованы. Чтобы продолжить — оставьте email (следующий экран).",
            "gate_required": True,
            "step_count": step_count,
        }

    state = _load_state(row["transcript"])
    answer = (text or "").strip()
    if not answer:
        return 400, {
            "error": "blank_answer",
            "message": "Напишите ответ своими словами.",
        }

    verify_fn = verify or smartcaptcha.verify_token
    if not verify_fn(captcha_token, ip):
        return 403, {
            "error": "captcha_failed",
            "message": "Проверка SmartCaptcha не пройдена. Модель не вызывалась.",
        }

    mid = model_id or MODEL_REQUESTED
    _append(state, "human", answer)
    touch_first = row["first_reply_at"] is None
    agent_reply = ""
    gate_required = False

    try:
        if state["phase"] == "event":
            ok, missing, _returned = judge_block("event", state["topic"], answer, mid)
            if not ok:
                agent_reply = f"{missing}\n{event_prompt(state['topic'])}"
            else:
                state["event_answer"] = answer
                state["phase"] = "scale"
                agent_reply = scale_prompt(state["topic"])
        elif state["phase"] == "scale":
            ok, missing, _returned = judge_block("scale", state["topic"], answer, mid)
            if not ok:
                agent_reply = f"{missing}\n{scale_prompt(state['topic'])}"
            else:
                state["scale_answer"] = answer
                state["phase"] = "closing"
                agent_reply = (
                    f"По «{state['topic']}» уже есть сдвиг и группы. "
                    "Какую короткую проверку за неделю вы бы сделали — как думаешь?"
                )
        elif state["phase"] == "closing":
            state["phase"] = "done"
            _spoken, worked, weak, missed, _ret = finale(
                state["topic"],
                state["event_answer"] or answer,
                state["scale_answer"] or answer,
                mid,
            )
            agent_reply = f"ПОЛУЧИЛОСЬ: {worked}\n\nСЛАБО: {weak}\n\nПРОПУЩЕНО: {missed}"
        else:
            return 403, {
                "error": "gate_required",
                "message": "Разбор в этом окне завершён. Дальше — email-гейт.",
                "gate_required": True,
                "step_count": step_count,
            }
    except ModelDown:
        return 503, {
            "error": "model_down",
            "message": "Модель сейчас недоступна. Попробуйте ещё раз чуть позже.",
        }

    _append(state, "agent", agent_reply)
    step_count += 1
    if step_count >= 3 or state["phase"] == "done":
        gate_required = True
        state["gate_shown"] = True
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE guest_window SET closed_at = COALESCE(closed_at, now()) WHERE id = %s",
                (wid,),
            )

    _save_window(conn, wid, state, step_count, touch_first=touch_first)
    return 200, {
        "window_id": wid,
        "agent_reply": agent_reply,
        "step_count": step_count,
        "steps_limit": 3,
        "gate_required": gate_required,
        "phase": state["phase"],
        "messages": state["messages"],
    }
