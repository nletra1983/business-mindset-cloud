from pathlib import Path

from app.entrances import (
    MemoryBook,
    begin_email_login,
    begin_settings_email,
    begin_settings_telegram,
    confirm_any_settings_code,
    confirm_email_login,
)
from app.mail import MailNotConfigured, mail_text


def _profile(strengths: str) -> dict:
    return {"strengths_text": strengths, "weaknesses_text": "слабость", "self_facts": []}


def test_email_login_admits_without_telegram_and_rejects_wrong_code():
    book = MemoryBook(mail=lambda _email, _text: None)
    started = begin_email_login(book, "Person@Example.com")
    assert started["ok"] is True
    email = started["email"]
    assert email == "person@example.com"
    sent = book.sent[0]
    assert sent == mail_text(book.read_code("email", email)["code"])
    assert "новост" not in sent.lower()
    assert "сильн" not in sent.lower()
    assert "модель" not in sent.lower()

    people_before = len(book.people)
    real = book.read_code("email", email)["code"]
    wrong_code = "0000" if real != "0000" else "0001"
    wrong = confirm_email_login(book, email, wrong_code)
    assert wrong["ok"] is False
    assert wrong["created"] is False
    assert len(book.people) == people_before

    admitted = confirm_email_login(book, email, real)
    assert admitted["ok"] is True
    assert admitted["created"] is True
    assert admitted["person_id"] not in book.telegram_of.values()


def test_replaced_code_does_not_admit():
    book = MemoryBook(mail=lambda _email, _text: None)
    email = "a@example.com"
    book.save_code("email", email, "1111", "login", None)
    book.save_code("email", email, "2222", "login", None)
    assert confirm_email_login(book, email, "1111")["ok"] is False
    assert confirm_email_login(book, email, "2222")["created"] is True


def test_failed_mail_creates_nobody():
    def fail(_email, _text):
        raise MailNotConfigured("код не отправлен")

    book = MemoryBook(mail=fail)
    result = begin_email_login(book, "a@example.com")
    assert result["ok"] is False
    assert result["reason"] == "mail"
    assert book.people == {}


def test_known_email_opens_the_same_person_and_does_not_merge():
    book = MemoryBook(mail=lambda _email, _text: None)
    email_person = book.add_person(email="a@example.com", runs=["ход-почта"])
    telegram_person = book.add_person(telegram="42", runs=["ход-бот"])
    book.save_code("email", "a@example.com", "3333", "login", None)
    result = confirm_email_login(book, "a@example.com", "3333")
    assert result["person_id"] == email_person
    assert result["created"] is False
    assert book.runs_of(telegram_person) == ["ход-бот"]
    assert book.runs_of(email_person) == ["ход-почта"]


def test_run_does_not_ask_for_email():
    flow = Path("app/run_flow.py").read_text(encoding="utf-8")
    schema = Path("app/schema.sql").read_text(encoding="utf-8")
    assert "email" not in flow.lower()
    assert "phone_link" not in schema
    assert "CREATE TABLE IF NOT EXISTS email_link" in schema


def test_one_code_of_two_links_does_not_merge():
    book = MemoryBook(mail=lambda _email, _text: None, telegram=lambda _dest, _text: None)
    email_person = book.add_person(
        email="a@example.com",
        runs=["ход-почта"],
        marks={"spotting": "устойчиво"},
        profile=_profile("текст почты"),
    )
    telegram_person = book.add_person(
        telegram="55",
        runs=["ход-бот"],
        marks={"spotting": "не наблюдалось"},
        profile=_profile("текст бота"),
    )
    assert begin_settings_email(book, email_person, "a@example.com")["ok"]
    assert begin_settings_telegram(book, email_person, "55")["ok"]
    email_code = book.read_code("email", "a@example.com")["code"]
    telegram_code = book.read_code("telegram", "55")["code"]

    assert confirm_any_settings_code(book, email_person, "9999")["ok"] is False
    assert book.runs_of(telegram_person) == ["ход-бот"]

    waiting = confirm_any_settings_code(book, email_person, telegram_code)
    assert waiting["waiting"] is True
    assert waiting["merged"] is False
    assert book.runs_of(email_person) == ["ход-почта"]
    assert book.runs_of(telegram_person) == ["ход-бот"]

    done = confirm_any_settings_code(book, email_person, email_code)
    assert done["merged"] is True
    assert telegram_person not in book.people
    assert book.runs_of(email_person) == ["ход-почта", "ход-бот"]
    assert book.people[email_person]["marks"]["spotting"] == "неравномерно"
    texts = [item["strengths_text"] for item in book.people[email_person]["profiles"]]
    assert texts == ["текст почты", "текст бота"]


def test_same_mark_stays_after_merge():
    book = MemoryBook(mail=lambda _email, _text: None, telegram=lambda _dest, _text: None)
    email_person = book.add_person(
        email="a@example.com",
        marks={"spotting": "устойчиво"},
        profile=_profile("один"),
    )
    book.add_person(telegram="55", marks={"spotting": "устойчиво"}, profile=_profile("два"))
    begin_settings_telegram(book, email_person, "55")
    code = book.read_code("telegram", "55")["code"]
    done = confirm_any_settings_code(book, email_person, code)
    assert done["merged"] is True
    assert book.people[email_person]["marks"]["spotting"] == "устойчиво"
