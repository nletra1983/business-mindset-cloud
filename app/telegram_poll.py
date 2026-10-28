import logging
import time

import httpx

from app.config import telegram_base, telegram_token
from app.db import apply_schema, connect
from app.person import upsert_from_telegram
from app.run_flow import handle_text
from app.run_list import exit_keyboard, resume, show_list

log = logging.getLogger("bot")


def poll() -> None:
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    conn = connect()
    apply_schema(conn)
    offset = _load_offset(conn)
    while True:
        try:
            updates = _get_updates(offset)
        except httpx.HTTPError:
            log.exception("getUpdates failed")
            time.sleep(2)
            continue
        for update in updates:
            update_id = int(update["update_id"])
            offset = update_id + 1
            if _seen(conn, update_id):
                _save_offset(conn, offset)
                continue
            try:
                _dispatch(conn, update)
                _mark(conn, update_id)
                _save_offset(conn, offset)
            except Exception:
                log.exception("update failed")
                conn.rollback()


def _dispatch(conn, update: dict) -> None:
    if "message" in update:
        message = update["message"]
        user = message.get("from") or {}
        if "id" not in user or "text" not in message:
            return
        _typing(message["chat"]["id"])
        person = upsert_from_telegram(conn, int(user["id"]), user.get("username"))
        actions = handle_text(
            conn,
            person,
            int(message["chat"]["id"]),
            int(message["message_id"]),
            message["text"],
        )
        _perform(message["chat"]["id"], actions)
        return
    if "callback_query" not in update:
        return
    query = update["callback_query"]
    user = query.get("from") or {}
    message = query.get("message") or {}
    chat = message.get("chat") or {}
    if "id" not in user or "id" not in chat:
        return
    data = query.get("data") or ""
    _answer_callback(query["id"])
    person = upsert_from_telegram(conn, int(user["id"]), user.get("username"))
    if data == "to_list":
        actions = show_list(conn, person["id"])
    elif data.startswith("r:"):
        actions = resume(conn, person["id"], data[2:])
    else:
        actions = []
    _perform(chat["id"], actions)


def _perform(chat_id: int, actions: list[dict]) -> None:
    for action in actions:
        kind = action["kind"]
        if kind == "pin":
            _call("pinChatMessage", {"chat_id": chat_id, "message_id": action["message_id"]})
        elif kind == "list":
            markup = {"inline_keyboard": action["buttons"]} if action["buttons"] else exit_keyboard()
            if action["buttons"]:
                markup["inline_keyboard"].append([{"text": "к другим вопросам", "callback_data": "to_list"}])
            _call(
                "sendMessage",
                {"chat_id": chat_id, "text": action["text"], "reply_markup": markup},
            )
        else:
            _call(
                "sendMessage",
                {
                    "chat_id": chat_id,
                    "text": action["text"],
                    "reply_markup": exit_keyboard(),
                },
            )


def _get_updates(offset: int | None) -> list[dict]:
    payload: dict = {"timeout": 30}
    if offset is not None:
        payload["offset"] = offset
    body = _call("getUpdates", payload)
    return body.get("result") or []


def _typing(chat_id: int) -> None:
    try:
        _call("sendChatAction", {"chat_id": chat_id, "action": "typing"})
    except httpx.HTTPError:
        log.exception("typing failed")


def _answer_callback(callback_id: str) -> None:
    try:
        _call("answerCallbackQuery", {"callback_query_id": callback_id})
    except httpx.HTTPError:
        log.exception("callback answer failed")


def _call(method: str, payload: dict) -> dict:
    response = httpx.post(_url(method), json=payload, timeout=40.0)
    response.raise_for_status()
    body = response.json()
    if not body.get("ok", False):
        raise httpx.HTTPError("telegram method failed")
    return body


def _url(method: str) -> str:
    base = telegram_base()
    token = telegram_token()
    if base.endswith("/bot"):
        return f"{base}{token}/{method}"
    return f"{base}/bot{token}/{method}"


def _seen(conn, update_id: int) -> bool:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT 1 FROM processed_telegram_update WHERE update_id = %s",
            (update_id,),
        )
        return cur.fetchone() is not None


def _mark(conn, update_id: int) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO processed_telegram_update (update_id)
            VALUES (%s)
            ON CONFLICT (update_id) DO NOTHING
            """,
            (update_id,),
        )
    conn.commit()


def _load_offset(conn) -> int | None:
    with conn.cursor() as cur:
        cur.execute("SELECT value FROM bot_kv WHERE key = 'offset'")
        row = cur.fetchone()
    if row is None:
        return None
    return int(row[0])


def _save_offset(conn, offset: int) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO bot_kv (key, value) VALUES ('offset', %s)
            ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value
            """,
            (str(offset),),
        )
    conn.commit()
