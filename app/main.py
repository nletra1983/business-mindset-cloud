from app.db import apply_schema, connect
from app.telegram_poll import poll


def main() -> None:
    conn = connect()
    apply_schema(conn)
    conn.close()
    poll()


if __name__ == "__main__":
    main()
