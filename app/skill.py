from app.config import SKILL_VERSION, skill_path

MISSED_LINE = (
    "В полной тренировке дальше были бы потери/выигрыш, потребности, варианты и фильтр; "
    "сейчас сессия тестовая и на этом останавливается."
)


def load_text() -> str:
    return skill_path().read_text(encoding="utf-8")


def version() -> str:
    text = load_text()
    if SKILL_VERSION not in text:
        raise RuntimeError("smoke skill version marker missing")
    return SKILL_VERSION


def blank_topic(text: str) -> bool:
    raw = (text or "").strip()
    if not raw:
        return True
    lowered = raw.lower()
    if lowered.startswith("http://") or lowered.startswith("https://"):
        return True
    return not any(ch.isalpha() for ch in raw)


def event_prompt(topic: str) -> str:
    return (
        f"Факт: {topic}\n"
        f"Что в «{topic}» произошло? Назови факт и что изменилось: "
        "правила, технология, поведение, цена или доступ. Идею продукта не предлагай."
    )


def scale_prompt(topic: str) -> str:
    return (
        f"Кто сталкивается с «{topic}»? Назови группы по их работе, где они и в какой отрасли. "
        "С какого момента это для них началось и можно ли это откатить?"
    )
