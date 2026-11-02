from datetime import datetime, timedelta, timezone

from app import web_day2_mail
from app.web_day2_mail import BODY, SUBJECT


class _Cur:
    def __init__(self, store):
        self.store = store
        self._rows = []
        self.rowcount = 0

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def execute(self, sql, params=None):
        params = params or ()
        q = " ".join(sql.split())
        if "SELECT id FROM day2_mail" in q and "status = 'pending'" in q and "due_at" not in q:
            email = params[0]
            for row in self.store["mails"]:
                if row["email"] == email and row["status"] == "pending":
                    self._rows = [(row["id"],)]
                    return
            self._rows = []
            return
        if q.startswith("INSERT INTO day2_mail"):
            self.store["mails"].append(
                {
                    "id": params[0],
                    "email": params[1],
                    "person_id": params[2],
                    "run_id": params[3],
                    "due_at": params[4],
                    "status": "pending",
                    "sent_at": None,
                }
            )
            self.rowcount = 1
            return
        if "SELECT id, email FROM day2_mail" in q:
            now = params[0]
            self._rows = [
                (m["id"], m["email"])
                for m in self.store["mails"]
                if m["status"] == "pending" and m["due_at"] <= now
            ]
            return
        if "SET status = 'sent'" in q:
            now, mail_id = params
            for m in self.store["mails"]:
                if m["id"] == mail_id:
                    m["status"] = "sent"
                    m["sent_at"] = now
            return
        if "SET status = 'failed'" in q:
            mail_id = params[0]
            for m in self.store["mails"]:
                if m["id"] == mail_id:
                    m["status"] = "failed"
            return

    def fetchone(self):
        return self._rows[0] if self._rows else None

    def fetchall(self):
        return list(self._rows)


class FakeConn:
    def __init__(self):
        self.store = {"mails": []}

    def cursor(self):
        return _Cur(self.store)


def test_enqueue_once_per_email():
    conn = FakeConn()
    a = web_day2_mail.enqueue_day2(conn, email="a@example.com", person_id="p1", run_id="r1")
    b = web_day2_mail.enqueue_day2(conn, email="a@example.com", person_id="p1", run_id="r1")
    assert a and a == b
    assert len(conn.store["mails"]) == 1
    assert conn.store["mails"][0]["due_at"] > datetime.now(timezone.utc)


def test_process_due_sends_without_transcript():
    conn = FakeConn()
    mid = web_day2_mail.enqueue_day2(conn, email="b@example.com", person_id=None, run_id=None)
    conn.store["mails"][0]["due_at"] = datetime.now(timezone.utc) - timedelta(minutes=1)
    sent = []

    def fake_send(email, subject, text):
        sent.append((email, subject, text))

    n = web_day2_mail.process_due(conn, send=fake_send)
    assert n == 1
    assert len(sent) == 1
    assert sent[0][0] == "b@example.com"
    assert sent[0][1] == SUBJECT
    body = sent[0][2]
    assert body == BODY
    assert "ПОЛУЧИЛОСЬ" not in body
    assert "ответ" not in body.lower() or "разбор" in body.lower()
    # explicit: no dialogue markers from smoke
    for banned in ("СЛАБО:", "НЕХВАТАЕТ:", "Факт:", "question 1"):
        assert banned not in body
    assert conn.store["mails"][0]["status"] == "sent"
    assert conn.store["mails"][0]["id"] == mid


def test_body_has_no_run_transcript_fixture():
    fixture_lines = [
        "Факт: цена бензина",
        "СЛАБО: мало групп",
        "human: водители на АЗС",
    ]
    body = web_day2_mail.day2_body()
    for line in fixture_lines:
        assert line not in body
