import pytest

from app.deepseek import ModelDown, parse_judge_reply
from app.skill import blank_topic


def test_blank_and_link_do_not_invent_event():
    assert blank_topic("  ")
    assert blank_topic("https://example.com/news")


def test_parse_judge_enough():
    ok, missing = parse_judge_reply("ДОСТАТОЧНО: да\nНЕХВАТАЕТ:")
    assert ok
    assert missing == ""


def test_parse_judge_weak():
    ok, missing = parse_judge_reply(
        "ДОСТАТОЧНО: нет\nНЕХВАТАЕТ: Назови факт и что изменилось."
    )
    assert not ok
    assert "факт" in missing.lower()


def test_parse_judge_missing_marker_raises():
    with pytest.raises(ModelDown):
        parse_judge_reply("просто текст без меток")
