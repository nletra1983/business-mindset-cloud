SETTINGS_CALLBACK = "settings"
SETTINGS_MODEL_CALLBACK = "settings:model"
SETTINGS_PROFILE_CALLBACK = "settings:profile"
SETTINGS_PREFIX = "settings:"

SETTINGS_LABEL = "настройки"
SETTINGS_TITLE = "Настройки аккаунта."
SETTINGS_MODEL_LABEL = "выбор модели"
SETTINGS_PROFILE_LABEL = "информация о себе"
PROFILE_ENTRY_TEXT = (
    "Раздел «информация о себе» в этой истории только как точка входа. "
    "Скоро здесь можно будет читать и менять записи о себе."
)
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
    ]


def settings_menu_action() -> dict:
    return {
        "kind": "settings_menu",
        "text": SETTINGS_TITLE,
        "buttons": settings_menu_buttons(),
    }


def profile_entry_action() -> dict:
    return {"kind": "text", "text": PROFILE_ENTRY_TEXT}


def recoverable_action() -> dict:
    return {"kind": "text", "text": RECOVERABLE_TEXT}
