from app.account_settings import RECOVERABLE_TEXT
from app.telegram_poll import _dispatch


def _callback_update(data: str) -> dict:
    return {
        "callback_query": {
            "id": "cb-1",
            "from": {"id": 123, "username": "alice"},
            "message": {"message_id": 77, "chat": {"id": 456}},
            "data": data,
        }
    }


def test_open_settings_does_not_mutate_run_or_model_state(monkeypatch):
    captured = {}

    monkeypatch.setattr("app.telegram_poll._answer_callback", lambda _callback_id: None)
    monkeypatch.setattr(
        "app.telegram_poll.upsert_from_telegram",
        lambda _conn, _tg_id, _username: {"id": "person-1"},
    )
    monkeypatch.setattr("app.telegram_poll._current_model", lambda _conn, _person_id: "deepseek-chat")
    monkeypatch.setattr(
        "app.telegram_poll._perform",
        lambda _chat_id, actions, current: captured.update(
            {"actions": actions, "current_model": current}
        ),
    )
    monkeypatch.setattr(
        "app.telegram_poll.write_model_state",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("write_model_state should not be called")),
    )
    monkeypatch.setattr(
        "app.telegram_poll.write_open_run_model",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("write_open_run_model should not be called")),
    )

    _dispatch(object(), _callback_update("settings"))

    actions = captured["actions"]
    assert captured["current_model"] == "deepseek-chat"
    assert len(actions) == 1
    assert actions[0]["kind"] == "settings_menu"
    assert actions[0]["text"] == "Настройки аккаунта."


def test_stale_settings_callback_returns_recoverable_message_without_writes(monkeypatch):
    captured = {}

    monkeypatch.setattr("app.telegram_poll._answer_callback", lambda _callback_id: None)
    monkeypatch.setattr(
        "app.telegram_poll.upsert_from_telegram",
        lambda _conn, _tg_id, _username: {"id": "person-1"},
    )
    monkeypatch.setattr("app.telegram_poll._current_model", lambda _conn, _person_id: "deepseek-chat")
    monkeypatch.setattr(
        "app.telegram_poll._perform",
        lambda _chat_id, actions, current: captured.update(
            {"actions": actions, "current_model": current}
        ),
    )
    monkeypatch.setattr(
        "app.telegram_poll.write_model_state",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("write_model_state should not be called")),
    )
    monkeypatch.setattr(
        "app.telegram_poll.write_open_run_model",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("write_open_run_model should not be called")),
    )

    _dispatch(object(), _callback_update("settings:stale"))

    actions = captured["actions"]
    assert captured["current_model"] == "deepseek-chat"
    assert len(actions) == 1
    assert actions[0]["kind"] == "text"
    assert actions[0]["text"] == RECOVERABLE_TEXT
