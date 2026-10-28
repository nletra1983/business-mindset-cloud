from app.person import (
    STATUS_NOT_OBSERVED,
    STATUS_SHOWING,
    STATUS_STABLE,
    STATUS_UNEVEN,
    STATUS_WEAK,
    choose_current_focus,
    status_from_signals,
)
from app.run_flow import _finish, _hidden_profile_observations


def test_status_from_signals_transitions():
    assert status_from_signals([]) == STATUS_NOT_OBSERVED
    assert status_from_signals([STATUS_SHOWING]) == STATUS_SHOWING
    assert status_from_signals([STATUS_WEAK]) == STATUS_WEAK
    assert status_from_signals([STATUS_WEAK, STATUS_WEAK]) == STATUS_STABLE
    assert status_from_signals([STATUS_SHOWING, STATUS_SHOWING]) == STATUS_STABLE
    assert status_from_signals([STATUS_SHOWING, STATUS_WEAK]) == STATUS_UNEVEN


def test_choose_current_focus_priority():
    statuses = {
        "spotting": STATUS_SHOWING,
        "creativity": STATUS_WEAK,
        "valuing": STATUS_NOT_OBSERVED,
        "uncertainty": STATUS_SHOWING,
        "resources": STATUS_UNEVEN,
        "learning": STATUS_SHOWING,
    }
    assert choose_current_focus(statuses) == "creativity"

    all_strong = {
        "spotting": STATUS_SHOWING,
        "creativity": STATUS_SHOWING,
        "valuing": STATUS_SHOWING,
        "uncertainty": STATUS_SHOWING,
        "resources": STATUS_SHOWING,
        "learning": STATUS_SHOWING,
    }
    assert choose_current_focus(all_strong) == "spotting"


def test_hidden_profile_observations_for_smoke_skill():
    run = {"skill_version": "business-idea-from-news.smoke", "topic_text": "рост цены доставки"}
    observations = _hidden_profile_observations(
        run,
        event_answer="изменились тарифы у курьеров",
        scale_answer="малому ритейлу стало дороже",
        worked="",
        weak="",
    )
    assert observations == [
        {
            "characteristic_id": "spotting",
            "signal": STATUS_SHOWING,
            "quote_or_paraphrase": "изменились тарифы у курьеров",
        }
    ]


def test_finish_calls_hidden_profile_update(monkeypatch):
    captured = {}

    class _Cursor:
        def __enter__(self):
            return self

        def __exit__(self, _exc_type, _exc, _tb):
            return False

        def execute(self, _query, _params=None):
            return None

    class _Conn:
        def __init__(self):
            self.commits = 0

        def cursor(self):
            return _Cursor()

        def commit(self):
            self.commits += 1

    monkeypatch.setattr(
        "app.run_flow.finale",
        lambda *_args, **_kwargs: (
            "ПОЛУЧИЛОСЬ: есть изменение",
            "есть изменение",
            "слабых мест нет",
            "пропущено: ...",
            "deepseek-chat",
        ),
    )
    monkeypatch.setattr("app.run_flow.save_summary", lambda *_args, **_kwargs: None)
    monkeypatch.setattr("app.run_flow._mark_answered", lambda *_args, **_kwargs: None)
    monkeypatch.setattr("app.run_flow._utter", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(
        "app.run_flow.apply_hidden_profile_observations",
        lambda _conn, person_id, run_id, exercise_id, observations: captured.update(
            {
                "person_id": person_id,
                "run_id": run_id,
                "exercise_id": exercise_id,
                "observations": observations,
            }
        ),
    )

    run = {
        "id": "11111111-1111-1111-1111-111111111111",
        "person_id": "22222222-2222-2222-2222-222222222222",
        "topic_text": "рост цены доставки",
        "model_requested": "deepseek-chat",
        "event_answer": "изменились тарифы у курьеров",
        "scale_answer": "малому ритейлу стало дороже",
        "status": "open",
        "skill_version": "business-idea-from-news.smoke",
    }

    actions = _finish(_Conn(), run)

    assert len(actions) == 1
    assert captured["person_id"] == run["person_id"]
    assert captured["run_id"] == run["id"]
    assert captured["exercise_id"] == run["skill_version"]
    assert captured["observations"][0]["characteristic_id"] == "spotting"
