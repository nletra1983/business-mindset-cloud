from app.channel_api import APP_PREFIX, dispatch
from app.device_session import MemoryDeviceSessionStore, logout, stay_signed_in
from app.entrances import MemoryBook
from app.sessions import MemorySessionStore


def _sign_in():
    book = MemoryBook(mail=lambda _email, _text: None)
    sessions = MemorySessionStore()
    vault = MemoryDeviceSessionStore()
    dispatch(
        "POST",
        f"{APP_PREFIX}/auth/email/request",
        {},
        {"email": "a@example.com"},
        book=book,
        sessions=sessions,
    )
    code = book.read_code("email", "a@example.com")["code"]
    confirmed = dispatch(
        "POST",
        f"{APP_PREFIX}/auth/email/confirm",
        {},
        {"email": "a@example.com", "code": code},
        book=book,
        sessions=sessions,
    )
    secret = confirmed["body"]["session_secret"]
    vault.put(secret)
    return book, sessions, vault, secret


def test_stay_signed_in_without_new_code():
    book, sessions, vault, secret = _sign_in()
    book.people[sessions.person_id(secret)]["runs"] = ["ход"]
    again = stay_signed_in(vault, sessions, book)
    assert again["inside"] is True
    assert again["runs"] == ["ход"]
    listed = dispatch(
        "GET",
        f"{APP_PREFIX}/runs",
        {"Authorization": f"Bearer {vault.get()}"},
        {},
        book=book,
        sessions=sessions,
    )
    assert listed["ok"] is True
    assert listed["body"]["runs"] == ["ход"]


def test_logout_revokes_server_and_clears_device():
    book, sessions, vault, secret = _sign_in()
    via_api = dispatch(
        "POST",
        f"{APP_PREFIX}/auth/logout",
        {"Authorization": f"Bearer {secret}"},
        {},
        book=book,
        sessions=sessions,
    )
    assert via_api["body"]["signed_out"] is True
    assert via_api["body"]["revoked"] is True
    result = logout(vault, sessions, secret=secret)
    assert result["signed_out"] is True
    assert vault.get() is None

    denied = dispatch(
        "GET",
        f"{APP_PREFIX}/runs",
        {"Authorization": f"Bearer {secret}"},
        {},
        book=book,
        sessions=sessions,
    )
    assert denied["status"] == 401
    assert stay_signed_in(vault, sessions, book)["inside"] is False


def test_logout_without_secret_is_safe():
    sessions = MemorySessionStore()
    vault = MemoryDeviceSessionStore()
    result = logout(vault, sessions)
    assert result["signed_out"] is True
    empty = dispatch(
        "POST",
        f"{APP_PREFIX}/auth/logout",
        {},
        {},
        book=MemoryBook(mail=lambda _e, _t: None),
        sessions=sessions,
    )
    assert empty["ok"] is True


def test_no_idle_timeout_field_on_session_issue():
    from app.sessions import hash_secret

    _book, sessions, _vault, secret = _sign_in()
    row = sessions.by_hash[hash_secret(secret)]
    assert sessions.person_id(secret) is not None
    assert "expires" not in row
    assert row["revoked"] is False
