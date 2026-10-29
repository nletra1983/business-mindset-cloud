from app.person import set_accepting_new
from app.run_flow import handle_text
from app.run_list import resume, show_list

LIST_ACTIONS = ("new", "resume")
EXCLUDED_ACTIONS = ("past", "redo", "delete")


def list_screen(conn, person_id) -> dict:
    shown = show_list(conn, person_id)
    return {
        "actions": list(LIST_ACTIONS),
        "excluded": list(EXCLUDED_ACTIONS),
        "shown": shown,
    }


def begin_from_list(conn, person: dict, chat_id: int, message_id: int, text: str) -> list[dict]:
    set_accepting_new(conn, person["id"], True)
    ready = dict(person)
    ready["accepting_new"] = True
    return handle_text(conn, ready, chat_id, message_id, text)


def resume_from_list(conn, person_id, run_id) -> list[dict]:
    return resume(conn, person_id, run_id)
