from app.account_settings import (
    PROFILE_STRENGTHS_PROMPT,
    SETTINGS_CALLBACK,
    SETTINGS_MODEL_CALLBACK,
    SETTINGS_MODEL_LABEL,
    SETTINGS_PROFILE_CALLBACK,
    SETTINGS_PROFILE_LABEL,
    SETTINGS_TITLE,
    settings_button,
    settings_menu_action,
)
from app.telegram_poll import _perform, _settings_actions


class _Conn:
    def __init__(self):
        self.commits = 0

    def commit(self):
        self.commits += 1


def test_settings_button_replaces_model_opener():
    button = settings_button()
    assert button["text"] == "настройки"
    assert button["callback_data"] == SETTINGS_CALLBACK


def test_settings_menu_contains_two_expected_options():
    action = settings_menu_action()
    assert action["kind"] == "settings_menu"
    assert action["text"] == SETTINGS_TITLE
    buttons = [row[0] for row in action["buttons"]]
    assert [button["text"] for button in buttons] == [
        SETTINGS_MODEL_LABEL,
        SETTINGS_PROFILE_LABEL,
    ]
    assert [button["callback_data"] for button in buttons] == [
        SETTINGS_MODEL_CALLBACK,
        SETTINGS_PROFILE_CALLBACK,
    ]


def test_settings_model_reuses_existing_model_flow(monkeypatch):
    monkeypatch.setattr(
        "app.telegram_poll.read_model_state",
        lambda _conn, _person_id: {"current_model": "glm-5.3-flash", "last_answered_model": None},
    )
    actions = _settings_actions(object(), "person-1", SETTINGS_MODEL_CALLBACK)
    assert actions == [{"kind": "models", "text": "Выбери модель.", "current": "glm-5.3-flash"}]


def test_profile_callback_routes_to_profile_entry(monkeypatch):
    conn = _Conn()
    observed = {}

    def remember_step(_conn, _person_id, step):
        observed["step"] = step

    profile = {
        "strengths_text": "умею фокусироваться",
        "weaknesses_text": "иногда тороплюсь",
        "self_facts": ["веду канал"],
    }
    monkeypatch.setattr("app.telegram_poll.read_visible_profile", lambda _conn, _pid: profile)
    monkeypatch.setattr("app.telegram_poll.write_profile_edit_step", remember_step)
    actions = _settings_actions(conn, "person-1", SETTINGS_PROFILE_CALLBACK)

    assert observed["step"] == "awaiting_strengths"
    assert conn.commits == 1
    assert len(actions) == 2
    assert actions[0]["kind"] == "text"
    assert "сильные стороны" in actions[0]["text"].lower()
    assert actions[1] == {"kind": "text", "text": PROFILE_STRENGTHS_PROMPT}


def test_list_render_keeps_settings_button(monkeypatch):
    calls: list[tuple[str, dict]] = []

    def capture(method: str, payload: dict) -> dict:
        calls.append((method, payload))
        return {"ok": True}

    monkeypatch.setattr("app.telegram_poll._call", capture)
    _perform(10, [{"kind": "list", "text": "x", "buttons": []}], "deepseek-chat")

    assert len(calls) == 1
    method, payload = calls[0]
    assert method == "sendMessage"
    keyboard = payload["reply_markup"]["inline_keyboard"]
    assert keyboard[0][1]["text"] == "настройки"
    assert keyboard[0][1]["callback_data"] == "settings"
