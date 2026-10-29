from app.entrances import begin_email_login, confirm_email_login

EMAIL_PROMPT = "Укажи email."
EMAIL_BAD = "Адрес не разобран."
CODE_PROMPT = "Пришли код из письма."
CODE_FAILED = "Код не отправлен."
CODE_REJECTED = "Код не подошёл."
EMPTY_LIST = "Ходов пока нет."


def start_screen() -> dict:
    return _screen("email", EMAIL_PROMPT, inside=False, runs=[])


def submit_email(book, raw: str) -> dict:
    result = begin_email_login(book, raw)
    if result["ok"]:
        return _screen("code", CODE_PROMPT, inside=False, runs=[], email=result["email"])
    if result.get("reason") == "mail":
        return _screen("email", CODE_FAILED, inside=False, runs=[])
    return _screen("email", EMAIL_BAD, inside=False, runs=[])


def submit_code(book, email: str, code: str) -> dict:
    before = len(getattr(book, "people", {}))
    result = confirm_email_login(book, email, code)
    if not result["ok"]:
        screen = _screen("code", CODE_REJECTED, inside=False, runs=[])
        screen["created"] = len(getattr(book, "people", {})) > before
        return screen
    runs = list(book.runs_of(result["person_id"]))
    text = EMPTY_LIST if not runs else "\n".join(str(item) for item in runs)
    screen = _screen("list", text, inside=True, runs=runs)
    screen["person_id"] = result["person_id"]
    screen["created"] = result["created"]
    return screen


def _screen(step: str, text: str, *, inside: bool, runs: list, email: str | None = None) -> dict:
    screen = {
        "step": step,
        "text": text,
        "inside": inside,
        "runs": runs,
        "actions": [],
        "mentions_telegram": "telegram" in text.lower(),
    }
    if email is not None:
        screen["email"] = email
    return screen
