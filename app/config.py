import os
from pathlib import Path

SKILL_VERSION = "business-idea-from-news.smoke"
SKILL_RELATIVE = Path(
    "features/business-idea-from-news/FeatureArtifacts/business-idea-from-news.smoke.md"
)
MODEL_REQUESTED = "deepseek-chat"
ACCESS_MODE = "service_free"
DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"
GIGACHAT_OAUTH_URL = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
GIGACHAT_URL = "https://api.giga.chat/v1/chat/completions"
GIGACHAT_SCOPE = "GIGACHAT_API_PERS"
GLM_URL = "https://api.z.ai/api/paas/v4/chat/completions"
MODELS = (
    {"id": "deepseek-chat", "label": "DeepSeek"},
    {"id": "GigaChat-2", "label": "GigaChat"},
    {"id": "glm-5.3-flash", "label": "GLM"},
)


def _env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"missing env {name}")
    return value


def telegram_base() -> str:
    return _env("TELEGRAM_API_BASE").rstrip("/")


def telegram_token() -> str:
    return _env("TG_GETBUSINESSIDEA_TOKEN")


def gigachat_key() -> str:
    return _env("GIGACHAT_AUTH_KEY")


def zai_key() -> str:
    return _env("ZAI_API_KEY")


def deepseek_key() -> str:
    if os.environ.get("DEEPSEEK_API_KEY", "").strip():
        return os.environ["DEEPSEEK_API_KEY"].strip()
    for candidate in (
        Path("/opt/business-mindset/secrets/deepseek.env"),
        Path(".secrets/deepseek.env"),
    ):
        if not candidate.is_file():
            continue
        for line in candidate.read_text(encoding="utf-8").splitlines():
            if line.startswith("DEEPSEEK_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise RuntimeError("missing DEEPSEEK_API_KEY")


def database_url() -> str | None:
    value = os.environ.get("DATABASE_URL", "").strip()
    if value:
        return value
    user = os.environ.get("POSTGRES_USER", "").strip()
    password = os.environ.get("POSTGRES_PASSWORD", "").strip()
    name = os.environ.get("POSTGRES_DB", "").strip()
    host = os.environ.get("POSTGRES_HOST", "db").strip() or "db"
    if user and password and name:
        return f"postgresql://{user}:{password}@{host}:5432/{name}"
    return None


def skill_path() -> Path:
    here = Path(__file__).resolve()
    root = here.parents[1]
    return root / SKILL_RELATIVE
