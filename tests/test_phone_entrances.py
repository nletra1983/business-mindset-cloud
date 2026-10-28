from pathlib import Path

from app.account_settings import PHONE_EMPTY, render_visible_profile, settings_menu_action
from app.entrances import (
    MemoryBook,
    begin_phone_login,
    begin_settings_phone,
    begin_settings_telegram,
    confirm_any_settings_code,
    confirm_phone_login,
)
from app.sms import SmsNotConfigured, sms_text
from app.telegram_poll import _profile_message_actions


def _profile(strengths: str) -> dict:
    return {"strengths_text": strengths, "weaknesses_text": "слабость", "self_facts": []}


def test_phone_login_admits_without_telegram_and_rejects_wrong_code():
    book = MemoryBook(sms=lambda _phone, _text: None)
    started = begin_phone_login(book, "+7 999 111-22-33")
    assert started["ok"] is True
    phone = started["phone"]
    sent = book.sent[0]
    assert sent == sms_text(book.read_code("phone", phone)["code"])
    assert "новост" not in sent.lower()
    assert "сильн" not in sent.lower()
    assert "модель" not in sent.lower()

    people_before = len(book.people)
    real = book.read_code("phone", phone)["code"]
    wrong_code = "0000" if real != "0000" else "0001"
    wrong = confirm_phone_login(book, phone, wrong_code)
    assert wrong["ok"] is False
    assert wrong["created"] is False
    assert len(book.people) == people_before

    code = book.read_code("phone", phone)["code"]
    admitted = confirm_phone_login(book, phone, code)
    assert admitted["ok"] is True
    assert admitted["created"] is True
    assert admitted["person_id"] not in book.telegram_of.values()


def test_replaced_code_does_not_admit():
    book = MemoryBook(sms=lambda _phone, _text: None)
    phone = "79991112233"
    book.save_code("phone", phone, "1111", "login", None)
    book.save_code("phone", phone, "2222", "login", None)
    assert confirm_phone_login(book, phone, "1111")["ok"] is False
    assert confirm_phone_login(book, phone, "2222")["created"] is True


def test_failed_sms_creates_nobody():
    def fail(_phone, _text):
        raise SmsNotConfigured("код не отправлен")

    book = MemoryBook(sms=fail)
    result = begin_phone_login(book, "79991112233")
    assert result["ok"] is False
    assert result["reason"] == "sms"
    assert book.people == {}


def test_phone_login_does_not_merge_existing_entrances():
    book = MemoryBook(sms=lambda _phone, _text: None)
    phone_person = book.add_person(phone="79990001122", runs=["ход-телефон"])
    telegram_person = book.add_person(telegram="42", runs=["ход-бот"])
    book.save_code("phone", "79990001122", "3333", "login", None)
    result = confirm_phone_login(book, "79990001122", "3333")
    assert result["person_id"] == phone_person
    assert result["created"] is False
    assert book.people[telegram_person]["runs"] == ["ход-бот"]
    assert book.people[phone_person]["runs"] == ["ход-телефон"]


def test_idle_text_is_not_a_phone_request(monkeypatch):
    monkeypatch.setattr("app.telegram_poll.read_profile_edit_step", lambda _conn, _person: "idle")
    assert _profile_message_actions(object(), "person", "продолжаем ход") is None


def test_settings_show_empty_phone():
    action = settings_menu_action()
    assert f"Телефон: {PHONE_EMPTY}." in action["text"]


def test_one_code_of_two_typed_links_does_not_merge():
    book = MemoryBook(sms=lambda _phone, _text: None, telegram=lambda _dest, _text: None)
    phone_person = book.add_person(
        phone="79990001122",
        runs=["ход-телефон"],
        marks={"spotting": "устойчиво"},
        profile=_profile("текст телефона"),
    )
    telegram_person = book.add_person(
        telegram="55",
        runs=["ход-бот"],
        marks={"spotting": "не наблюдалось"},
        profile=_profile("текст бота"),
    )
    assert begin_settings_phone(book, phone_person, "79990001122")["ok"]
    assert begin_settings_telegram(book, phone_person, "55")["ok"]
    phone_code = book.read_code("phone", "79990001122")["code"]
    telegram_code = book.read_code("telegram", "55")["code"]

    assert confirm_any_settings_code(book, phone_person, "9999")["ok"] is False
    assert book.people[telegram_person]["runs"] == ["ход-бот"]

    waiting = confirm_any_settings_code(book, phone_person, telegram_code)
    assert waiting["waiting"] is True
    assert waiting["merged"] is False
    assert book.people[phone_person]["runs"] == ["ход-телефон"]
    assert book.people[telegram_person]["runs"] == ["ход-бот"]

    done = confirm_any_settings_code(book, phone_person, phone_code)
    assert done["merged"] is True
    assert telegram_person not in book.people
    runs = book.people[phone_person]["runs"]
    assert runs == ["ход-телефон", "ход-бот"]
    assert book.people[phone_person]["marks"]["spotting"] == "неравномерно"
    texts = [item["strengths_text"] for item in book.people[phone_person]["profiles"]]
    assert texts == ["текст телефона", "текст бота"]


def test_same_mark_stays_after_merge():
    book = MemoryBook(sms=lambda _phone, _text: None, telegram=lambda _dest, _text: None)
    phone_person = book.add_person(
        phone="79990001122",
        marks={"spotting": "устойчиво"},
        profile=_profile("один"),
    )
    book.add_person(telegram="55", marks={"spotting": "устойчиво"}, profile=_profile("два"))
    begin_settings_telegram(book, phone_person, "55")
    code = book.read_code("telegram", "55")["code"]
    done = confirm_any_settings_code(book, phone_person, code)
    assert done["merged"] is True
    assert book.people[phone_person]["marks"]["spotting"] == "устойчиво"


def test_visible_texts_stay_separate_on_screen():
    rendered = render_visible_profile(
        _profile("текст телефона"),
        [_profile("текст бота")],
    )
    assert "текст телефона" in rendered
    assert "текст бота" in rendered
    assert "Другой вход." in rendered
    assert "текст телефона текст бота" not in rendered


def test_schema_has_phone_link():
    schema = Path("app/schema.sql").read_text(encoding="utf-8")
    assert "CREATE TABLE IF NOT EXISTS phone_link" in schema
    assert "awaiting_link_code" in schema
