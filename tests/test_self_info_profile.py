from app.account_settings import (
    PROFILE_FACT_RETRY,
    PROFILE_STRENGTHS_RETRY,
    PROFILE_WEAKNESSES_PROMPT,
    RECOVERABLE_TEXT,
)
from app.person import PROFILE_AWAITING_EXTRA_FACT, PROFILE_AWAITING_STRENGTHS
from app.telegram_poll import _profile_message_actions


class _Conn:
    def __init__(self):
        self.commits = 0

    def commit(self):
        self.commits += 1


def test_strengths_step_saves_and_moves_to_weaknesses(monkeypatch):
    conn = _Conn()
    observed = {}
    monkeypatch.setattr(
        "app.telegram_poll.read_profile_edit_step",
        lambda _conn, _person_id: PROFILE_AWAITING_STRENGTHS,
    )
    monkeypatch.setattr(
        "app.telegram_poll.write_visible_strengths",
        lambda _conn, _person_id, value: observed.setdefault("strengths", value),
    )
    monkeypatch.setattr(
        "app.telegram_poll.write_profile_edit_step",
        lambda _conn, _person_id, step: observed.setdefault("next_step", step),
    )

    actions = _profile_message_actions(conn, "person-1", "  умею быстро собираться  ")

    assert observed["strengths"] == "умею быстро собираться"
    assert observed["next_step"] == "awaiting_weaknesses"
    assert conn.commits == 1
    assert actions[1] == {"kind": "text", "text": PROFILE_WEAKNESSES_PROMPT}


def test_blank_strengths_input_is_recoverable_and_not_saved(monkeypatch):
    conn = _Conn()
    monkeypatch.setattr(
        "app.telegram_poll.read_profile_edit_step",
        lambda _conn, _person_id: PROFILE_AWAITING_STRENGTHS,
    )
    monkeypatch.setattr(
        "app.telegram_poll.write_visible_strengths",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("should not save blank strengths")),
    )

    actions = _profile_message_actions(conn, "person-1", "   ")

    assert conn.commits == 0
    assert actions == [{"kind": "text", "text": PROFILE_STRENGTHS_RETRY}]


def test_extra_fact_step_accepts_skip_and_finishes_session(monkeypatch):
    conn = _Conn()
    observed = {}
    monkeypatch.setattr(
        "app.telegram_poll.read_profile_edit_step",
        lambda _conn, _person_id: PROFILE_AWAITING_EXTRA_FACT,
    )
    monkeypatch.setattr(
        "app.telegram_poll.append_visible_fact",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("skip should not append")),
    )
    monkeypatch.setattr(
        "app.telegram_poll.write_profile_edit_step",
        lambda _conn, _person_id, step: observed.setdefault("next_step", step),
    )
    monkeypatch.setattr(
        "app.telegram_poll.read_visible_profile",
        lambda _conn, _person_id: {
            "strengths_text": "умею учиться",
            "weaknesses_text": "теряю фокус",
            "self_facts": [],
        },
    )

    actions = _profile_message_actions(conn, "person-1", "нет")

    assert observed["next_step"] == "idle"
    assert conn.commits == 1
    assert "Профиль сохранён." in actions[0]["text"]
    assert "Информация о себе." in actions[1]["text"]


def test_unknown_profile_step_returns_recoverable(monkeypatch):
    conn = _Conn()
    observed = {}
    monkeypatch.setattr(
        "app.telegram_poll.read_profile_edit_step",
        lambda _conn, _person_id: "broken-step",
    )
    monkeypatch.setattr(
        "app.telegram_poll.write_profile_edit_step",
        lambda _conn, _person_id, step: observed.setdefault("next_step", step),
    )

    actions = _profile_message_actions(conn, "person-1", "что угодно")

    assert observed["next_step"] == "idle"
    assert conn.commits == 1
    assert actions == [{"kind": "text", "text": RECOVERABLE_TEXT}]


def test_blank_extra_fact_is_recoverable(monkeypatch):
    conn = _Conn()
    monkeypatch.setattr(
        "app.telegram_poll.read_profile_edit_step",
        lambda _conn, _person_id: PROFILE_AWAITING_EXTRA_FACT,
    )
    actions = _profile_message_actions(conn, "person-1", "   ")
    assert conn.commits == 0
    assert actions == [{"kind": "text", "text": PROFILE_FACT_RETRY}]
