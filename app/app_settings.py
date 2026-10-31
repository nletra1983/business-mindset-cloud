from app.account_settings import (
    PROFILE_FACT_PROMPT,
    PROFILE_STRENGTHS_PROMPT,
    PROFILE_WEAKNESSES_PROMPT,
    render_visible_profile,
)
from app.config import MODELS
from app.model_switch import CHANGED, PICK_TEXT, UNAVAILABLE, apply_choice, is_model_id
from app.person import (
    append_visible_fact,
    read_model_state,
    read_visible_profile,
    write_model_state,
    write_visible_strengths,
    write_visible_weaknesses,
)

SETTINGS_MOMENTS = ("open_run", "list", "after_finale")


def settings_available(moment: str) -> bool:
    return moment in SETTINGS_MOMENTS


def open_settings() -> dict:
    return {
        "actions": ["model", "profile", "second_entrance"],
        "offers_second_entrance": True,
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


def choose_model_for_person(conn, person_id, model_id: str) -> dict:
    state = (
        read_model_state(conn, person_id)
        if conn is not None
        else {"current_model": "deepseek-chat", "last_answered_model": None}
    )
    person = {
        "current_model": state["current_model"],
        "last_answered_model": state.get("last_answered_model"),
    }
    result = choose_model(person, None, model_id)
    if result.get("changed") and conn is not None:
        write_model_state(
            conn,
            person_id,
            {
                "current_model": person["current_model"],
                "last_answered_model": person.get("last_answered_model"),
            },
        )
    return result


def show_profile(profile: dict) -> dict:
    text = render_visible_profile(profile)
    return {
        "text": text,
        "next": PROFILE_STRENGTHS_PROMPT,
        "then": PROFILE_WEAKNESSES_PROMPT,
        "fact": PROFILE_FACT_PROMPT,
        "shows_hidden_profile": False,
    }


def save_strengths(conn, person_id, text: str) -> dict:
    if conn is not None:
        write_visible_strengths(conn, person_id, (text or "").strip())
        profile = read_visible_profile(conn, person_id)
    else:
        profile = {"strengths_text": (text or "").strip(), "weaknesses_text": "", "self_facts": []}
    screen = show_profile(profile)
    screen["saved"] = "strengths"
    screen["prompt"] = PROFILE_WEAKNESSES_PROMPT
    return screen


def save_weaknesses(conn, person_id, text: str) -> dict:
    if conn is not None:
        write_visible_weaknesses(conn, person_id, (text or "").strip())
        profile = read_visible_profile(conn, person_id)
    else:
        profile = {"strengths_text": "", "weaknesses_text": (text or "").strip(), "self_facts": []}
    screen = show_profile(profile)
    screen["saved"] = "weaknesses"
    screen["prompt"] = PROFILE_FACT_PROMPT
    return screen


def save_fact(conn, person_id, text: str) -> dict:
    fact = (text or "").strip()
    if conn is not None and fact:
        append_visible_fact(conn, person_id, fact)
        profile = read_visible_profile(conn, person_id)
    elif conn is not None:
        profile = read_visible_profile(conn, person_id)
    else:
        profile = {
            "strengths_text": "",
            "weaknesses_text": "",
            "self_facts": [fact] if fact else [],
        }
    screen = show_profile(profile)
    screen["saved"] = "fact"
    return screen
