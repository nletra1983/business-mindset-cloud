import json
from datetime import date

import pytest

from app import smartcaptcha, web_guest_smoke
from app.get_news_backlog import BACKLOG
from app.web_landing import WINDOWS_LIMIT


class _Cur:
    def __init__(self, store):
        self.store = store
        self._rows = []

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def execute(self, sql, params=None):
        params = params or ()
        q = " ".join(sql.split())
        if q.startswith("INSERT INTO guest_window"):
            wid, sid, transcript = params[:3]
            step = params[3] if len(params) > 3 else 0
            self.store["windows"][wid] = {
                "id": wid,
                "guest_session_id": sid,
                "transcript": json.loads(transcript) if isinstance(transcript, str) else transcript,
                "step_count": step,
                "first_reply_at": None,
                "closed_at": None,
                "cleared_client_at": None,
            }
            return
        if "UPDATE guest_session" in q and "windows_used_today = windows_used_today + 1" in q:
            sid = params[2]
            sess = self.store["sessions"][sid]
            sess["windows_used_today"] += 1
            sess["windows_day"] = params[0]
            sess["current_window_id"] = params[1]
            return
        if q.startswith("SELECT id, guest_session_id, transcript, step_count"):
            row = self.store["windows"].get(params[0])
            self._rows = (
                [
                    (
                        row["id"],
                        row["guest_session_id"],
                        row["transcript"],
                        row["step_count"],
                        row["first_reply_at"],
                        row["closed_at"],
                    )
                ]
                if row
                else []
            )
            return
        if "SET transcript" in q and "first_reply_at = COALESCE" in q:
            transcript, step, _ts, wid = params
            row = self.store["windows"][wid]
            row["transcript"] = json.loads(transcript)
            row["step_count"] = step
            if row["first_reply_at"] is None:
                row["first_reply_at"] = _ts
            return
        if "SET transcript" in q:
            transcript, step, wid = params
            row = self.store["windows"][wid]
            row["transcript"] = json.loads(transcript)
            row["step_count"] = step
            return
        if "SET closed_at" in q:
            wid = params[0]
            self.store["windows"][wid]["closed_at"] = "now"
            return
        if "SET cleared_client_at" in q:
            wid = params[0]
            self.store["windows"][wid]["cleared_client_at"] = "now"
            return
        if "current_window_id = NULL" in q:
            sid = params[0]
            self.store["sessions"][sid]["current_window_id"] = None
            return

    def fetchone(self):
        return self._rows[0] if self._rows else None


class FakeConn:
    def __init__(self):
        self.store = {"sessions": {}, "windows": {}}

    def cursor(self):
        return _Cur(self.store)


@pytest.fixture(autouse=True)
def _skill_prompt(monkeypatch):
    def fake(model_id, messages):
        assert messages[0]["role"] == "system"
        assert "business-idea-from-news.smoke" in messages[0]["content"]
        return ("Вопрос по этой новости, как думаешь?", model_id)

    monkeypatch.setattr(web_guest_smoke, "complete", fake)


def _session(conn, used=0):
    sid = "11111111-1111-1111-1111-111111111111"
    sess = {
        "id": sid,
        "windows_used_today": used,
        "windows_limit": WINDOWS_LIMIT,
        "current_window_id": None,
        "windows_day": date.today(),
        "new_cookie": False,
    }
    conn.store["sessions"][sid] = sess
    return sess


def test_pick_news_from_backlog():
    fact = web_guest_smoke.pick_news_fact(BACKLOG)
    assert fact
    assert len(fact) > 10


def test_start_rejects_blank_own_fact():
    conn = FakeConn()
    sess = _session(conn)
    status, body = web_guest_smoke.start_window(conn, sess, fact="https://example.com", use_news=False)
    assert status == 400
    assert body["error"] == "blank_fact"


def test_start_own_fact_and_limit():
    conn = FakeConn()
    sess = _session(conn)
    status, body = web_guest_smoke.start_window(
        conn, sess, fact="ФНС начала проверять доходы от аренды за рубежом", use_news=False
    )
    assert status == 200
    assert body["step_count"] == 0
    assert "agent_reply" in body
    assert sess["windows_used_today"] == 1

    for _ in range(2):
        st, _ = web_guest_smoke.start_window(
            conn, sess, fact="Ozon открыл ещё пункты выдачи в малых городах", use_news=False
        )
        assert st == 200
    status, body = web_guest_smoke.start_window(
        conn, sess, fact="Ставка по вкладам выросла в топ-10 банков", use_news=False
    )
    assert status == 403
    assert body["error"] == "window_limit"


def test_message_without_captcha_does_not_call_model(monkeypatch):
    conn = FakeConn()
    sess = _session(conn)
    web_guest_smoke.start_window(
        conn, sess, fact="Бюджет ОМС вырос за двадцать лет почти в 23 раза", use_news=False
    )
    called = {"n": 0}

    def boom(*_a, **_k):
        called["n"] += 1
        raise AssertionError("model must not run")

    monkeypatch.setattr(web_guest_smoke, "complete", boom)
    status, body = web_guest_smoke.post_message(
        conn,
        sess,
        text="Изменились правила финансирования медицины",
        captcha_token="",
        verify=lambda _t, _ip: False,
    )
    assert status == 403
    assert body["error"] == "captcha_failed"
    assert called["n"] == 0


def test_three_steps_then_gate(monkeypatch):
    conn = FakeConn()
    sess = _session(conn)
    web_guest_smoke.start_window(
        conn,
        sess,
        fact="Розничная цена бензина снижалась несколько недель подряд",
        use_news=False,
    )

    s1, b1 = web_guest_smoke.post_message(
        conn,
        sess,
        text="Снизилась розничная цена топлива — изменилась доступность",
        captcha_token="ok",
        verify=lambda _t, _ip: True,
    )
    assert s1 == 200
    assert b1["step_count"] == 1
    assert b1["gate_required"] is False

    s2, b2 = web_guest_smoke.post_message(
        conn,
        sess,
        text="Водители и АЗС в регионах, с прошлой зимы",
        captcha_token="ok",
        verify=lambda _t, _ip: True,
    )
    assert s2 == 200
    assert b2["step_count"] == 2
    assert b2["gate_required"] is False

    s3, b3 = web_guest_smoke.post_message(
        conn,
        sess,
        text="Спрошу у десяти водителей на заправке",
        captcha_token="ok",
        verify=lambda _t, _ip: True,
    )
    assert s3 == 200
    assert b3["gate_required"] is True
    assert b3["step_count"] == 3
    assert "как думаешь?" in b3["agent_reply"]

    status, body = web_guest_smoke.post_message(
        conn,
        sess,
        text="ещё шаг",
        captcha_token="ok",
        verify=lambda _t, _ip: True,
    )
    assert status == 403
    assert body.get("gate_required") or body.get("error") == "gate_required"


def test_clear_resets_current_window_only():
    conn = FakeConn()
    sess = _session(conn)
    st, body = web_guest_smoke.start_window(
        conn, sess, fact="Пункты выдачи Ozon превысили 94 тысячи", use_news=False
    )
    assert st == 200
    wid = body["window_id"]
    status, cleared = web_guest_smoke.clear_window(conn, sess)
    assert status == 200
    assert cleared["cleared"] is True
    assert sess["current_window_id"] is None
    assert conn.store["windows"][wid]["cleared_client_at"] == "now"
    assert conn.store["windows"][wid]["transcript"]  # server copy kept


def test_smartcaptcha_verify_fail_closed_without_secret(monkeypatch):
    monkeypatch.delenv("SMARTCAPTCHA_SERVER_KEY", raising=False)
    assert smartcaptcha.verify_token("any-token") is False
