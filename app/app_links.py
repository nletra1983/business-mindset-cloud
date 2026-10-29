from app.account_settings import (
    EMAIL_LINK_BAD,
    EMAIL_LINK_PROMPT,
    ENTRANCE_CONFIRMED,
    ENTRANCES_MERGED,
    LINK_CODE_FAILED,
    LINK_CODE_REJECTED,
    LINK_CODE_SENT,
    SECOND_STILL_OPEN,
    TELEGRAM_LINK_BAD,
    TELEGRAM_LINK_PROMPT,
)
from app.entrances import begin_settings_email, begin_settings_telegram, confirm_any_settings_code

SECOND_ENTRANCE_TITLE = "Второй вход."


def second_entrance_screen() -> dict:
    return {
        "text": SECOND_ENTRANCE_TITLE,
        "actions": ["email", "telegram"],
        "opens_model": False,
        "opens_profile": False,
    }


def submit_email_link(book, person_id, raw: str) -> dict:
    result = begin_settings_email(book, person_id, raw)
    if result["ok"]:
        return {"text": LINK_CODE_SENT, "merged": False, "waiting": False}
    if result.get("reason") == "mail":
        return {"text": LINK_CODE_FAILED, "merged": False, "waiting": False}
    return {"text": EMAIL_LINK_BAD, "merged": False, "waiting": False}


def submit_telegram_link(book, person_id, raw: str) -> dict:
    result = begin_settings_telegram(book, person_id, raw)
    if result["ok"]:
        return {"text": LINK_CODE_SENT, "merged": False, "waiting": False}
    if result.get("reason") == "delivery":
        return {"text": LINK_CODE_FAILED, "merged": False, "waiting": False}
    return {"text": TELEGRAM_LINK_BAD, "merged": False, "waiting": False}


def submit_link_code(book, person_id, code: str) -> dict:
    result = confirm_any_settings_code(book, person_id, code)
    if not result["ok"]:
        return {"text": LINK_CODE_REJECTED, "merged": False, "waiting": False}
    if result.get("waiting"):
        return {"text": SECOND_STILL_OPEN, "merged": False, "waiting": True}
    note = ENTRANCES_MERGED if result.get("merged") else ENTRANCE_CONFIRMED
    return {"text": note, "merged": bool(result.get("merged")), "waiting": False}


def prompt_for(kind: str) -> str:
    if kind == "email":
        return EMAIL_LINK_PROMPT
    return TELEGRAM_LINK_PROMPT
