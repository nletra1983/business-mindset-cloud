from app.channel_api import APP_PREFIX, dispatch
from app.entrances import MemoryBook
from app.mail import mail_text
from app.sessions import MemorySessionStore


def _book():
    return MemoryBook(mail=lambda _email, _text: None)


def test_prefix_is_not_telegram_long_poll():
    assert APP_PREFIX == "/app/v1"
    assert "getUpdates" not in APP_PREFIX


def test_email_confirm_issues_session_and_wrong_code_does_not():
    book = _book()
    sessions = MemorySessionStore()
    asked = dispatch(
        "POST",
        f"{APP_PREFIX}/auth/email/request",
        {},
        {"email": "a@example.com"},
        book=book,
        sessions=sessions,
    )
    assert asked["ok"] is True
    assert asked["body"]["status"] == "code_sent"
    code = book.read_code("email", "a@example.com")["code"]
    assert book.sent[0] == mail_text(code)

    bad = dispatch(
        "POST",
        f"{APP_PREFIX}/auth/email/confirm",
        {},
        {"email": "a@example.com", "code": "0000" if code != "0000" else "0001"},
        book=book,
        sessions=sessions,
    )
    assert bad["ok"] is False
    assert "session_secret" not in bad["body"]

    good = dispatch(
        "POST",
        f"{APP_PREFIX}/auth/email/confirm",
        {},
        {"email": "a@example.com", "code": code},
        book=book,
        sessions=sessions,
    )
    assert good["ok"] is True
    secret = good["body"]["session_secret"]
    assert sessions.person_id(secret) == good["body"]["person_id"]


def test_runs_require_session_and_list_own_runs():
    book = _book()
    sessions = MemorySessionStore()
    person = book.add_person(email="a@example.com", runs=["ход один"])
    book.add_person(telegram="55", runs=["чужой"])
    secret = sessions.issue(person)
    denied = dispatch("GET", f"{APP_PREFIX}/runs", {}, {}, book=book, sessions=sessions)
    assert denied["status"] == 401
    listed = dispatch(
        "GET",
        f"{APP_PREFIX}/runs",
        {"Authorization": f"Bearer {secret}"},
        {},
        book=book,
        sessions=sessions,
    )
    assert listed["body"]["runs"] == ["ход один"]
    assert listed["body"]["actions"] == ["new", "resume"]
    assert "delete" in listed["body"]["excluded"]
    assert "past" in listed["body"]["excluded"]
    assert "redo" in listed["body"]["excluded"]


def test_blank_topic_does_not_start_run():
    book = _book()
    sessions = MemorySessionStore()
    person = book.add_person(email="a@example.com", runs=[])
    secret = sessions.issue(person)
    blank = dispatch(
        "POST",
        f"{APP_PREFIX}/runs",
        {"Authorization": f"Bearer {secret}"},
        {"topic": "   "},
        book=book,
        sessions=sessions,
    )
    assert blank["ok"] is False
    assert blank["status"] == 400
    assert blank["body"]["error"] == "blank_topic"
    assert book.runs_of(person) == []


def test_idempotent_answer_does_not_move_step_twice():
    book = _book()
    sessions = MemorySessionStore()
    person = book.add_person(email="a@example.com", runs=["тема"])
    secret = sessions.issue(person)
    headers = {"Authorization": f"Bearer {secret}", "Idempotency-Key": "ans-1"}
    first = dispatch(
        "POST",
        f"{APP_PREFIX}/runs/run-1/answers",
        headers,
        {"text": "ответ"},
        book=book,
        sessions=sessions,
    )
    second = dispatch(
        "POST",
        f"{APP_PREFIX}/runs/run-1/answers",
        headers,
        {"text": "ответ"},
        book=book,
        sessions=sessions,
    )
    assert first["body"]["step_moves"] == 1
    assert second["body"]["step_moves"] == 1
    assert book.people[str(person)]["answers"]["run-1"] == 1


def test_settings_and_second_entrance_need_session():
    book = _book()
    sessions = MemorySessionStore()
    secret = sessions.issue(book.add_person(email="a@example.com"))
    denied = dispatch("GET", f"{APP_PREFIX}/settings", {}, {}, book=book, sessions=sessions)
    assert denied["status"] == 401
    opened = dispatch(
        "GET",
        f"{APP_PREFIX}/settings",
        {"Authorization": f"Bearer {secret}"},
        {},
        book=book,
        sessions=sessions,
    )
    assert opened["body"]["actions"] == ["model", "profile"]
    second = dispatch(
        "GET",
        f"{APP_PREFIX}/settings/second-entrance",
        {"Authorization": f"Bearer {secret}"},
        {},
        book=book,
        sessions=sessions,
    )
    assert second["body"]["actions"] == ["email", "telegram"]
