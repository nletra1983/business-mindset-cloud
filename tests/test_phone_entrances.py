from pathlib import Path


def test_phone_login_is_not_in_the_current_bot():
    schema = Path("app/schema.sql").read_text(encoding="utf-8")
    poll = Path("app/telegram_poll.py").read_text(encoding="utf-8")
    assert "phone_link" not in schema
    assert "settings:phone" not in poll
