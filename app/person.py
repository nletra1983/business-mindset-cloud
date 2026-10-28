import uuid
import json

PROFILE_IDLE = "idle"
PROFILE_AWAITING_STRENGTHS = "awaiting_strengths"
PROFILE_AWAITING_WEAKNESSES = "awaiting_weaknesses"
PROFILE_AWAITING_EXTRA_FACT = "awaiting_extra_fact"

STATUS_NOT_OBSERVED = "не наблюдалось"
STATUS_SHOWING = "проявляется"
STATUS_WEAK = "слабо"
STATUS_STABLE = "устойчиво"
STATUS_UNEVEN = "неравномерно"

SIGNAL_STATUSES = (STATUS_SHOWING, STATUS_WEAK)
PROFILE_STATUSES = (
    STATUS_NOT_OBSERVED,
    STATUS_SHOWING,
    STATUS_WEAK,
    STATUS_STABLE,
    STATUS_UNEVEN,
)
HIDDEN_CHARACTERISTICS = (
    "spotting",
    "creativity",
    "valuing",
    "uncertainty",
    "resources",
    "learning",
)
SMOKE_SKILL_SUFFIX = ".smoke"

_STATUS_FIELD_BY_CHARACTERISTIC = {
    "spotting": "spotting_status",
    "creativity": "creativity_status",
    "valuing": "valuing_status",
    "uncertainty": "uncertainty_status",
    "resources": "resources_status",
    "learning": "learning_status",
}


def upsert_from_telegram(conn, telegram_user_id: int, username: str | None) -> dict:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT p.id, p.accepting_new, p.current_model, p.last_answered_model,
                   c.telegram_username
            FROM channel_link c
            JOIN person p ON p.id = c.person_id
            WHERE c.telegram_user_id = %s
            """,
            (telegram_user_id,),
        )
        row = cur.fetchone()
        if row is None:
            person_id = uuid.uuid4()
            link_id = uuid.uuid4()
            cur.execute(
                """
                INSERT INTO person (id, accepting_new)
                VALUES (%s, false)
                RETURNING current_model, last_answered_model
                """,
                (person_id,),
            )
            current_model, last_answered_model = cur.fetchone()
            cur.execute(
                """
                INSERT INTO channel_link
                    (id, person_id, channel, telegram_user_id, telegram_username)
                VALUES (%s, %s, 'telegram', %s, %s)
                """,
                (link_id, person_id, telegram_user_id, username),
            )
            conn.commit()
            return {
                "id": person_id,
                "accepting_new": False,
                "is_new": True,
                "current_model": current_model,
                "last_answered_model": last_answered_model,
            }
        person_id, accepting_new, current_model, last_answered_model, stored_name = row
        if username != stored_name:
            cur.execute(
                """
                UPDATE channel_link
                SET telegram_username = %s, updated_at = now()
                WHERE telegram_user_id = %s
                """,
                (username, telegram_user_id),
            )
        conn.commit()
        return {
            "id": person_id,
            "accepting_new": accepting_new,
            "is_new": False,
            "current_model": current_model,
            "last_answered_model": last_answered_model,
        }


def read_model_state(conn, person_id) -> dict:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT current_model, last_answered_model FROM person WHERE id = %s",
            (person_id,),
        )
        row = cur.fetchone()
    if row is None:
        return {"current_model": "deepseek-chat", "last_answered_model": None}
    return {"current_model": row[0], "last_answered_model": row[1]}


def write_model_state(conn, person_id, state: dict) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE person
            SET current_model = %s, last_answered_model = %s
            WHERE id = %s
            """,
            (state["current_model"], state["last_answered_model"], person_id),
        )


def write_open_run_model(conn, run_id, model_id: str) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE run
            SET model_requested = %s, updated_at = now()
            WHERE id = %s AND status = 'open'
            """,
            (model_id, run_id),
        )


def set_accepting_new(conn, person_id, value: bool) -> None:
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE person SET accepting_new = %s WHERE id = %s",
            (value, person_id),
        )
    conn.commit()


def has_any_run(conn, person_id) -> bool:
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM run WHERE person_id = %s LIMIT 1", (person_id,))
        return cur.fetchone() is not None


def _normalize_facts(raw) -> list[str]:
    if isinstance(raw, list):
        return [str(item) for item in raw if str(item).strip()]
    if isinstance(raw, str):
        text = raw.strip()
        if not text:
            return []
        try:
            parsed = json.loads(text)
        except ValueError:
            return [text]
        if isinstance(parsed, list):
            return [str(item) for item in parsed if str(item).strip()]
        return [text]
    if raw is None:
        return []
    return [str(raw)] if str(raw).strip() else []


def read_kept_profile_texts(conn, person_id) -> list[dict]:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT strengths_text, weaknesses_text, self_facts
            FROM kept_profile_text
            WHERE person_id = %s
            ORDER BY created_at ASC, id ASC
            """,
            (person_id,),
        )
        rows = cur.fetchall()
    texts = []
    for row in rows:
        texts.append(
            {
                "strengths_text": row[0] or "",
                "weaknesses_text": row[1] or "",
                "self_facts": _normalize_facts(row[2]),
            }
        )
    return texts


def read_visible_profile(conn, person_id) -> dict:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT strengths_text, weaknesses_text, self_facts
            FROM visible_profile
            WHERE person_id = %s
            """,
            (person_id,),
        )
        row = cur.fetchone()
    if row is None:
        return {"strengths_text": "", "weaknesses_text": "", "self_facts": []}
    return {
        "strengths_text": row[0] or "",
        "weaknesses_text": row[1] or "",
        "self_facts": _normalize_facts(row[2]),
    }


def write_visible_strengths(conn, person_id, text: str) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO visible_profile (person_id, strengths_text)
            VALUES (%s, %s)
            ON CONFLICT (person_id)
            DO UPDATE SET strengths_text = EXCLUDED.strengths_text, updated_at = now()
            """,
            (person_id, text),
        )


def write_visible_weaknesses(conn, person_id, text: str) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO visible_profile (person_id, weaknesses_text)
            VALUES (%s, %s)
            ON CONFLICT (person_id)
            DO UPDATE SET weaknesses_text = EXCLUDED.weaknesses_text, updated_at = now()
            """,
            (person_id, text),
        )


def append_visible_fact(conn, person_id, fact: str) -> None:
    profile = read_visible_profile(conn, person_id)
    facts = list(profile["self_facts"])
    facts.append(fact)
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO visible_profile (person_id, self_facts)
            VALUES (%s, %s::jsonb)
            ON CONFLICT (person_id)
            DO UPDATE SET self_facts = EXCLUDED.self_facts, updated_at = now()
            """,
            (person_id, json.dumps(facts, ensure_ascii=False)),
        )


def read_profile_edit_step(conn, person_id) -> str:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT step FROM profile_edit_session WHERE person_id = %s",
            (person_id,),
        )
        row = cur.fetchone()
    return row[0] if row and row[0] else PROFILE_IDLE


def write_profile_edit_step(conn, person_id, step: str) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO profile_edit_session (person_id, step)
            VALUES (%s, %s)
            ON CONFLICT (person_id)
            DO UPDATE SET step = EXCLUDED.step, updated_at = now()
            """,
            (person_id, step),
        )


def status_from_signals(signals: list[str]) -> str:
    normalized = [item for item in signals if item in SIGNAL_STATUSES]
    if not normalized:
        return STATUS_NOT_OBSERVED
    if len(normalized) == 1:
        return normalized[0]
    first = normalized[0]
    if all(item == first for item in normalized):
        return STATUS_STABLE
    return STATUS_UNEVEN


def choose_current_focus(statuses: dict[str, str]) -> str:
    for preferred in (STATUS_WEAK, STATUS_UNEVEN, STATUS_NOT_OBSERVED):
        for characteristic_id in HIDDEN_CHARACTERISTICS:
            if statuses.get(characteristic_id) == preferred:
                return characteristic_id
    for characteristic_id in HIDDEN_CHARACTERISTICS:
        if statuses.get(characteristic_id) in PROFILE_STATUSES:
            return characteristic_id
    return "spotting"


def _default_hidden_profile() -> dict[str, str]:
    return {characteristic_id: STATUS_NOT_OBSERVED for characteristic_id in HIDDEN_CHARACTERISTICS}


def _ensure_hidden_profile(conn, person_id) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO hidden_profile (person_id)
            VALUES (%s)
            ON CONFLICT (person_id) DO NOTHING
            """,
            (person_id,),
        )


def _read_hidden_profile_from_cursor(cur, person_id) -> dict[str, str]:
    cur.execute(
        """
        SELECT spotting_status, creativity_status, valuing_status, uncertainty_status,
               resources_status, learning_status, current_focus
        FROM hidden_profile
        WHERE person_id = %s
        """,
        (person_id,),
    )
    row = cur.fetchone()
    statuses = _default_hidden_profile()
    if row is None:
        return statuses
    values = row[:6]
    for index, characteristic_id in enumerate(HIDDEN_CHARACTERISTICS):
        if values[index] in PROFILE_STATUSES:
            statuses[characteristic_id] = values[index]
    return statuses


def read_hidden_profile(conn, person_id) -> dict[str, str]:
    _ensure_hidden_profile(conn, person_id)
    with conn.cursor() as cur:
        statuses = _read_hidden_profile_from_cursor(cur, person_id)
    return statuses


def _signals_for_characteristic(cur, person_id, characteristic_id: str) -> list[str]:
    cur.execute(
        """
        SELECT signal
        FROM hidden_profile_evidence
        WHERE person_id = %s AND characteristic_id = %s
        ORDER BY created_at ASC, id ASC
        """,
        (person_id, characteristic_id),
    )
    rows = cur.fetchall() or []
    return [row[0] for row in rows if row and row[0] in SIGNAL_STATUSES]


def apply_hidden_profile_observations(
    conn,
    person_id,
    run_id,
    exercise_id: str,
    observations: list[dict],
) -> None:
    if not observations:
        return
    _ensure_hidden_profile(conn, person_id)
    applied = False
    with conn.cursor() as cur:
        for raw in observations:
            characteristic_id = str(raw.get("characteristic_id") or "").strip()
            signal = str(raw.get("signal") or "").strip()
            quote = str(raw.get("quote_or_paraphrase") or "").strip() or "нет цитаты"
            if characteristic_id not in HIDDEN_CHARACTERISTICS:
                raise ValueError(f"unsupported characteristic_id: {characteristic_id}")
            if signal not in SIGNAL_STATUSES:
                raise ValueError(f"unsupported signal: {signal}")
            if exercise_id.endswith(SMOKE_SKILL_SUFFIX) and characteristic_id != "spotting":
                continue

            cur.execute(
                """
                SELECT 1
                FROM hidden_profile_evidence
                WHERE run_id = %s AND characteristic_id = %s
                """,
                (run_id, characteristic_id),
            )
            if cur.fetchone() is not None:
                continue

            cur.execute(
                """
                INSERT INTO hidden_profile_evidence (
                    id, person_id, run_id, exercise_id, characteristic_id, signal, quote_or_paraphrase
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    uuid.uuid4(),
                    person_id,
                    run_id,
                    exercise_id,
                    characteristic_id,
                    signal,
                    quote,
                ),
            )

            signals = _signals_for_characteristic(cur, person_id, characteristic_id)
            status = status_from_signals(signals)
            status_field = _STATUS_FIELD_BY_CHARACTERISTIC[characteristic_id]
            cur.execute(
                f"""
                UPDATE hidden_profile
                SET {status_field} = %s, updated_at = now()
                WHERE person_id = %s
                """,
                (status, person_id),
            )
            applied = True

        if not applied:
            return

        statuses = _read_hidden_profile_from_cursor(cur, person_id)
        focus = choose_current_focus(statuses)
        cur.execute(
            """
            UPDATE hidden_profile
            SET current_focus = %s, updated_at = now()
            WHERE person_id = %s
            """,
            (focus, person_id),
        )
