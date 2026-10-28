from app.model_client import ModelDown, complete


_EVENT_RULES = (
    "Блок «Событие». Достаточно: факт отделён от интерпретации, изменение названо "
    "(правила, технология, поведение, цена или доступ). "
    "Слабо: пересказ заголовка или сразу идея продукта / «сделаем приложение»."
)

_SCALE_RULES = (
    "Блок «Масштаб». Достаточно: группы названы по имени (не «все»), есть место/отрасль "
    "и срок или обратимость. "
    "Слабо: «все», «рынок», «всегда» без места и срока."
)


def parse_judge_reply(text: str) -> tuple[bool, str]:
    """Parse ДОСТАТОЧНО / НЕХВАТАЕТ from model reply."""
    lines = [line.strip() for line in (text or "").splitlines() if line.strip()]
    enough = None
    missing = ""
    for line in lines:
        upper = line.upper()
        if upper.startswith("ДОСТАТОЧНО:"):
            value = line.split(":", 1)[1].strip().lower()
            enough = value in ("да", "yes", "true", "1", "+")
        elif upper.startswith("НЕХВАТАЕТ:"):
            missing = line.split(":", 1)[1].strip()
    if enough is None:
        raise ModelDown
    if enough:
        return True, ""
    if not missing:
        missing = "Ответ слабый. Уточни по правилам блока."
    return False, missing


def judge_block(block: str, topic: str, answer: str, model_id: str) -> tuple[bool, str, str | None]:
    """Evaluate answer with DeepSeek against smoke rules. block: event|scale."""
    rules = _EVENT_RULES if block == "event" else _SCALE_RULES
    text, returned = complete(
        model_id,
        [
            {
                "role": "system",
                "content": (
                    "Ты оцениваешь ответ человека в коротком упражнении. "
                    "Не выдумывай факты. Не предлагай продукт. "
                    "Ответь ровно двумя строками:\n"
                    "ДОСТАТОЧНО: да\n"
                    "или\n"
                    "ДОСТАТОЧНО: нет\n"
                    "НЕХВАТАЕТ: одно короткое предложение, чего не хватает "
                    "(только если ДОСТАТОЧНО: нет).\n"
                    f"Правила блока:\n{rules}"
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Формулировка темы: {topic}\n"
                    f"Ответ человека: {answer}"
                ),
            },
        ]
    )
    ok, missing = parse_judge_reply(text)
    return ok, missing, returned


def finale(topic: str, event_answer: str, scale_answer: str, model_id: str) -> tuple[str, str, str, str, str | None]:
    text, returned = complete(
        model_id,
        [
            {
                "role": "system",
                "content": (
                    "Ты ведёшь короткую тестовую сессию. Не выдумывай факты сверх слов человека. "
                    "Не предлагай новый продукт. Ответь ровно тремя абзацами с метками "
                    "ПОЛУЧИЛОСЬ:, СЛАБО:, ПРОПУЩЕНО:. "
                    "В ПРОПУЩЕНО одна фраза: в полной тренировке дальше были бы потери/выигрыш, "
                    "потребности, варианты и фильтр; сейчас сессия тестовая и на этом останавливается."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Формулировка: {topic}\n"
                    f"Событие: {event_answer}\n"
                    f"Масштаб: {scale_answer}"
                ),
            },
        ]
    )
    worked = _section(text, "ПОЛУЧИЛОСЬ:", "СЛАБО:")
    weak = _section(text, "СЛАБО:", "ПРОПУЩЕНО:")
    missed = _section(text, "ПРОПУЩЕНО:", None)
    if not worked or not weak or not missed:
        raise ModelDown
    return text, worked, weak, missed, returned


def _section(text: str, start: str, end: str | None) -> str:
    low = text
    begin = low.find(start)
    if begin < 0:
        return ""
    begin += len(start)
    if end is None:
        return low[begin:].strip()
    stop = low.find(end, begin)
    if stop < 0:
        return low[begin:].strip()
    return low[begin:stop].strip()
