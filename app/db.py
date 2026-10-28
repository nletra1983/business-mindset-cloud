from pathlib import Path

import psycopg

from app.config import database_url

SCHEMA_PATH = Path(__file__).with_name("schema.sql")


def connect():
    url = database_url()
    if url:
        return psycopg.connect(url)
    return psycopg.connect("")


def apply_schema(conn) -> None:
    sql = SCHEMA_PATH.read_text(encoding="utf-8")
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()
