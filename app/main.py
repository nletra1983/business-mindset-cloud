from app.channel_http import start_channel_server
from app.db import apply_schema, connect
from app.get_news_backlog import mark_refresh_needed, start_backlog_ticker
from app.telegram_poll import poll
from app.web_day2_mail import start_day2_ticker


def main() -> None:
    conn = connect()
    apply_schema(conn)
    conn.close()
    mark_refresh_needed()
    start_backlog_ticker()
    start_day2_ticker()
    start_channel_server()
    poll()


if __name__ == "__main__":
    main()
