from app.config import MODELS

UNAVAILABLE = "Выбранная модель недоступна."
PICK_TEXT = "Выбери модель."
MODEL_CALLBACK = "model"


def is_model_id(model_id: str) -> bool:
    return any(item["id"] == model_id for item in MODELS)


def apply_choice(person: dict, run: dict | None, model_id: str) -> None:
    person["current_model"] = model_id
    if run is not None and run.get("status") == "open":
        run["model_requested"] = model_id


def apply_fallback(person: dict, run: dict | None) -> None:
    previous = person.get("last_answered_model")
    if not previous:
        return
    person["current_model"] = previous
    if run is not None and run.get("status") == "open":
        run["model_requested"] = previous


def note_answered(person: dict, requested_id: str) -> None:
    person["last_answered_model"] = requested_id


def model_keyboard(current_model: str) -> dict:
    rows = []
    for item in MODELS:
        button = {"text": item["label"], "callback_data": f"m:{item['id']}"}
        if item["id"] == current_model:
            button["style"] = "success"
        rows.append([button])
    return {"inline_keyboard": rows}
