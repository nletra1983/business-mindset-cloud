from app.account_settings import (
    PROFILE_FACT_PROMPT,
    PROFILE_STRENGTHS_PROMPT,
    PROFILE_WEAKNESSES_PROMPT,
    render_visible_profile,
)
from app.config import MODELS
from app.model_switch import CHANGED, PICK_TEXT, UNAVAILABLE, apply_choice, is_model_id

SETTINGS_MOMENTS = ("open_run", "list", "after_finale")


def settings_available(moment: str) -> bool:
    return moment in SETTINGS_MOMENTS


def open_settings() -> dict:
    return {
        "actions": ["model", "profile"],
        "offers_second_entrance": False,
        "starts_review": False,
        "shows_hidden_profile": False,
    }


def model_screen(current: str) -> dict:
    return {
        "text": PICK_TEXT,
        "models": [item["id"] for item in MODELS],
        "current": current,
    }


def choose_model(person: dict, run: dict | None, model_id: str) -> dict:
    if not is_model_id(model_id):
        return {"text": UNAVAILABLE, "changed": False}
    apply_choice(person, run, model_id)
    return {"text": CHANGED, "changed": True, "current": person["current_model"]}


def show_profile(profile: dict) -> dict:
    text = render_visible_profile(profile)
    return {
        "text": text,
        "next": PROFILE_STRENGTHS_PROMPT,
        "then": PROFILE_WEAKNESSES_PROMPT,
        "fact": PROFILE_FACT_PROMPT,
        "shows_hidden_profile": "не наблюдалось" in text or "устойчиво" in text,
    }
