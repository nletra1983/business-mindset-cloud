import logging
import time

import httpx

from app.account_settings import (
    PROFILE_FACT_PROMPT,
    PROFILE_FACT_RETRY,
    PROFILE_STRENGTHS_RETRY,
    PROFILE_WEAKNESSES_PROMPT,
    PROFILE_WEAKNESSES_RETRY,
    SETTINGS_CALLBACK,
    SETTINGS_MODEL_CALLBACK,
    SETTINGS_PREFIX,
    SETTINGS_PROFILE_CALLBACK,
    profile_saved_actions,
    profile_start_actions,
    recoverable_action,
    settings_menu_action,
    voice_not_recognized_action,
    voice_unsupported_action,
)
from app.config import telegram_base, telegram_token
from app.db import apply_schema, connect
from app.model_client import ModelDown, VoiceNotSupported, transcribe_voice
from app.model_switch import (
    MODEL_CALLBACK,
    PICK_TEXT,
    after_choice,
    apply_choice,
    is_model_id,
    model_keyboard,
)
from app.person import (
    PROFILE_AWAITING_EXTRA_FACT,
    PROFILE_AWAITING_STRENGTHS,
    PROFILE_AWAITING_WEAKNESSES,
    append_visible_fact,
    read_model_state,
    read_profile_edit_step,
    read_visible_profile,
    upsert_from_telegram,
    write_model_state,
    write_open_run_model,
    write_profile_edit_step,
    write_visible_strengths,
    write_visible_weaknesses,
)
from app.run_flow import handle_text, open_window
from app.run_list import exit_keyboard, exit_row, resume, show_list

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
        if "id" not in user or ("text" not in message and "voice" not in message):
            return
        _typing(message["chat"]["id"])
        person = upsert_from_telegram(conn, int(user["id"]), user.get("username"))
        if "voice" in message and "text" not in message:
            actions = _voice_message_actions(conn, person, message)
            if actions:
                _perform(message["chat"]["id"], actions, _current_model(conn, person["id"]))
            return
        if "text" not in message:
            return
        profile_actions = _profile_message_actions(conn, person["id"], message["text"])
        if profile_actions is not None:
            _perform(message["chat"]["id"], profile_actions, _current_model(conn, person["id"]))
            return
        actions = handle_text(
            conn,
            person,
            int(message["chat"]["id"]),
            int(message["message_id"]),
            message["text"],
        )
        _perform(message["chat"]["id"], actions, _current_model(conn, person["id"]))
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
    elif data == MODEL_CALLBACK or data == SETTINGS_CALLBACK or data.startswith(SETTINGS_PREFIX):
        actions = _settings_actions(conn, person["id"], data)
    elif data.startswith("m:"):
        _choose(conn, person["id"], data[2:])
        actions = [after_choice(int(message["message_id"]))]
    elif data.startswith("r:"):
        actions = resume(conn, person["id"], data[2:])
    else:
        actions = []
    _perform(chat["id"], actions, _current_model(conn, person["id"]))


def _current_model(conn, person_id) -> str:
    return read_model_state(conn, person_id)["current_model"]


def _settings_actions(conn, person_id, data: str) -> list[dict]:
    if data == SETTINGS_CALLBACK:
        return [settings_menu_action()]
    if data == SETTINGS_MODEL_CALLBACK or data == MODEL_CALLBACK:
        state = read_model_state(conn, person_id)
        return [{"kind": "models", "text": PICK_TEXT, "current": state["current_model"]}]
    if data == SETTINGS_PROFILE_CALLBACK:
        profile = read_visible_profile(conn, person_id)
        write_profile_edit_step(conn, person_id, PROFILE_AWAITING_STRENGTHS)
        conn.commit()
        return profile_start_actions(profile)
    if data.startswith(SETTINGS_PREFIX):
        return [recoverable_action()]
    return []


def _profile_message_actions(conn, person_id, text: str) -> list[dict] | None:
    step = read_profile_edit_step(conn, person_id)
    if step == "idle":
        return None

    value = text.strip()
    if step == PROFILE_AWAITING_STRENGTHS:
        if not value:
            return [{"kind": "text", "text": PROFILE_STRENGTHS_RETRY}]
        write_visible_strengths(conn, person_id, value)
        write_profile_edit_step(conn, person_id, PROFILE_AWAITING_WEAKNESSES)
        conn.commit()
        return [
            {"kind": "text", "text": "Сильные стороны сохранены."},
            {"kind": "text", "text": PROFILE_WEAKNESSES_PROMPT},
        ]

    if step == PROFILE_AWAITING_WEAKNESSES:
        if not value:
            return [{"kind": "text", "text": PROFILE_WEAKNESSES_RETRY}]
        write_visible_weaknesses(conn, person_id, value)
        write_profile_edit_step(conn, person_id, PROFILE_AWAITING_EXTRA_FACT)
        conn.commit()
        return [
            {"kind": "text", "text": "Слабые стороны сохранены."},
            {"kind": "text", "text": PROFILE_FACT_PROMPT},
        ]

    if step == PROFILE_AWAITING_EXTRA_FACT:
        if not value:
            return [{"kind": "text", "text": PROFILE_FACT_RETRY}]
        fact_added = value.lower() not in {"нет", "no", "skip", "-"}
        if fact_added:
            append_visible_fact(conn, person_id, value)
        write_profile_edit_step(conn, person_id, "idle")
        profile = read_visible_profile(conn, person_id)
        conn.commit()
        return profile_saved_actions(profile, fact_added)

    write_profile_edit_step(conn, person_id, "idle")
    conn.commit()
    return [recoverable_action()]


def _voice_message_actions(conn, person: dict, message: dict) -> list[dict]:
    voice = message.get("voice")
    if not isinstance(voice, dict):
        return []
    model_id = _current_model(conn, person["id"])
    if model_id != "GigaChat-2":
        return [voice_unsupported_action()]
    file_id = str(voice.get("file_id") or "").strip()
    if not file_id:
        return [voice_not_recognized_action()]
    try:
        voice_bytes = _download_voice_bytes(file_id)
        recognized_text = transcribe_voice(model_id, voice_bytes)
    except VoiceNotSupported:
        return [voice_unsupported_action()]
    except (ModelDown, httpx.HTTPError):
        return [voice_not_recognized_action()]

    text = recognized_text.strip()
    if not text:
        return [voice_not_recognized_action()]

    actions = [{"kind": "text", "text": text}]
    profile_actions = _profile_message_actions(conn, person["id"], text)
    if profile_actions is not None:
        actions.extend(profile_actions)
        return actions

    actions.extend(
        handle_text(
            conn,
            person,
            int(message["chat"]["id"]),
            int(message["message_id"]),
            text,
        )
    )
    return actions


def _choose(conn, person_id, model_id: str) -> str:
    state = read_model_state(conn, person_id)
    if not is_model_id(model_id):
        return state["current_model"]
    window = open_window(conn, person_id)
    target = window if window and window.get("status") == "open" else None
    apply_choice(state, target, model_id)
    write_model_state(conn, person_id, state)
    if target is not None:
        write_open_run_model(conn, target["id"], target["model_requested"])
    conn.commit()
    return state["current_model"]


def _perform(chat_id: int, actions: list[dict], current_model: str) -> None:
    for action in actions:
        kind = action["kind"]
        if kind == "pin":
            _call("pinChatMessage", {"chat_id": chat_id, "message_id": action["message_id"]})
        elif kind == "list":
            markup = {"inline_keyboard": action["buttons"]} if action["buttons"] else exit_keyboard(current_model)
            if action["buttons"]:
                markup["inline_keyboard"].append(exit_row(current_model))
            _call(
                "sendMessage",
                {"chat_id": chat_id, "text": action["text"], "reply_markup": markup},
            )
        elif kind == "plain_edit":
            try:
                _call(
                    "editMessageText",
                    {
                        "chat_id": chat_id,
                        "message_id": action["message_id"],
                        "text": action["text"],
                        "reply_markup": {"inline_keyboard": []},
                    },
                )
            except httpx.HTTPError:
                _call("sendMessage", {"chat_id": chat_id, "text": action["text"]})
        elif kind == "models":
            _call(
                "sendMessage",
                {
                    "chat_id": chat_id,
                    "text": action["text"],
                    "reply_markup": model_keyboard(action["current"]),
                },
            )
        elif kind == "settings_menu":
            _call(
                "sendMessage",
                {
                    "chat_id": chat_id,
                    "text": action["text"],
                    "reply_markup": {"inline_keyboard": action["buttons"]},
                },
            )
        else:
            _call(
                "sendMessage",
                {
                    "chat_id": chat_id,
                    "text": action["text"],
                    "reply_markup": exit_keyboard(current_model),
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


def _file_url(file_path: str) -> str:
    base = telegram_base()
    token = telegram_token()
    normalized = file_path.lstrip("/")
    if base.endswith("/bot"):
        return f"{base[:-4]}/file/bot{token}/{normalized}"
    return f"{base}/file/bot{token}/{normalized}"


def _download_voice_bytes(file_id: str) -> bytes:
    body = _call("getFile", {"file_id": file_id})
    file_path = ((body.get("result") or {}).get("file_path") or "").strip()
    if not file_path:
        raise httpx.HTTPError("missing telegram file_path")
    response = httpx.get(_file_url(file_path), timeout=40.0)
    response.raise_for_status()
    return response.content


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
