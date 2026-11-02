from datetime import datetime, timedelta
from pathlib import Path

from app.get_news_backlog import BACKLOG, PERIOD_HOURS, backlog_is_stale, mark_refresh_needed
from app import web_landing


def test_static_index_exists():
    path = web_landing.static_path("/")
    assert path is not None
    assert path.name == "index.html"
    assert path.is_file()


def test_static_css():
    path = web_landing.static_path("/web/styles.css")
    assert path is not None
    assert path.suffix == ".css"


def test_cookie_roundtrip_parse():
    header = web_landing.set_guest_cookie_header("11111111-1111-1111-1111-111111111111")
    assert "gbi_guest=" in header
    assert "HttpOnly" in header
    got = web_landing.parse_cookie_guest_id(f"gbi_guest=11111111-1111-1111-1111-111111111111; other=1")
    assert got == "11111111-1111-1111-1111-111111111111"


def test_invalid_cookie_ignored():
    assert web_landing.parse_cookie_guest_id("gbi_guest=not-a-uuid") is None


def test_backlog_period_is_four_hours():
    assert PERIOD_HOURS == 4


def test_backlog_missing_is_stale(tmp_path, monkeypatch):
    missing = tmp_path / "missing.md"
    monkeypatch.setattr("app.get_news_backlog.BACKLOG", missing)
    assert backlog_is_stale() is True
    assert mark_refresh_needed() is True


def test_backlog_fresh_not_stale(tmp_path, monkeypatch):
    f = tmp_path / "get-news-backlog.md"
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    f.write_text(f"Создан: {now}\n", encoding="utf-8")
    monkeypatch.setattr("app.get_news_backlog.BACKLOG", f)
    assert backlog_is_stale() is False


def test_backlog_old_is_stale(tmp_path, monkeypatch):
    f = tmp_path / "get-news-backlog.md"
    old = (datetime.now() - timedelta(hours=5)).strftime("%Y-%m-%d %H:%M")
    f.write_text(f"Создан: {old}\n", encoding="utf-8")
    monkeypatch.setattr("app.get_news_backlog.BACKLOG", f)
    assert backlog_is_stale() is True


def test_app_prefix_unchanged():
    from app.channel_api import APP_PREFIX

    assert APP_PREFIX == "/app/v1"


def test_smartcaptcha_env_file_wired():
    compose = Path("docker-compose.yml").read_text(encoding="utf-8")
    assert "smartcaptcha.env" in compose
    assert "YANDEX_METRIKA_COUNTER_ID" in compose


def test_mail_env_still_present():
    compose = Path("docker-compose.yml").read_text(encoding="utf-8")
    assert "mail.env" in compose
