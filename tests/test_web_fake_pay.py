from decimal import Decimal

from app import web_fake_pay
from app.web_fake_pay import CONFIRMATION, DEFAULT_AMOUNT, PAYWALL_COPY


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
        if "FROM guest_session WHERE id" in q:
            sess = self.store["sessions"].get(params[0], {})
            if "email_steps_done" in q:
                self._rows = [
                    (
                        sess.get("last_email"),
                        sess.get("person_id"),
                        sess.get("email_steps_done", 0),
                    )
                ]
            else:
                self._rows = [(sess.get("last_email"), sess.get("person_id"))]
            return
        if "FROM fake_payment_intent" in q and "person_id" in q:
            pid = params[0]
            rows = [i for i in self.store["intents"] if i.get("person_id") == pid]
            rows.sort(key=lambda x: x["created_at"], reverse=True)
            self._rows = [(rows[0]["amount_rub"],)] if rows else []
            return
        if "FROM fake_payment_intent" in q and "email" in q:
            email = params[0]
            rows = [i for i in self.store["intents"] if i.get("email") == email]
            rows.sort(key=lambda x: x["created_at"], reverse=True)
            self._rows = [(rows[0]["amount_rub"],)] if rows else []
            return
        if q.startswith("INSERT INTO fake_payment_intent"):
            self.store["intents"].append(
                {
                    "id": params[0],
                    "person_id": params[1],
                    "email": params[2],
                    "amount_rub": params[3],
                    "created_at": len(self.store["intents"]) + 1,
                }
            )
            return

    def fetchone(self):
        return self._rows[0] if self._rows else None


class FakeConn:
    def __init__(self):
        self.store = {"sessions": {}, "intents": []}

    def cursor(self):
        return _Cur(self.store)


def test_paywall_copy_and_default_100():
    conn = FakeConn()
    sid = "55555555-5555-5555-5555-555555555555"
    conn.store["sessions"][sid] = {
        "last_email": "p@example.com",
        "person_id": "p1",
        "email_steps_done": 3,
    }
    status, body = web_fake_pay.paywall_state(conn, {"id": sid, "person_id": "p1"})
    assert status == 200
    assert body["copy"] == PAYWALL_COPY
    assert body["default_amount"] == float(DEFAULT_AMOUNT)
    assert body["has_prior_amount"] is False
    assert "регулярно и на результат" in body["copy"]


def test_last_amount_restored_and_click_not_charged():
    conn = FakeConn()
    sid = "66666666-6666-6666-6666-666666666666"
    conn.store["sessions"][sid] = {
        "last_email": "p2@example.com",
        "person_id": "p2",
        "email_steps_done": 3,
    }
    session = {"id": sid, "person_id": "p2"}
    st, body = web_fake_pay.record_click(conn, session, 250)
    assert st == 200
    assert body["charged"] is False
    assert body["confirmation"] == CONFIRMATION
    assert body["amount"] == 250.0

    status, wall = web_fake_pay.paywall_state(conn, session)
    assert status == 200
    assert wall["default_amount"] == 250.0
    assert wall["has_prior_amount"] is True


def test_invalid_amount_rejected():
    conn = FakeConn()
    sid = "77777777-7777-7777-7777-777777777777"
    conn.store["sessions"][sid] = {"last_email": "x@y.z", "person_id": None}
    status, body = web_fake_pay.record_click(conn, {"id": sid}, 0)
    assert status == 400
    assert body["error"] == "invalid_amount"


def test_parse_amount():
    assert web_fake_pay.parse_amount("100") == Decimal("100.00")
    assert web_fake_pay.parse_amount("-1") is None
    assert web_fake_pay.parse_amount("") is None
