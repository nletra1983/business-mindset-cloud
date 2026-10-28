from pathlib import Path

from app.model_switch import apply_choice


def test_change_after_finale_keeps_completed_run_and_defaults_to_deepseek():
    schema = Path("app/schema.sql").read_text(encoding="utf-8")
    assert "current_model text NOT NULL DEFAULT 'deepseek-chat'" in schema

    person = {"current_model": "deepseek-chat", "last_answered_model": "deepseek-chat"}
    run = {"status": "completed", "model_requested": "deepseek-chat"}
    utterances = [{"speaker": "agent", "text": "финал"}]
    summary = {"what_worked": "а", "what_weak": "б", "what_missed": "в"}
    before_utterances = [dict(item) for item in utterances]
    before_summary = dict(summary)
    before_requested = run["model_requested"]

    apply_choice(person, run, "glm-5.3-flash")

    assert person["current_model"] == "glm-5.3-flash"
    assert run["model_requested"] == before_requested
    assert run["status"] == "completed"
    assert utterances == before_utterances
    assert summary == before_summary
