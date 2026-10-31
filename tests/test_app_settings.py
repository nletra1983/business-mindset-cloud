from app.app_settings import choose_model, model_screen, open_settings, settings_available, show_profile
from app.model_switch import CHANGED


def test_settings_exist_at_the_three_bot_moments():
    assert settings_available("open_run")
    assert settings_available("list")
    assert settings_available("after_finale")
    assert settings_available("somewhere_else") is False


def test_settings_are_model_and_profile_only():
    screen = open_settings()
    assert "model" in screen["actions"]
    assert "profile" in screen["actions"]
    assert "second_entrance" in screen["actions"]
    assert screen["offers_second_entrance"] is True
    assert screen["starts_review"] is False
    assert screen["shows_hidden_profile"] is False


def test_choosing_a_model_uses_the_bot_phrase():
    person = {"current_model": "deepseek-chat"}
    run = {"status": "open", "model_requested": "deepseek-chat"}
    screen = model_screen(person["current_model"])
    assert "deepseek-chat" in screen["models"]
    chosen = choose_model(person, run, "glm-5.3-flash")
    assert chosen["text"] == CHANGED
    assert chosen["current"] == "glm-5.3-flash"
    assert run["model_requested"] == "glm-5.3-flash"


def test_visible_profile_hides_skill_marks_and_asks_separately():
    screen = show_profile(
        {
            "strengths_text": "умею фокусироваться",
            "weaknesses_text": "тороплюсь",
            "self_facts": [],
        }
    )
    assert "умею фокусироваться" in screen["text"]
    assert screen["shows_hidden_profile"] is False
    assert "сильн" in screen["next"].lower()
    assert "слаб" in screen["then"].lower()
    assert screen["next"] != screen["then"]
