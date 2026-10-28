import uuid


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
