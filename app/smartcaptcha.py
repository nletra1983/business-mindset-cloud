"""Yandex SmartCaptcha server-side token check."""

from __future__ import annotations

import json
import logging
import os
import urllib.error
import urllib.parse
import urllib.request

log = logging.getLogger("bot")

VALIDATE_URL = "https://smartcaptcha.cloud.yandex.ru/validate"


def client_key() -> str:
    return os.environ.get("SMARTCAPTCHA_CLIENT_KEY", "").strip()


def server_key() -> str:
    return os.environ.get("SMARTCAPTCHA_SERVER_KEY", "").strip()


def verify_token(token: str | None, ip: str | None = None) -> bool:
    """Return True only when Yandex status is ok. Fail closed without keys/token."""
    secret = server_key()
    raw = (token or "").strip()
    if not secret or not raw:
        return False
    data = {"secret": secret, "token": raw}
    if ip:
        data["ip"] = ip
    body = urllib.parse.urlencode(data).encode("utf-8")
    req = urllib.request.Request(
        VALIDATE_URL,
        data=body,
        method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        log.warning("smartcaptcha validate failed: %s", exc)
        return False
    return payload.get("status") == "ok"
