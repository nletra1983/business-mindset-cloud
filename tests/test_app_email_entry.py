from app.app_entry import (
    CODE_FAILED,
    CODE_PROMPT,
    CODE_REJECTED,
    EMPTY_LIST,
    EMAIL_PROMPT,
    start_screen,
    submit_code,
    submit_email,
)
from app.entrances import MemoryBook
from app.mail import MailNotConfigured


def _book():
    return MemoryBook(mail=lambda _email, _text: None)


def test_start_does_not_mention_telegram():
    screen = start_screen()
    assert screen["text"] == EMAIL_PROMPT
    assert screen["mentions_telegram"] is False
    assert screen["actions"] == []
    assert screen["inside"] is False


def test_valid_code_shows_only_this_entrance_runs():
    book = _book()
    mine = book.add_person(email="a@example.com", runs=["ход один", "ход два"])
    book.add_person(telegram="55", runs=["чужой ход"])
    asked = submit_email(book, "A@Example.com")
    assert asked["text"] == CODE_PROMPT
    assert asked["mentions_telegram"] is False
    code = book.read_code("email", "a@example.com")["code"]
    screen = submit_code(book, asked["email"], code)
    assert screen["inside"] is True
    assert screen["person_id"] == mine
    assert screen["runs"] == ["ход один", "ход два"]
    assert "чужой ход" not in screen["text"]
    assert screen["actions"] == []
    assert screen["mentions_telegram"] is False


def test_empty_list_still_means_inside():
    book = _book()
    submit_email(book, "a@example.com")
    code = book.read_code("email", "a@example.com")["code"]
    screen = submit_code(book, "a@example.com", code)
    assert screen["inside"] is True
    assert screen["runs"] == []
    assert screen["text"] == EMPTY_LIST


def test_wrong_code_hides_the_list_and_creates_nobody():
    book = _book()
    submit_email(book, "a@example.com")
    before = len(book.people)
    real = book.read_code("email", "a@example.com")["code"]
    wrong = "0000" if real != "0000" else "0001"
    screen = submit_code(book, "a@example.com", wrong)
    assert screen["text"] == CODE_REJECTED
    assert screen["inside"] is False
    assert screen["runs"] == []
    assert screen["created"] is False
    assert len(book.people) == before


def test_failed_mail_does_not_open_the_list():
    def fail(_email, _text):
        raise MailNotConfigured("код не отправлен")

    book = MemoryBook(mail=fail)
    screen = submit_email(book, "a@example.com")
    assert screen["text"] == CODE_FAILED
    assert screen["inside"] is False
    assert screen["runs"] == []
    assert book.people == {}
