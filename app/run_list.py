from app.run_flow import EXIT_LABEL, continue_prompt, focus, leave_window, open_runs


def exit_keyboard() -> dict:
    return {
        "inline_keyboard": [[{"text": EXIT_LABEL, "callback_data": "to_list"}]]
    }


def show_list(conn, person_id) -> list[dict]:
    leave_window(conn, person_id)
    rows = open_runs(conn, person_id)
    buttons = []
    for run_id, topic, _step, _version in rows:
        label = topic if len(topic) <= 40 else topic[:37] + "..."
        buttons.append([{"text": label, "callback_data": f"r:{run_id}"}])
    text = "Незавершённые ходы. Нажми ход, чтобы вернуться, или напиши новую формулировку."
    if not rows:
        text = "Незавершённых ходов нет. Напиши новую формулировку."
    return [{"kind": "list", "text": text, "buttons": buttons}]


def resume(conn, person_id, run_id) -> list[dict]:
    run = focus(conn, person_id, run_id)
    if run is None:
        return [{"kind": "text", "text": "Этот ход уже закрыт или не твой."}]
    if run["step"] == "finalizing":
        from app.run_flow import _finish

        return _finish(conn, run)
    return [{"kind": "text", "text": continue_prompt(run)}]
