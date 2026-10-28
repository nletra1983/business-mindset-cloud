import uuid

from app.config import ACCESS_MODE, MODEL_REQUESTED, SKILL_VERSION
from app.deepseek import ModelDown, finale, judge_block
from app.model_switch import UNAVAILABLE, apply_fallback, note_answered
from app.person import (
    STATUS_SHOWING,
    STATUS_WEAK,
    apply_hidden_profile_observations,
    has_any_run,
    read_model_state,
    set_accepting_new,
    write_model_state,
    write_open_run_model,
)
from app.skill import MISSED_LINE, blank_topic, event_prompt, scale_prompt
from app.summary import save_summary

STATUSES = ("open", "completed")
EXIT_LABEL = "к другим вопросам"


def silence(state: dict) -> dict:
    return {"status": state["status"], "step": state["step"]}


def handle_text(conn, person: dict, chat_id: int, message_id: int, text: str) -> list[dict]:
    window = _window(conn, person["id"])
    if window and window["status"] == "open":
        return _answer(conn, window, message_id, text)
    if person["accepting_new"] or not has_any_run(conn, person["id"]):
        if blank_topic(text):
            return [_text("Пусто. Сформулируй новость или проблему своими словами. Событие я не выдумываю.")]
        return _start(conn, person, chat_id, message_id, text.strip())
    return [_text("Чтобы начать другой ход, нажми «к другим вопросам».")]


def _start(conn, person: dict, chat_id: int, message_id: int, topic: str) -> list[dict]:
    person_id = person["id"]
    requested = person.get("current_model") or MODEL_REQUESTED
    run_id = uuid.uuid4()
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE run SET in_window = false WHERE person_id = %s",
            (person_id,),
        )
        cur.execute(
            """
            INSERT INTO run (
                id, person_id, status, step, skill_version, topic_text,
                access_mode, model_requested, telegram_chat_id, pinned_message_id, in_window
            ) VALUES (
                %s, %s, 'open', 'event', %s, %s,
                %s, %s, %s, %s, true
            )
            """,
            (run_id, person_id, SKILL_VERSION, topic, ACCESS_MODE, requested, chat_id, message_id),
        )
        _utter(cur, run_id, "human", topic, message_id)
        question = event_prompt(topic)
        _utter(cur, run_id, "agent", question, None)
        cur.execute("UPDATE person SET accepting_new = false WHERE id = %s", (person_id,))
    conn.commit()
    return [
        {"kind": "pin", "message_id": message_id},
        _text(question),
    ]


def _answer(conn, run: dict, message_id: int, text: str) -> list[dict]:
    if run["step"] == "finalizing":
        return _finish(conn, run)
    block = "event" if run["step"] == "event" else "scale"
    try:
        ok, missing, returned = judge_block(block, run["topic_text"], text, run["model_requested"])
    except ModelDown:
        return _unavailable(conn, run, text, message_id)
    with conn.cursor() as cur:
        _mark_answered(cur, run)
        _utter(cur, run["id"], "human", text, message_id)
        if returned:
            cur.execute(
                "UPDATE run SET model_returned = %s, updated_at = now() WHERE id = %s",
                (returned, run["id"]),
            )
        if not ok:
            prompt = event_prompt(run["topic_text"]) if block == "event" else scale_prompt(run["topic_text"])
            reply = f"{missing}\n{prompt}"
            _utter(cur, run["id"], "agent", reply, None)
            conn.commit()
            return [_text(reply)]
        if block == "event":
            cur.execute(
                """
                UPDATE run
                SET step = 'scale', event_answer = %s, updated_at = now()
                WHERE id = %s
                """,
                (text, run["id"]),
            )
            question = scale_prompt(run["topic_text"])
            _utter(cur, run["id"], "agent", question, None)
            conn.commit()
            return [_text(question)]
        cur.execute(
            """
            UPDATE run
            SET step = 'finalizing', scale_answer = %s, updated_at = now()
            WHERE id = %s
            """,
            (text, run["id"]),
        )
    conn.commit()
    run["step"] = "finalizing"
    run["scale_answer"] = text
    return _finish(conn, run)


def _finish(conn, run: dict) -> list[dict]:
    event_answer, scale_answer = _answers(conn, run)
    try:
        spoken, worked, weak, missed, returned = finale(
            run["topic_text"], event_answer, scale_answer, run["model_requested"]
        )
    except ModelDown:
        return _unavailable(conn, run, None, None)
    if MISSED_LINE not in missed:
        missed = f"{missed}\n{MISSED_LINE}".strip()
        spoken = f"{spoken}\n{MISSED_LINE}"
    save_summary(conn, run["id"], worked, weak, missed)
    observations = _hidden_profile_observations(run, event_answer, scale_answer, worked, weak)
    if observations:
        apply_hidden_profile_observations(
            conn,
            run["person_id"],
            run["id"],
            run.get("skill_version") or "",
            observations,
        )
    with conn.cursor() as cur:
        _mark_answered(cur, run)
        cur.execute(
            """
            UPDATE run
            SET status = 'completed', in_window = false, model_returned = %s, updated_at = now()
            WHERE id = %s
            """,
            (returned, run["id"]),
        )
        _utter(cur, run["id"], "agent", spoken, None)
    conn.commit()
    return [_text(spoken)]


def open_runs(conn, person_id) -> list[tuple]:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, topic_text, step, skill_version
            FROM run
            WHERE person_id = %s AND status = 'open'
            ORDER BY updated_at DESC
            """,
            (person_id,),
        )
        return cur.fetchall()


def focus(conn, person_id, run_id) -> dict | None:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, status, step, topic_text, skill_version, event_answer, scale_answer,
                   model_requested, person_id
            FROM run
            WHERE id = %s AND person_id = %s AND status = 'open'
            """,
            (run_id, person_id),
        )
        row = cur.fetchone()
        if row is None:
            return None
        cur.execute("UPDATE run SET in_window = false WHERE person_id = %s", (person_id,))
        cur.execute(
            "UPDATE run SET in_window = true, updated_at = now() WHERE id = %s",
            (run_id,),
        )
        cur.execute("UPDATE person SET accepting_new = false WHERE id = %s", (person_id,))
    conn.commit()
    return {
        "id": row[0],
        "status": row[1],
        "step": row[2],
        "topic_text": row[3],
        "skill_version": row[4],
        "event_answer": row[5],
        "scale_answer": row[6],
        "model_requested": row[7],
        "person_id": row[8],
    }


def leave_window(conn, person_id) -> None:
    with conn.cursor() as cur:
        cur.execute("UPDATE run SET in_window = false WHERE person_id = %s", (person_id,))
    set_accepting_new(conn, person_id, True)


def continue_prompt(run: dict) -> str:
    if run["step"] == "event":
        return event_prompt(run["topic_text"])
    if run["step"] == "scale":
        return scale_prompt(run["topic_text"])
    return "Продолжаем этот ход. Следующий ответ за тобой, если вопрос ещё открыт. Иначе я снова соберу финал."


def _window(conn, person_id) -> dict | None:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, status, step, topic_text, skill_version, event_answer, scale_answer,
                   model_requested, person_id
            FROM run
            WHERE person_id = %s AND in_window = true
            ORDER BY updated_at DESC
            LIMIT 1
            """,
            (person_id,),
        )
        row = cur.fetchone()
    if row is None:
        return None
    return {
        "id": row[0],
        "status": row[1],
        "step": row[2],
        "topic_text": row[3],
        "skill_version": row[4],
        "event_answer": row[5],
        "scale_answer": row[6],
        "model_requested": row[7],
        "person_id": row[8],
    }


def open_window(conn, person_id) -> dict | None:
    return _window(conn, person_id)


def _mark_answered(cur, run: dict) -> None:
    state = {"last_answered_model": None}
    note_answered(state, run["model_requested"])
    cur.execute(
        "UPDATE person SET last_answered_model = %s WHERE id = %s",
        (state["last_answered_model"], run["person_id"]),
    )


def _unavailable(conn, run: dict, human_text: str | None, message_id: int | None) -> list[dict]:
    state = read_model_state(conn, run["person_id"])
    target = run if run.get("status") == "open" else None
    apply_fallback(state, target)
    write_model_state(conn, run["person_id"], state)
    if target is not None:
        write_open_run_model(conn, run["id"], run["model_requested"])
    with conn.cursor() as cur:
        if human_text is not None:
            _utter(cur, run["id"], "human", human_text, message_id)
        _utter(cur, run["id"], "agent", UNAVAILABLE, None)
    conn.commit()
    return [{"kind": "models", "text": UNAVAILABLE, "current": state["current_model"]}]


def _answers(conn, run: dict) -> tuple[str, str]:
    event_answer = run.get("event_answer") or ""
    scale_answer = run.get("scale_answer") or ""
    if event_answer and scale_answer:
        return event_answer, scale_answer
    with conn.cursor() as cur:
        cur.execute(
            "SELECT event_answer, scale_answer FROM run WHERE id = %s",
            (run["id"],),
        )
        row = cur.fetchone()
    if row:
        return row[0] or event_answer, row[1] or scale_answer
    return event_answer, scale_answer


def _utter(cur, run_id, speaker: str, text: str, telegram_message_id) -> None:
    cur.execute(
        """
        INSERT INTO utterance (id, run_id, speaker, text, telegram_message_id)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (uuid.uuid4(), run_id, speaker, text, telegram_message_id),
    )


def _text(text: str) -> dict:
    return {"kind": "text", "text": text}


def _hidden_profile_observations(
    run: dict,
    event_answer: str,
    scale_answer: str,
    worked: str,
    weak: str,
) -> list[dict]:
    skill_version = str(run.get("skill_version") or "")
    if not skill_version.endswith(".smoke"):
        return []
    signal = STATUS_SHOWING
    weak_low = (weak or "").lower()
    if "слабо" in weak_low and "событ" in weak_low:
        signal = STATUS_WEAK
    evidence = (
        (event_answer or "").strip()
        or (scale_answer or "").strip()
        or (worked or "").strip()
        or (weak or "").strip()
        or str(run.get("topic_text") or "").strip()
    )
    return [
        {
            "characteristic_id": "spotting",
            "signal": signal,
            "quote_or_paraphrase": evidence or "нет цитаты",
        }
    ]
