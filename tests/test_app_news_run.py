from app.app_news import EXCLUDED_ACTIONS, LIST_ACTIONS, begin_from_list, list_screen, resume_from_list


def test_list_offers_start_and_resume_only(monkeypatch):
    monkeypatch.setattr(
        "app.app_news.show_list",
        lambda *_args: [{"kind": "list", "text": "список", "buttons": []}],
    )
    screen = list_screen(object(), "person-1")
    assert screen["actions"] == list(LIST_ACTIONS)
    assert "past" in screen["excluded"]
    assert "redo" in EXCLUDED_ACTIONS
    assert "delete" in EXCLUDED_ACTIONS


def test_begin_from_list_uses_the_existing_run_rule(monkeypatch):
    seen = {}

    def remember(conn, person, chat_id, message_id, text):
        seen["person"] = person
        seen["text"] = text
        return [{"kind": "text", "text": "вопрос"}]

    monkeypatch.setattr("app.app_news.set_accepting_new", lambda *_args: None)
    monkeypatch.setattr("app.app_news.handle_text", remember)
    monkeypatch.setattr(
        "app.app_news.show_list",
        lambda *_args: [{"kind": "list", "text": "список", "buttons": []}],
    )
    actions = begin_from_list(object(), {"id": "person-1", "accepting_new": False}, 1, 2, "новость")
    assert seen["person"]["accepting_new"] is True
    assert seen["text"] == "новость"
    assert actions == [{"kind": "text", "text": "вопрос"}]


def test_resume_uses_the_existing_return(monkeypatch):
    monkeypatch.setattr(
        "app.app_news.resume",
        lambda _conn, person_id, run_id: [{"kind": "text", "text": f"{person_id}:{run_id}"}],
    )
    assert resume_from_list(object(), "person-1", "run-9") == [
        {"kind": "text", "text": "person-1:run-9"}
    ]


def test_list_screen_has_no_delete(monkeypatch):
    monkeypatch.setattr(
        "app.app_news.show_list",
        lambda *_args: [{"kind": "list", "text": "Незавершённые ходы.", "buttons": []}],
    )
    screen = list_screen(object(), "person-1")
    assert "delete" not in screen["actions"]
    assert "удал" not in screen["shown"][0]["text"].lower()
