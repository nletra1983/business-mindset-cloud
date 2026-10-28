import secrets
import uuid

from psycopg.types.json import Json

from app.person import HIDDEN_CHARACTERISTICS, STATUS_NOT_OBSERVED, STATUS_UNEVEN
from app.sms import sms_text


def normalize_phone(raw: str) -> str | None:
    digits = "".join(ch for ch in (raw or "") if ch.isdigit())
    if len(digits) < 10 or len(digits) > 15:
        return None
    return digits


def normalize_telegram_id(raw: str) -> str | None:
    text = (raw or "").strip()
    if text.isdigit() and 1 <= len(text) <= 15:
        return text
    return None


def new_code() -> str:
    return f"{secrets.randbelow(10000):04d}"


def merged_marks(left: dict, right: dict) -> dict:
    result = {}
    for key in HIDDEN_CHARACTERISTICS:
        first = left.get(key) or STATUS_NOT_OBSERVED
        second = right.get(key) or STATUS_NOT_OBSERVED
        result[key] = first if first == second else STATUS_UNEVEN
    return result


def begin_phone_login(book, raw: str) -> dict:
    phone = normalize_phone(raw)
    if phone is None:
        return {"ok": False, "reason": "phone"}
    code = new_code()
    try:
        book.deliver_sms(phone, sms_text(code))
    except Exception:
        return {"ok": False, "reason": "sms"}
    book.save_code("phone", phone, code, "login", None)
    return {"ok": True, "phone": phone}


def confirm_phone_login(book, raw: str, code: str) -> dict:
    phone = normalize_phone(raw)
    saved = book.read_code("phone", phone) if phone else None
    if saved is None or saved["purpose"] != "login" or saved["code"] != (code or "").strip():
        return {"ok": False, "created": False}
    owner = book.owner("phone", phone)
    if owner is not None:
        return {"ok": True, "person_id": owner, "created": False}
    person_id = book.create_person()
    book.bind(person_id, "phone", phone)
    return {"ok": True, "person_id": person_id, "created": True}


def begin_settings_phone(book, person_id, raw: str) -> dict:
    phone = normalize_phone(raw)
    if phone is None:
        return {"ok": False, "reason": "phone"}
    code = new_code()
    try:
        book.deliver_sms(phone, sms_text(code))
    except Exception:
        return {"ok": False, "reason": "sms"}
    book.save_code("phone", phone, code, "settings", person_id)
    book.stage(person_id, "phone", phone)
    return {"ok": True}


def begin_settings_telegram(book, person_id, raw: str) -> dict:
    telegram_id = normalize_telegram_id(raw)
    if telegram_id is None:
        return {"ok": False, "reason": "telegram"}
    code = new_code()
    try:
        book.deliver_telegram(telegram_id, sms_text(code))
    except Exception:
        return {"ok": False, "reason": "delivery"}
    book.save_code("telegram", telegram_id, code, "settings", person_id)
    book.stage(person_id, "telegram", telegram_id)
    return {"ok": True}


def confirm_settings(book, person_id, kind: str, code: str) -> dict:
    destination = book.staged_destination(person_id, kind)
    saved = book.read_code(kind, destination) if destination else None
    given = (code or "").strip()
    if (
        saved is None
        or saved["purpose"] != "settings"
        or str(saved["requester"]) != str(person_id)
        or saved["code"] != given
    ):
        return {"ok": False, "merged": False}
    book.mark_staged_confirmed(person_id, kind)
    if book.has_unconfirmed_stage(person_id):
        return {"ok": True, "merged": False, "waiting": True}
    pairs = book.pop_stage(person_id)
    absorbed = False
    for staged_kind, staged_destination in pairs:
        other = book.owner(staged_kind, staged_destination)
        if other is not None and str(other) != str(person_id):
            book.absorb(person_id, other)
            absorbed = True
        book.bind(person_id, staged_kind, staged_destination)
    return {"ok": True, "merged": absorbed, "waiting": False}


def confirm_any_settings_code(book, person_id, code: str) -> dict:
    for kind in book.unconfirmed_kinds(person_id):
        result = confirm_settings(book, person_id, kind, code)
        if result["ok"]:
            return result
    return {"ok": False, "merged": False}


class MemoryBook:
    def __init__(self, sms, telegram=None):
        self._sms = sms
        self._telegram = telegram or (lambda _destination, _text: None)
        self.people: dict[str, dict] = {}
        self.phone_of: dict[str, str] = {}
        self.telegram_of: dict[str, str] = {}
        self.codes: dict[tuple[str, str], dict] = {}
        self.staged: dict[str, dict[str, dict]] = {}
        self.sent: list[str] = []

    def add_person(self, *, phone=None, telegram=None, runs=None, marks=None, profile=None) -> str:
        person_id = str(uuid.uuid4())
        text = profile or {"strengths_text": "", "weaknesses_text": "", "self_facts": []}
        self.people[person_id] = {
            "runs": list(runs or []),
            "marks": {key: STATUS_NOT_OBSERVED for key in HIDDEN_CHARACTERISTICS},
            "profiles": [dict(text)],
        }
        if marks:
            self.people[person_id]["marks"].update(marks)
        if phone:
            self.phone_of[phone] = person_id
        if telegram:
            self.telegram_of[str(telegram)] = person_id
        return person_id

    def deliver_sms(self, phone: str, text: str) -> None:
        self._sms(phone, text)
        self.sent.append(text)

    def deliver_telegram(self, destination: str, text: str) -> None:
        self._telegram(destination, text)

    def save_code(self, kind, destination, code, purpose, requester) -> None:
        self.codes[(kind, destination)] = {
            "code": code,
            "purpose": purpose,
            "requester": None if requester is None else str(requester),
        }

    def read_code(self, kind, destination):
        if destination is None:
            return None
        return self.codes.get((kind, destination))

    def owner(self, kind, destination):
        if kind == "phone":
            return self.phone_of.get(destination)
        return self.telegram_of.get(str(destination))

    def create_person(self) -> str:
        return self.add_person()

    def bind(self, person_id, kind, destination) -> None:
        person_id = str(person_id)
        if kind == "phone":
            self.phone_of[destination] = person_id
        else:
            self.telegram_of[str(destination)] = person_id

    def stage(self, person_id, kind, destination) -> None:
        bucket = self.staged.setdefault(str(person_id), {})
        bucket[kind] = {"destination": destination, "confirmed": False}

    def staged_destination(self, person_id, kind):
        item = self.staged.get(str(person_id), {}).get(kind)
        if item is None or item["confirmed"]:
            return None
        return item["destination"]

    def mark_staged_confirmed(self, person_id, kind) -> None:
        self.staged[str(person_id)][kind]["confirmed"] = True

    def has_unconfirmed_stage(self, person_id) -> bool:
        return any(not item["confirmed"] for item in self.staged.get(str(person_id), {}).values())

    def unconfirmed_kinds(self, person_id) -> list[str]:
        return [
            kind
            for kind, item in self.staged.get(str(person_id), {}).items()
            if not item["confirmed"]
        ]

    def pop_stage(self, person_id) -> list[tuple[str, str]]:
        bucket = self.staged.pop(str(person_id), {})
        return [(kind, item["destination"]) for kind, item in bucket.items()]

    def absorb(self, survivor_id, other_id) -> None:
        survivor_id = str(survivor_id)
        other_id = str(other_id)
        if survivor_id == other_id or other_id not in self.people:
            return
        survivor = self.people[survivor_id]
        other = self.people.pop(other_id)
        survivor["runs"].extend(other["runs"])
        survivor["marks"] = merged_marks(survivor["marks"], other["marks"])
        survivor["profiles"].extend(other["profiles"])
        for phone, person_id in list(self.phone_of.items()):
            if person_id == other_id:
                self.phone_of[phone] = survivor_id
        for telegram_id, person_id in list(self.telegram_of.items()):
            if person_id == other_id:
                self.telegram_of[telegram_id] = survivor_id

    def phone_label(self, person_id) -> str | None:
        for phone, owner in self.phone_of.items():
            if owner == str(person_id):
                return phone
        return None


class SqlBook:
    def __init__(self, conn, sms=None, telegram=None):
        self.conn = conn
        self._sms = sms
        self._telegram = telegram

    def deliver_sms(self, phone: str, text: str) -> None:
        from app.sms import send_code

        (self._sms or send_code)(phone, text)

    def deliver_telegram(self, destination: str, text: str) -> None:
        if self._telegram is not None:
            self._telegram(destination, text)
            return
        from app.config import telegram_base, telegram_token

        url = f"{telegram_base()}/bot{telegram_token()}/sendMessage"
        import httpx

        response = httpx.post(
            url,
            json={"chat_id": int(destination), "text": text},
            timeout=10.0,
        )
        response.raise_for_status()

    def save_code(self, kind, destination, code, purpose, requester) -> None:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO link_code (id, kind, destination, code, purpose, requester_person_id)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (kind, destination)
                DO UPDATE SET code = EXCLUDED.code, purpose = EXCLUDED.purpose,
                              requester_person_id = EXCLUDED.requester_person_id,
                              created_at = now()
                """,
                (uuid.uuid4(), kind, destination, code, purpose, requester),
            )

    def read_code(self, kind, destination):
        if destination is None:
            return None
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT code, purpose, requester_person_id
                FROM link_code
                WHERE kind = %s AND destination = %s
                """,
                (kind, destination),
            )
            row = cur.fetchone()
        if row is None:
            return None
        return {"code": row[0], "purpose": row[1], "requester": row[2]}

    def owner(self, kind, destination):
        with self.conn.cursor() as cur:
            if kind == "phone":
                cur.execute(
                    """
                    SELECT person_id FROM phone_link
                    WHERE phone = %s AND confirmed
                    """,
                    (destination,),
                )
            else:
                cur.execute(
                    """
                    SELECT person_id FROM channel_link
                    WHERE telegram_user_id = %s
                    """,
                    (int(destination),),
                )
            row = cur.fetchone()
        return None if row is None else row[0]

    def create_person(self):
        person_id = uuid.uuid4()
        with self.conn.cursor() as cur:
            cur.execute(
                "INSERT INTO person (id, accepting_new) VALUES (%s, false)",
                (person_id,),
            )
        return person_id

    def bind(self, person_id, kind, destination) -> None:
        with self.conn.cursor() as cur:
            if kind == "phone":
                cur.execute(
                    """
                    INSERT INTO phone_link (id, person_id, phone, confirmed)
                    VALUES (%s, %s, %s, true)
                    ON CONFLICT (phone)
                    DO UPDATE SET person_id = EXCLUDED.person_id, confirmed = true, updated_at = now()
                    """,
                    (uuid.uuid4(), person_id, destination),
                )
            else:
                cur.execute(
                    """
                    INSERT INTO channel_link (id, person_id, channel, telegram_user_id)
                    VALUES (%s, %s, 'telegram', %s)
                    ON CONFLICT (telegram_user_id)
                    DO UPDATE SET person_id = EXCLUDED.person_id, updated_at = now()
                    """,
                    (uuid.uuid4(), person_id, int(destination)),
                )

    def stage(self, person_id, kind, destination) -> None:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO staged_link (person_id, kind, destination, confirmed)
                VALUES (%s, %s, %s, false)
                ON CONFLICT (person_id, kind)
                DO UPDATE SET destination = EXCLUDED.destination, confirmed = false
                """,
                (person_id, kind, destination),
            )

    def staged_destination(self, person_id, kind):
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT destination FROM staged_link
                WHERE person_id = %s AND kind = %s AND confirmed = false
                """,
                (person_id, kind),
            )
            row = cur.fetchone()
        return None if row is None else row[0]

    def mark_staged_confirmed(self, person_id, kind) -> None:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                UPDATE staged_link SET confirmed = true
                WHERE person_id = %s AND kind = %s
                """,
                (person_id, kind),
            )

    def has_unconfirmed_stage(self, person_id) -> bool:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT 1 FROM staged_link
                WHERE person_id = %s AND confirmed = false
                LIMIT 1
                """,
                (person_id,),
            )
            return cur.fetchone() is not None

    def unconfirmed_kinds(self, person_id) -> list[str]:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT kind FROM staged_link
                WHERE person_id = %s AND confirmed = false
                ORDER BY kind
                """,
                (person_id,),
            )
            return [row[0] for row in cur.fetchall()]

    def pop_stage(self, person_id) -> list[tuple[str, str]]:
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT kind, destination FROM staged_link WHERE person_id = %s",
                (person_id,),
            )
            pairs = [(row[0], row[1]) for row in cur.fetchall()]
            cur.execute("DELETE FROM staged_link WHERE person_id = %s", (person_id,))
        return pairs

    def absorb(self, survivor_id, other_id) -> None:
        if str(survivor_id) == str(other_id):
            return
        with self.conn.cursor() as cur:
            cur.execute(
                "UPDATE run SET person_id = %s, updated_at = now() WHERE person_id = %s",
                (survivor_id, other_id),
            )
            cur.execute(
                "UPDATE hidden_profile_evidence SET person_id = %s WHERE person_id = %s",
                (survivor_id, other_id),
            )
            cur.execute(
                "UPDATE channel_link SET person_id = %s, updated_at = now() WHERE person_id = %s",
                (survivor_id, other_id),
            )
            cur.execute(
                "UPDATE phone_link SET person_id = %s, updated_at = now() WHERE person_id = %s",
                (survivor_id, other_id),
            )
            cur.execute(
                """
                SELECT strengths_text, weaknesses_text, self_facts
                FROM visible_profile WHERE person_id = %s
                """,
                (other_id,),
            )
            profile = cur.fetchone()
            if profile is not None:
                facts = profile[2] if isinstance(profile[2], list) else []
                cur.execute(
                    """
                    INSERT INTO kept_profile_text (
                        id, person_id, source_label, strengths_text, weaknesses_text, self_facts
                    )
                    VALUES (%s, %s, 'другой вход', %s, %s, %s)
                    """,
                    (uuid.uuid4(), survivor_id, profile[0], profile[1], Json(facts)),
                )
            left = _marks(cur, survivor_id)
            right = _marks(cur, other_id)
            merged = merged_marks(left, right)
            cur.execute(
                """
                INSERT INTO hidden_profile (person_id)
                VALUES (%s)
                ON CONFLICT (person_id) DO NOTHING
                """,
                (survivor_id,),
            )
            cur.execute(
                """
                UPDATE hidden_profile
                SET spotting_status = %s, creativity_status = %s, valuing_status = %s,
                    uncertainty_status = %s, resources_status = %s, learning_status = %s,
                    updated_at = now()
                WHERE person_id = %s
                """,
                (
                    merged["spotting"],
                    merged["creativity"],
                    merged["valuing"],
                    merged["uncertainty"],
                    merged["resources"],
                    merged["learning"],
                    survivor_id,
                ),
            )
            cur.execute("DELETE FROM visible_profile WHERE person_id = %s", (other_id,))
            cur.execute("DELETE FROM hidden_profile WHERE person_id = %s", (other_id,))
            cur.execute("DELETE FROM profile_edit_session WHERE person_id = %s", (other_id,))
            cur.execute("DELETE FROM staged_link WHERE person_id = %s", (other_id,))
            cur.execute(
                """
                UPDATE link_code
                SET requester_person_id = %s
                WHERE requester_person_id = %s
                """,
                (survivor_id, other_id),
            )
            cur.execute("DELETE FROM person WHERE id = %s", (other_id,))

    def phone_label(self, person_id) -> str | None:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT phone FROM phone_link
                WHERE person_id = %s AND confirmed
                ORDER BY updated_at DESC
                LIMIT 1
                """,
                (person_id,),
            )
            row = cur.fetchone()
        return None if row is None else row[0]


def _marks(cur, person_id) -> dict:
    cur.execute(
        """
        SELECT spotting_status, creativity_status, valuing_status,
               uncertainty_status, resources_status, learning_status
        FROM hidden_profile
        WHERE person_id = %s
        """,
        (person_id,),
    )
    row = cur.fetchone()
    marks = {key: STATUS_NOT_OBSERVED for key in HIDDEN_CHARACTERISTICS}
    if row is None:
        return marks
    for index, key in enumerate(HIDDEN_CHARACTERISTICS):
        marks[key] = row[index]
    return marks
