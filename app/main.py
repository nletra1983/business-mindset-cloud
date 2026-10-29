from app.channel_http import start_channel_server
from app.db import apply_schema, connect
from app.telegram_poll import poll


def main() -> None:
    conn = connect()
    apply_schema(conn)
    conn.close()
    start_channel_server()
    poll()


if __name__ == "__main__":
    main()
