SETTINGS_CALLBACK = "settings"
SETTINGS_MODEL_CALLBACK = "settings:model"
SETTINGS_PROFILE_CALLBACK = "settings:profile"
SETTINGS_PREFIX = "settings:"

SETTINGS_LABEL = "настройки"
SETTINGS_TITLE = "Настройки аккаунта."
SETTINGS_MODEL_LABEL = "выбор модели"
SETTINGS_PROFILE_LABEL = "информация о себе"
SETTINGS_PHONE_CALLBACK = "settings:phone"
SETTINGS_PHONE_LABEL = "телефон"
SETTINGS_TELEGRAM_CALLBACK = "settings:telegram"
SETTINGS_TELEGRAM_LABEL = "Telegram"
PHONE_PROMPT = "Пришли номер телефона."
TELEGRAM_PROMPT = "Пришли идентификатор Telegram числом."
CODE_SENT = "Код отправлен. Пришли код из сообщения."
CODE_FAILED = "Код не отправлен."
CODE_REJECTED = "Код не подошёл."
PHONE_BAD = "Номер не разобран."
TELEGRAM_BAD = "Идентификатор Telegram не разобран."
PHONE_CONFIRMED = "Телефон подтверждён."
ENTRANCE_CONFIRMED = "Вход подтверждён."
ENTRANCES_MERGED = "Входы объединены."
SECOND_STILL_OPEN = "Второй вход ещё не подтверждён."
PHONE_EMPTY = "не указан"
PROFILE_STRENGTHS_PROMPT = "Напиши сильные стороны о себе одним сообщением."
PROFILE_WEAKNESSES_PROMPT = "Теперь напиши слабые стороны о себе одним сообщением."
PROFILE_FACT_PROMPT = "Добавь один факт о себе. Если не хочешь добавлять, напиши «нет»."
PROFILE_STRENGTHS_RETRY = "Пусто. Напиши сильные стороны о себе."
PROFILE_WEAKNESSES_RETRY = "Пусто. Напиши слабые стороны о себе."
PROFILE_FACT_RETRY = "Пусто. Напиши факт о себе или «нет»."
PROFILE_SAVED_TEXT = "Профиль сохранён."
PROFILE_FACT_ADDED_TEXT = "Факт добавлен."
PROFILE_FACT_SKIPPED_TEXT = "Ок, новый факт не добавляю."
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
        [{"text": SETTINGS_PHONE_LABEL, "callback_data": SETTINGS_PHONE_CALLBACK}],
        [{"text": SETTINGS_TELEGRAM_LABEL, "callback_data": SETTINGS_TELEGRAM_CALLBACK}],
    ]


def settings_menu_action(phone: str | None = None) -> dict:
    shown = phone or PHONE_EMPTY
    return {
        "kind": "settings_menu",
        "text": f"{SETTINGS_TITLE}\nТелефон: {shown}.",
        "buttons": settings_menu_buttons(),
    }


def profile_entry_action() -> dict:
    return {"kind": "text", "text": PROFILE_STRENGTHS_PROMPT}


def recoverable_action() -> dict:
    return {"kind": "text", "text": RECOVERABLE_TEXT}


def profile_start_actions(profile: dict, extras: list[dict] | None = None) -> list[dict]:
    return [
        {"kind": "text", "text": render_visible_profile(profile, extras)},
        {"kind": "text", "text": PROFILE_STRENGTHS_PROMPT},
    ]


def profile_saved_actions(profile: dict, fact_added: bool) -> list[dict]:
    note = PROFILE_FACT_ADDED_TEXT if fact_added else PROFILE_FACT_SKIPPED_TEXT
    return [
        {"kind": "text", "text": f"{note}\n{PROFILE_SAVED_TEXT}"},
        {"kind": "text", "text": render_visible_profile(profile)},
    ]


def _profile_sections(profile: dict) -> str:
    strengths = (profile.get("strengths_text") or "").strip() or "Пока не заполнено."
    weaknesses = (profile.get("weaknesses_text") or "").strip() or "Пока не заполнено."
    facts = profile.get("self_facts") or []
    if facts:
        facts_block = "\n".join(f"- {item}" for item in facts)
    else:
        facts_block = "Пока не добавлено."
    return (
        f"Сильные стороны:\n{strengths}\n\n"
        f"Слабые стороны:\n{weaknesses}\n\n"
        f"Сказано человеком:\n{facts_block}"
    )


def render_visible_profile(profile: dict, extras: list[dict] | None = None) -> str:
    blocks = ["Информация о себе.\n\n" + _profile_sections(profile)]
    for extra in extras or []:
        blocks.append("Другой вход.\n\n" + _profile_sections(extra))
    return "\n\n".join(blocks)
