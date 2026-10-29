from app.account_settings import SETTINGS_EMAIL_LABEL, SETTINGS_TELEGRAM_LABEL, settings_menu_action
from app.app_links import second_entrance_screen, submit_email_link, submit_link_code, submit_telegram_link
from app.entrances import MemoryBook


def test_bot_and_app_offer_the_same_two_additions():
    buttons = [row[0]["text"] for row in settings_menu_action()["buttons"]]
    screen = second_entrance_screen()
    assert SETTINGS_EMAIL_LABEL in buttons
    assert SETTINGS_TELEGRAM_LABEL in buttons
    assert screen["actions"] == ["email", "telegram"]
    assert screen["opens_model"] is False
    assert screen["opens_profile"] is False


def test_one_code_waits_and_the_second_merges():
    book = MemoryBook(mail=lambda _email, _text: None, telegram=lambda _dest, _text: None)
    email_person = book.add_person(email="a@example.com", runs=["ход-почта"], marks={"spotting": "устойчиво"})
    telegram_person = book.add_person(telegram="55", runs=["ход-бот"], marks={"spotting": "не наблюдалось"})
    assert submit_email_link(book, email_person, "a@example.com")["text"].startswith("Код отправлен")
    assert submit_telegram_link(book, email_person, "55")["text"].startswith("Код отправлен")
    telegram_code = book.read_code("telegram", "55")["code"]
    email_code = book.read_code("email", "a@example.com")["code"]

    waiting = submit_link_code(book, email_person, telegram_code)
    assert waiting["waiting"] is True
    assert waiting["merged"] is False
    assert book.runs_of(telegram_person) == ["ход-бот"]

    done = submit_link_code(book, email_person, email_code)
    assert done["merged"] is True
    assert done["text"] == "Входы объединены."
    assert book.runs_of(email_person) == ["ход-почта", "ход-бот"]
    assert book.people[email_person]["marks"]["spotting"] == "неравномерно"
