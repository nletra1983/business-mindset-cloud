from app.app_entry import submit_code, submit_email
from app.app_links import second_entrance_screen, submit_email_link, submit_link_code, submit_telegram_link
from app.app_news import EXCLUDED_ACTIONS, LIST_ACTIONS, begin_from_list, list_screen, resume_from_list
from app.app_settings import (
    choose_model_for_person,
    model_screen,
    open_settings,
    save_fact,
    save_strengths,
    save_weaknesses,
    show_profile,
)
from app.person import read_model_state, read_visible_profile

_BLANK_TOPIC = "Пусто. Сформулируй новость или проблему своими словами."

APP_PREFIX = "/app/v1"


def dispatch(method: str, path: str, headers: dict, body: dict, *, book, sessions, conn=None) -> dict:
    path = (path or "").split("?")[0].rstrip("/") or "/"
    method = (method or "GET").upper()
    if not path.startswith(APP_PREFIX):
        return _error(404, "not_found", "путь не найден")

    rel = path[len(APP_PREFIX) :] or "/"
    if rel == "/auth/email/request" and method == "POST":
        return _request_email(book, body)
    if rel == "/auth/email/confirm" and method == "POST":
        return _confirm_email(book, sessions, body)
    if rel == "/auth/logout" and method == "POST":
        return _logout(sessions, headers)
    person_id = _person(sessions, headers)
    if person_id is None and rel not in {"/auth/email/request", "/auth/email/confirm", "/auth/logout"}:
        return _error(401, "unauthorized", "нужна сессия")

    if rel == "/runs" and method == "GET":
        return _list_runs(conn, book, person_id)
    if rel == "/runs/leave" and method == "POST":
        return _leave_to_list(conn, book, person_id)
    if rel == "/runs" and method == "POST":
        return _idempotent(
            sessions,
            person_id,
            headers,
            lambda: _start_run(conn, book, person_id, body),
        )
    if rel.startswith("/runs/") and rel.endswith("/resume") and method == "POST":
        run_id = rel[len("/runs/") : -len("/resume")]
        if conn is None:
            return _error(400, "no_store", "ход без базы не открыть")
        return _ok({"actions": resume_from_list(conn, person_id, run_id)})
    if rel.startswith("/runs/") and rel.endswith("/answers") and method == "POST":
        run_id = rel[len("/runs/") : -len("/answers")]
        return _idempotent(
            sessions,
            person_id,
            headers,
            lambda: _answer_run(conn, book, person_id, run_id, body),
        )
    if rel == "/settings" and method == "GET":
        return _ok(open_settings())
    if rel == "/settings/models" and method == "GET":
        state = read_model_state(conn, person_id) if conn is not None else {"current_model": "deepseek-chat"}
        return _ok(model_screen(state["current_model"]))
    if rel == "/settings/models" and method == "POST":
        return _ok(choose_model_for_person(conn, person_id, (body or {}).get("model_id") or ""))
    if rel == "/settings/profile" and method == "GET":
        profile = (
            read_visible_profile(conn, person_id)
            if conn is not None
            else {"strengths_text": "", "weaknesses_text": "", "self_facts": []}
        )
        return _ok(show_profile(profile))
    if rel == "/settings/profile/strengths" and method == "POST":
        return _ok(save_strengths(conn, person_id, (body or {}).get("text") or ""))
    if rel == "/settings/profile/weaknesses" and method == "POST":
        return _ok(save_weaknesses(conn, person_id, (body or {}).get("text") or ""))
    if rel == "/settings/profile/fact" and method == "POST":
        return _ok(save_fact(conn, person_id, (body or {}).get("text") or ""))
    if rel == "/settings/second-entrance" and method == "GET":
        return _ok(second_entrance_screen())
    if rel == "/settings/second-entrance/email" and method == "POST":
        return _ok(submit_email_link(book, person_id, (body or {}).get("email") or ""))
    if rel == "/settings/second-entrance/telegram" and method == "POST":
        return _ok(submit_telegram_link(book, person_id, (body or {}).get("telegram") or ""))
    if rel == "/settings/second-entrance/code" and method == "POST":
        return _ok(submit_link_code(book, person_id, (body or {}).get("code") or ""))
    if rel == "/news/list" and method == "GET":
        return _ok(list_screen(conn, person_id) if conn is not None else {"actions": ["new", "resume"]})
    return _error(404, "not_found", "путь не найден")


def _request_email(book, body: dict) -> dict:
    screen = submit_email(book, (body or {}).get("email") or "")
    if screen["step"] == "code":
        return _ok({"status": "code_sent", "email": screen["email"]})
    return _error(400, "email_failed", screen["text"])


def _confirm_email(book, sessions, body: dict) -> dict:
    email = (body or {}).get("email") or ""
    code = (body or {}).get("code") or ""
    screen = submit_code(book, email, code)
    if not screen.get("inside"):
        return _error(401, "code_rejected", screen["text"])
    secret = sessions.issue(screen["person_id"])
    return _ok(
        {
            "session_secret": secret,
            "person_id": str(screen["person_id"]),
            "runs": screen["runs"],
        }
    )


def _logout(sessions, headers: dict) -> dict:
    auth = headers.get("Authorization") or headers.get("authorization") or ""
    secret = auth[7:].strip() if auth.lower().startswith("bearer ") else ""
    revoked = sessions.revoke(secret) if secret else False
    return _ok({"signed_out": True, "revoked": revoked})


def _list_runs(conn, book, person_id) -> dict:
    if conn is None:
        return _ok(
            {
                "runs": list(book.runs_of(person_id)),
                "actions": list(LIST_ACTIONS),
                "excluded": list(EXCLUDED_ACTIONS),
            }
        )
    from app.run_flow import open_runs

    runs = [
        {"id": str(run_id), "topic": topic, "step": step}
        for run_id, topic, step, _version in open_runs(conn, person_id)
    ]
    return _ok(
        {
            "runs": runs,
            "actions": list(LIST_ACTIONS),
            "excluded": list(EXCLUDED_ACTIONS),
        }
    )


def _leave_to_list(conn, book, person_id) -> dict:
    """Leave the open run window unfinished and return the list (no pause status)."""
    if conn is not None:
        from app.run_flow import leave_window

        leave_window(conn, person_id)
    return _list_runs(conn, book, person_id)


def _start_run(conn, book, person_id, body: dict) -> dict:
    topic = ((body or {}).get("topic") or "").strip()
    if not topic:
        return _error(400, "blank_topic", _BLANK_TOPIC)
    if conn is None:
        runs = list(book.runs_of(person_id))
        runs.append(topic)
        if hasattr(book, "people") and str(person_id) in book.people:
            book.people[str(person_id)]["runs"] = runs
        return _ok({"started": True, "topic": topic, "runs": runs})
    person = {
        "id": person_id,
        "accepting_new": True,
        "current_model": read_model_state(conn, person_id)["current_model"],
    }
    actions = begin_from_list(conn, person, chat_id=0, message_id=0, text=topic)
    return _ok({"actions": actions, "topic": topic})


def _answer_run(conn, book, person_id, run_id, body: dict) -> dict:
    if conn is None:
        text = ((body or {}).get("text") or "").strip()
        person = book.people.setdefault(str(person_id), {"runs": [], "answers": {}})
        answers = person.setdefault("answers", {})
        answers[run_id] = answers.get(run_id, 0) + 1
        return _ok(
            {
                "actions": [{"kind": "text", "text": f"принято:{text}"}],
                "step_moves": answers[run_id],
                "run_id": run_id,
            }
        )
    from app.run_flow import handle_text

    person = {
        "id": person_id,
        "accepting_new": False,
        "current_model": read_model_state(conn, person_id)["current_model"],
    }
    actions = handle_text(conn, person, chat_id=0, message_id=0, text=(body or {}).get("text") or "")
    return _ok({"actions": actions, "run_id": run_id})


def _idempotent(sessions, person_id, headers: dict, compute):
    key = (headers.get("Idempotency-Key") or headers.get("idempotency-key") or "").strip()
    if key:
        cached = sessions.get_operation(person_id, key)
        if cached is not None:
            return cached
    result = compute()
    if key and result.get("ok"):
        sessions.save_operation(person_id, key, result)
    return result


def _person(sessions, headers: dict):
    auth = headers.get("Authorization") or headers.get("authorization") or ""
    if not auth.lower().startswith("bearer "):
        return None
    return sessions.person_id(auth[7:].strip())


def _ok(payload: dict) -> dict:
    return {"ok": True, "status": 200, "body": payload}


def _error(status: int, code: str, message: str) -> dict:
    return {"ok": False, "status": status, "body": {"error": code, "message": message}}
