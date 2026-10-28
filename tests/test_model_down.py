import httpx
import pytest

from app.model_client import ModelDown, complete
from app.model_switch import apply_fallback, note_answered


def test_first_break_retries_the_same_call_once(monkeypatch):
    calls = {"n": 0}

    def fail(*_args, **_kwargs):
        calls["n"] += 1
        raise httpx.ConnectError("down")

    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")
    monkeypatch.setattr("app.model_client.httpx.post", fail)

    with pytest.raises(ModelDown):
        complete("deepseek-chat", [{"role": "user", "content": "ping"}])

    assert calls["n"] == 2


def test_second_break_returns_to_last_answered_model_and_keeps_run_open():
    person = {"current_model": "GigaChat-2", "last_answered_model": "deepseek-chat"}
    run = {"status": "open", "model_requested": "GigaChat-2"}

    apply_fallback(person, run)

    assert person["current_model"] == "deepseek-chat"
    assert run["model_requested"] == "deepseek-chat"
    assert run["status"] == "open"


def test_second_break_without_answered_model_does_not_replace_current():
    person = {"current_model": "glm-5.3-flash", "last_answered_model": None}
    run = {"status": "open", "model_requested": "glm-5.3-flash"}

    apply_fallback(person, run)

    assert person["current_model"] == "glm-5.3-flash"
    assert run["model_requested"] == "glm-5.3-flash"
    assert run["status"] == "open"


def test_successful_reply_stores_requested_id():
    person = {"current_model": "glm-5.3-flash", "last_answered_model": None}

    note_answered(person, "glm-5.3-flash")

    assert person["last_answered_model"] == "glm-5.3-flash"
