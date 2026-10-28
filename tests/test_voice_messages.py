from app.account_settings import VOICE_NOT_RECOGNIZED_TEXT, VOICE_UNSUPPORTED_TEXT
from app.telegram_poll import _dispatch


def _voice_update(file_id: str = "voice-file-1") -> dict:
    return {
        "message": {
            "message_id": 77,
            "chat": {"id": 456},
            "from": {"id": 123, "username": "alice"},
            "voice": {"file_id": file_id, "duration": 4, "mime_type": "audio/ogg"},
        }
    }


def _audio_update() -> dict:
    return {
        "message": {
            "message_id": 77,
            "chat": {"id": 456},
            "from": {"id": 123, "username": "alice"},
            "audio": {"file_id": "audio-file-1"},
        }
    }


def _video_note_update() -> dict:
    return {
        "message": {
            "message_id": 77,
            "chat": {"id": 456},
            "from": {"id": 123, "username": "alice"},
            "video_note": {"file_id": "video-note-1"},
        }
    }


def test_voice_dispatch_recognized_text_uses_existing_text_flow(monkeypatch):
    captured = {}
    monkeypatch.setattr("app.telegram_poll._typing", lambda _chat_id: None)
    monkeypatch.setattr(
        "app.telegram_poll.upsert_from_telegram",
        lambda _conn, _tg_id, _username: {"id": "person-1"},
    )
    monkeypatch.setattr("app.telegram_poll._current_model", lambda _conn, _person_id: "GigaChat-2")
    monkeypatch.setattr("app.telegram_poll._download_voice_bytes", lambda _file_id: b"voice-bytes")
    monkeypatch.setattr("app.telegram_poll.transcribe_voice", lambda *_args, **_kwargs: "распознанный текст")
    monkeypatch.setattr("app.telegram_poll._profile_message_actions", lambda *_args, **_kwargs: None)

    handled = {}

    def fake_handle_text(_conn, _person, _chat_id, _message_id, text):
        handled["text"] = text
        return [{"kind": "text", "text": "дальше по ходу"}]

    monkeypatch.setattr("app.telegram_poll.handle_text", fake_handle_text)
    monkeypatch.setattr(
        "app.telegram_poll._perform",
        lambda _chat_id, actions, current: captured.update(
            {"actions": actions, "current_model": current}
        ),
    )

    _dispatch(object(), _voice_update())

    assert handled["text"] == "распознанный текст"
    assert captured["current_model"] == "GigaChat-2"
    assert captured["actions"][0] == {"kind": "text", "text": "распознанный текст"}
    assert captured["actions"][1] == {"kind": "text", "text": "дальше по ходу"}


def test_voice_dispatch_unsupported_model_does_not_call_text_flow(monkeypatch):
    captured = {}
    monkeypatch.setattr("app.telegram_poll._typing", lambda _chat_id: None)
    monkeypatch.setattr(
        "app.telegram_poll.upsert_from_telegram",
        lambda _conn, _tg_id, _username: {"id": "person-1"},
    )
    monkeypatch.setattr("app.telegram_poll._current_model", lambda _conn, _person_id: "deepseek-chat")
    monkeypatch.setattr(
        "app.telegram_poll.handle_text",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("handle_text should not be called")),
    )
    monkeypatch.setattr(
        "app.telegram_poll._perform",
        lambda _chat_id, actions, current: captured.update(
            {"actions": actions, "current_model": current}
        ),
    )

    _dispatch(object(), _voice_update())

    assert captured["current_model"] == "deepseek-chat"
    assert captured["actions"] == [{"kind": "text", "text": VOICE_UNSUPPORTED_TEXT}]


def test_voice_dispatch_empty_recognition_is_recoverable(monkeypatch):
    captured = {}
    monkeypatch.setattr("app.telegram_poll._typing", lambda _chat_id: None)
    monkeypatch.setattr(
        "app.telegram_poll.upsert_from_telegram",
        lambda _conn, _tg_id, _username: {"id": "person-1"},
    )
    monkeypatch.setattr("app.telegram_poll._current_model", lambda _conn, _person_id: "GigaChat-2")
    monkeypatch.setattr("app.telegram_poll._download_voice_bytes", lambda _file_id: b"voice-bytes")
    monkeypatch.setattr("app.telegram_poll.transcribe_voice", lambda *_args, **_kwargs: "  ")
    monkeypatch.setattr(
        "app.telegram_poll.handle_text",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("handle_text should not be called")),
    )
    monkeypatch.setattr(
        "app.telegram_poll._perform",
        lambda _chat_id, actions, current: captured.update(
            {"actions": actions, "current_model": current}
        ),
    )

    _dispatch(object(), _voice_update())

    assert captured["actions"] == [{"kind": "text", "text": VOICE_NOT_RECOGNIZED_TEXT}]


def test_voice_dispatch_profile_step_uses_recognized_text(monkeypatch):
    captured = {}
    observed = {}
    monkeypatch.setattr("app.telegram_poll._typing", lambda _chat_id: None)
    monkeypatch.setattr(
        "app.telegram_poll.upsert_from_telegram",
        lambda _conn, _tg_id, _username: {"id": "person-1"},
    )
    monkeypatch.setattr("app.telegram_poll._current_model", lambda _conn, _person_id: "GigaChat-2")
    monkeypatch.setattr("app.telegram_poll._download_voice_bytes", lambda _file_id: b"voice-bytes")
    monkeypatch.setattr("app.telegram_poll.transcribe_voice", lambda *_args, **_kwargs: "умею слушать")

    def fake_profile_actions(_conn, _person_id, text):
        observed["text"] = text
        return [{"kind": "text", "text": "Сильные стороны сохранены."}]

    monkeypatch.setattr("app.telegram_poll._profile_message_actions", fake_profile_actions)
    monkeypatch.setattr(
        "app.telegram_poll.handle_text",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("handle_text should not be called")),
    )
    monkeypatch.setattr(
        "app.telegram_poll._perform",
        lambda _chat_id, actions, current: captured.update(
            {"actions": actions, "current_model": current}
        ),
    )

    _dispatch(object(), _voice_update())

    assert observed["text"] == "умею слушать"
    assert captured["actions"][0] == {"kind": "text", "text": "умею слушать"}
    assert captured["actions"][1] == {"kind": "text", "text": "Сильные стороны сохранены."}


def test_audio_and_video_note_are_not_processed_as_voice(monkeypatch):
    calls = {"perform": 0}
    monkeypatch.setattr("app.telegram_poll._typing", lambda _chat_id: None)
    monkeypatch.setattr(
        "app.telegram_poll._perform",
        lambda *_args, **_kwargs: calls.__setitem__("perform", calls["perform"] + 1),
    )

    _dispatch(object(), _audio_update())
    _dispatch(object(), _video_note_update())

    assert calls["perform"] == 0
