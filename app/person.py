import uuid


def upsert_from_telegram(conn, telegram_user_id: int, username: str | None) -> dict:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT p.id, p.accepting_new, c.telegram_username
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
                "INSERT INTO person (id, accepting_new) VALUES (%s, false)",
                (person_id,),
            )
            cur.execute(
                """
                INSERT INTO channel_link
                    (id, person_id, channel, telegram_user_id, telegram_username)
                VALUES (%s, %s, 'telegram', %s, %s)
                """,
                (link_id, person_id, telegram_user_id, username),
            )
            conn.commit()
            return {"id": person_id, "accepting_new": False, "is_new": True}
        person_id, accepting_new, stored_name = row
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
        return {"id": person_id, "accepting_new": accepting_new, "is_new": False}


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
