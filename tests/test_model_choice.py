from app.model_switch import after_choice, apply_choice, model_keyboard
from app.run_list import exit_row


def test_choice_sets_current_model_and_open_run_without_rewriting_utterances():
    person = {"current_model": "deepseek-chat", "last_answered_model": None}
    run = {"status": "open", "model_requested": "deepseek-chat"}
    utterances = [{"speaker": "human", "text": "факт"}, {"speaker": "agent", "text": "вопрос"}]
    before = [dict(item) for item in utterances]

    apply_choice(person, run, "GigaChat-2")

    assert person["current_model"] == "GigaChat-2"
    assert run["model_requested"] == "GigaChat-2"
    assert utterances == before

    buttons = [row[0] for row in model_keyboard(person["current_model"])["inline_keyboard"]]
    assert [button["text"] for button in buttons] == ["DeepSeek", "GigaChat", "GLM"]
    assert buttons[1]["style"] == "success"
    assert "style" not in buttons[0]
    assert "style" not in buttons[2]
    assert all("<" not in button["text"] for button in buttons)


def test_after_choice_is_text_only():
    action = after_choice(10)
    assert action["text"] == "Модель изменена."
    assert action["kind"] == "plain_edit"
    assert "current" not in action


def test_opener_button_shows_current_model_name():
    deepseek = exit_row("deepseek-chat")[1]
    gigachat = exit_row("GigaChat-2")[1]
    glm = exit_row("glm-5.3-flash")[1]
    assert deepseek["text"] == "DeepSeek"
    assert gigachat["text"] == "GigaChat"
    assert glm["text"] == "GLM"
    assert deepseek["callback_data"] == gigachat["callback_data"] == glm["callback_data"] == "model"
    assert all("<" not in button["text"] for button in (deepseek, gigachat, glm))
