def save_summary(conn, run_id, worked: str, weak: str, missed: str) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO run_summary (run_id, what_worked, what_weak, what_missed)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (run_id) DO UPDATE
            SET what_worked = EXCLUDED.what_worked,
                what_weak = EXCLUDED.what_weak,
                what_missed = EXCLUDED.what_missed
            """,
            (run_id, worked, weak, missed),
        )
