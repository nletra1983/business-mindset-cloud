import uuid

import httpx

from app.config import (
    DEEPSEEK_URL,
    GIGACHAT_OAUTH_URL,
    GIGACHAT_SCOPE,
    GIGACHAT_URL,
    GLM_URL,
    deepseek_key,
    gigachat_key,
    zai_key,
)

class ModelDown(Exception):
    pass


def complete(model_id: str, messages: list[dict]) -> tuple[str, str | None]:
    error: ModelDown | None = None
    for _ in range(2):
        try:
            return _once(model_id, messages)
        except ModelDown as exc:
            error = exc
    assert error is not None
    raise error


def _once(model_id: str, messages: list[dict]) -> tuple[str, str | None]:
    payload = {"model": model_id, "messages": messages, "temperature": 0.2}
    try:
        if model_id == "deepseek-chat":
            body = _post(
                DEEPSEEK_URL,
                {"Authorization": f"Bearer {deepseek_key()}"},
                payload,
            )
        elif model_id == "GigaChat-2":
            body = _post(
                GIGACHAT_URL,
                {"Authorization": f"Bearer {_gigachat_token()}"},
                payload,
            )
        elif model_id == "glm-5.3-flash":
            body = _post(
                GLM_URL,
                {"Authorization": f"Bearer {zai_key()}"},
                payload,
            )
        else:
            raise ModelDown
    except RuntimeError as exc:
        raise ModelDown from exc
    return _content(body)


def _gigachat_token() -> str:
    key = gigachat_key()
    auth = key if key.lower().startswith("basic ") else f"Basic {key}"
    try:
        response = httpx.post(
            GIGACHAT_OAUTH_URL,
            headers={
                "Authorization": auth,
                "RqUID": str(uuid.uuid4()),
                "Accept": "application/json",
            },
            data={"scope": GIGACHAT_SCOPE},
            timeout=40.0,
        )
        response.raise_for_status()
        token = response.json().get("access_token")
    except (httpx.HTTPError, ValueError, RuntimeError) as exc:
        raise ModelDown from exc
    if not isinstance(token, str) or not token.strip():
        raise ModelDown
    return token


def _post(url: str, headers: dict, payload: dict) -> dict:
    try:
        response = httpx.post(url, headers=headers, json=payload, timeout=40.0)
        response.raise_for_status()
        return response.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise ModelDown from exc


def _content(body: dict) -> tuple[str, str | None]:
    try:
        content = body["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, AttributeError, TypeError) as exc:
        raise ModelDown from exc
    if not content:
        raise ModelDown
    returned = body.get("model")
    if not isinstance(returned, str) or not returned.strip():
        returned = None
    return content, returned
