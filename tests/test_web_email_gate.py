import json
from datetime import date

from app import web_email_gate
from app.channel_api import APP_PREFIX, dispatch
from app.entrances import MemoryBook, begin_email_login, confirm_email_login
from app.mail import mail_text
from app.sessions import MemorySessionStore
from app.web_landing import WINDOWS_LIMIT


class _Cur:
    def __init__(self, store):
        self.store = store
        self._rows = []

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def execute(self, sql, params=None):
        params = params or ()
        q = " ".join(sql.split())
        if "FROM email_link WHERE email" in q and "SELECT person_id" in q:
            link = self.store["emails"].get(params[0])
            self._rows = [(link["person_id"],)] if link else []
            return
        if q.startswith("UPDATE email_link"):
            return
        if q.startswith("INSERT INTO person"):
            self.store["persons"][params[0]] = {"id": params[0]}
            return
        if q.startswith("INSERT INTO email_link"):
            self.store["emails"][params[2]] = {
                "id": params[0],
                "person_id": params[1],
                "email": params[2],
                "confirmed": True,
            }
            return
        if q.startswith("INSERT INTO run"):
            self.store["runs"][params[0]] = {
                "id": params[0],
                "person_id": params[1],
                "topic": params[3],
                "status": "open",
                "utterances": [],
            }
            return
        if q.startswith("INSERT INTO utterance") and "), (" in q:
            run = self.store["runs"].get(params[1])
            if run is not None and len(params) >= 6:
                run["utterances"].append({"speaker": "human", "text": params[2]})
                run["utterances"].append({"speaker": "agent", "text": params[5]})
            return
        if q.startswith("INSERT INTO utterance"):
            run = self.store["runs"].get(params[1])
            if run is not None:
                run["utterances"].append({"speaker": params[2], "text": params[3]})
            return
        if "UPDATE guest_session" in q and "continue_run_id" in q:
            sid = params[5]
            sess = self.store["sessions"][sid]
            sess["person_id"] = params[0]
            sess["last_email"] = params[1]
            sess["continue_run_id"] = params[2]
            sess["continue_transcript"] = json.loads(params[3])
            sess["email_steps_done"] = params[4]
            return
        if "FROM guest_session WHERE id" in q and "continue_run_id" in q:
            sess = self.store["sessions"].get(params[0])
            if not sess or not sess.get("continue_run_id"):
                self._rows = []
            else:
                self._rows = [
                    (
                        sess.get("person_id"),
                        sess.get("last_email"),
                        sess.get("continue_run_id"),
                        sess.get("email_steps_done", 0),
                        sess.get("continue_transcript", []),
                    )
                ]
            return
        if "FROM guest_session" in q and "last_email =" in q:
            email = params[0]
            found = None
            for sess in self.store["sessions"].values():
                if sess.get("last_email") == email and sess.get("continue_run_id"):
                    found = sess
                    break
            if not found:
                self._rows = []
            else:
                self._rows = [
                    (
                        found["id"],
                        found.get("person_id"),
                        found.get("last_email"),
                        found.get("continue_run_id"),
                        found.get("email_steps_done", 0),
                        found.get("continue_transcript", []),
                    )
                ]
            return
        if "SELECT id, guest_session_id, transcript" in q:
            row = self.store["windows"].get(params[0])
            self._rows = (
                [
                    (
                        row["id"],
                        row["guest_session_id"],
                        row["transcript"],
                        row["step_count"],
                        row.get("first_reply_at"),
                        row.get("closed_at"),
                    )
                ]
                if row
                else []
            )
            return
        if q.startswith("UPDATE run SET status"):
            run = self.store["runs"].get(params[0])
            if run:
                run["status"] = "completed"
            return
        if "FROM day2_mail" in q and "status = 'pending'" in q:
            self._rows = []
            return
        if q.startswith("INSERT INTO day2_mail"):
            self.store.setdefault("day2", []).append({"id": params[0], "email": params[1]})
            return
        if "INSERT INTO utterance" in q and "human" in q:
            # dual insert: id, run, human text, id, run, agent text
            if len(params) >= 6:
                run = self.store["runs"].get(params[1])
                if run is not None:
                    run["utterances"].append({"speaker": "human", "text": params[2]})
                    run["utterances"].append({"speaker": "agent", "text": params[5]})
            return

    def fetchone(self):
        return self._rows[0] if self._rows else None


class FakeConn:
    def __init__(self):
        self.store = {
            "sessions": {},
            "windows": {},
            "persons": {},
            "emails": {},
            "runs": {},
        }

    def cursor(self):
        return _Cur(self.store)


def _session(conn, wid=None):
    sid = "22222222-2222-2222-2222-222222222222"
    sess = {
        "id": sid,
        "windows_used_today": 1,
        "windows_limit": WINDOWS_LIMIT,
        "current_window_id": wid,
        "windows_day": date.today(),
        "person_id": None,
        "new_cookie": False,
    }
    conn.store["sessions"][sid] = {
        "id": sid,
        "person_id": None,
        "last_email": None,
        "continue_run_id": None,
        "email_steps_done": 0,
        "continue_transcript": [],
    }
    return sess


def _seed_guest_window(conn, sess, messages):
    wid = "33333333-3333-3333-3333-333333333333"
    sess["current_window_id"] = wid
    conn.store["windows"][wid] = {
        "id": wid,
        "guest_session_id": sess["id"],
        "transcript": {
            "topic": "Цена бензина снижалась несколько недель",
            "phase": "done",
            "messages": messages,
            "gate_shown": True,
        },
        "step_count": 3,
        "first_reply_at": "now",
        "closed_at": "now",
    }
    return wid


def test_invalid_email_rejected():
    conn = FakeConn()
    sess = _session(conn)
    status, body = web_email_gate.submit_email(conn, sess, "not-an-email")
    assert status == 400
    assert body["error"] == "invalid_email"


def test_email_continue_without_code_keeps_transcript():
    conn = FakeConn()
    sess = _session(conn)
    guest_msgs = [
        {"role": "agent", "text": "вопрос 1"},
        {"role": "human", "text": "ответ 1"},
        {"role": "agent", "text": "вопрос 2"},
    ]
    _seed_guest_window(conn, sess, guest_msgs)
    status, body = web_email_gate.submit_email(conn, sess, "guest@example.com")
    assert status == 200
    assert body["code_required"] is False
    assert body["email_steps_done"] == 0
    texts = [m["text"] for m in body["messages"]]
    assert "ответ 1" in texts
    assert body["agent_reply"] in texts
    run = next(iter(conn.store["runs"].values()))
    assert any(u["text"] == "ответ 1" for u in run["utterances"])


def test_three_email_steps_then_payment_flag():
    conn = FakeConn()
    sess = _session(conn)
    _seed_guest_window(conn, sess, [{"role": "agent", "text": "q"}])
    web_email_gate.submit_email(conn, sess, "cont@example.com")
    for i in range(3):
        status, body = web_email_gate.post_continue_message(conn, sess, text=f"шаг {i+1}")
        assert status == 200
        assert body["email_steps_done"] == i + 1
    assert body["payment_gate"] is True
    status, body = web_email_gate.post_continue_message(conn, sess, text="ещё")
    assert status == 403
    assert body["payment_gate"] is True


def test_resume_by_same_email():
    conn = FakeConn()
    sess = _session(conn)
    _seed_guest_window(conn, sess, [{"role": "human", "text": "было"}])
    web_email_gate.submit_email(conn, sess, "back@example.com")
    web_email_gate.post_continue_message(conn, sess, text="после email")
    # First cookie session must keep continue_* for lookup by last_email.
    assert conn.store["sessions"][sess["id"]]["last_email"] == "back@example.com"

    other_id = "44444444-4444-4444-4444-444444444444"
    other = {
        "id": other_id,
        "windows_used_today": 0,
        "windows_limit": WINDOWS_LIMIT,
        "current_window_id": None,
        "windows_day": date.today(),
        "person_id": None,
        "new_cookie": True,
    }
    conn.store["sessions"][other_id] = {
        "id": other_id,
        "person_id": None,
        "last_email": None,
        "continue_run_id": None,
        "email_steps_done": 0,
        "continue_transcript": [],
    }
    status, body = web_email_gate.resume_email(conn, other, "back@example.com")
    assert status == 200
    assert body["resumed"] is True
    assert body["email_steps_done"] == 1
    assert any(m.get("text") == "после email" for m in body["messages"])


def test_app_email_login_still_requires_code():
    book = MemoryBook(mail=lambda _email, _text: None)
    sessions = MemorySessionStore()
    asked = begin_email_login(book, "app@example.com")
    assert asked["ok"] is True
    bad = confirm_email_login(book, "app@example.com", "0000")
    assert bad["ok"] is False
    code = book.read_code("email", "app@example.com")["code"]
    # wrong code via channel API
    denied = dispatch(
        "POST",
        f"{APP_PREFIX}/auth/email/confirm",
        {},
        {"email": "app@example.com", "code": "1111" if code != "1111" else "2222"},
        book=book,
        sessions=sessions,
    )
    assert denied["ok"] is False
    assert "session_secret" not in denied["body"]
    good = dispatch(
        "POST",
        f"{APP_PREFIX}/auth/email/confirm",
        {},
        {"email": "app@example.com", "code": code},
        book=book,
        sessions=sessions,
    )
    assert good["ok"] is True
    assert good["body"]["session_secret"]
    assert book.sent[0] == mail_text(code)
