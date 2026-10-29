SETTINGS_CALLBACK = "settings"
SETTINGS_MODEL_CALLBACK = "settings:model"
SETTINGS_PROFILE_CALLBACK = "settings:profile"
SETTINGS_PREFIX = "settings:"

SETTINGS_LABEL = "настройки"
SETTINGS_TITLE = "Настройки аккаунта."
SETTINGS_MODEL_LABEL = "выбор модели"
SETTINGS_PROFILE_LABEL = "информация о себе"
SETTINGS_EMAIL_CALLBACK = "settings:email"
SETTINGS_EMAIL_LABEL = "email"
SETTINGS_TELEGRAM_CALLBACK = "settings:telegram"
SETTINGS_TELEGRAM_LABEL = "Telegram"
EMAIL_LINK_PROMPT = "Пришли email."
TELEGRAM_LINK_PROMPT = "Пришли идентификатор Telegram числом."
LINK_CODE_SENT = "Код отправлен. Пришли код из сообщения."
LINK_CODE_FAILED = "Код не отправлен."
LINK_CODE_REJECTED = "Код не подошёл."
EMAIL_LINK_BAD = "Адрес не разобран."
TELEGRAM_LINK_BAD = "Идентификатор Telegram не разобран."
ENTRANCE_CONFIRMED = "Вход подтверждён."
ENTRANCES_MERGED = "Входы объединены."
SECOND_STILL_OPEN = "Второй вход ещё не подтверждён."
PROFILE_STRENGTHS_PROMPT = "Напиши сильные стороны о себе одним сообщением."
PROFILE_WEAKNESSES_PROMPT = "Теперь напиши слабые стороны о себе одним сообщением."
PROFILE_FACT_PROMPT = "Добавь один факт о себе. Если не хочешь добавлять, напиши «нет»."
PROFILE_STRENGTHS_RETRY = "Пусто. Напиши сильные стороны о себе."
PROFILE_WEAKNESSES_RETRY = "Пусто. Напиши слабые стороны о себе."
PROFILE_FACT_RETRY = "Пусто. Напиши факт о себе или «нет»."
PROFILE_SAVED_TEXT = "Профиль сохранён."
PROFILE_FACT_ADDED_TEXT = "Факт добавлен."
PROFILE_FACT_SKIPPED_TEXT = "Ок, новый факт не добавляю."
VOICE_UNSUPPORTED_TEXT = "Эта модель не разбирает голос."
VOICE_NOT_RECOGNIZED_TEXT = "Голос не разобран."
RECOVERABLE_TEXT = (
    "Этот экран устарел или больше недоступен. "
    "Нажми «настройки» в свежем сообщении."
)


def settings_button() -> dict:
    return {"text": SETTINGS_LABEL, "callback_data": SETTINGS_CALLBACK}


def settings_menu_buttons() -> list[list[dict]]:
    return [
        [{"text": SETTINGS_MODEL_LABEL, "callback_data": SETTINGS_MODEL_CALLBACK}],
        [{"text": SETTINGS_PROFILE_LABEL, "callback_data": SETTINGS_PROFILE_CALLBACK}],
        [{"text": SETTINGS_EMAIL_LABEL, "callback_data": SETTINGS_EMAIL_CALLBACK}],
        [{"text": SETTINGS_TELEGRAM_LABEL, "callback_data": SETTINGS_TELEGRAM_CALLBACK}],
    ]


def settings_menu_action() -> dict:
    return {
        "kind": "settings_menu",
        "text": SETTINGS_TITLE,
        "buttons": settings_menu_buttons(),
    }


def profile_entry_action() -> dict:
    return {"kind": "text", "text": PROFILE_STRENGTHS_PROMPT}


def recoverable_action() -> dict:
    return {"kind": "text", "text": RECOVERABLE_TEXT}


def voice_unsupported_action() -> dict:
    return {"kind": "text", "text": VOICE_UNSUPPORTED_TEXT}


def voice_not_recognized_action() -> dict:
    return {"kind": "text", "text": VOICE_NOT_RECOGNIZED_TEXT}


def profile_start_actions(profile: dict) -> list[dict]:
    return [
        {"kind": "text", "text": render_visible_profile(profile)},
        {"kind": "text", "text": PROFILE_STRENGTHS_PROMPT},
    ]


def profile_saved_actions(profile: dict, fact_added: bool) -> list[dict]:
    note = PROFILE_FACT_ADDED_TEXT if fact_added else PROFILE_FACT_SKIPPED_TEXT
    return [
        {"kind": "text", "text": f"{note}\n{PROFILE_SAVED_TEXT}"},
        {"kind": "text", "text": render_visible_profile(profile)},
    ]


def render_visible_profile(profile: dict) -> str:
    strengths = (profile.get("strengths_text") or "").strip() or "Пока не заполнено."
    weaknesses = (profile.get("weaknesses_text") or "").strip() or "Пока не заполнено."
    facts = profile.get("self_facts") or []
    if facts:
        facts_block = "\n".join(f"- {item}" for item in facts)
    else:
        facts_block = "Пока не добавлено."
    return (
        "Информация о себе.\n\n"
        f"Сильные стороны:\n{strengths}\n\n"
        f"Слабые стороны:\n{weaknesses}\n\n"
        f"Сказано человеком:\n{facts_block}"
    )
