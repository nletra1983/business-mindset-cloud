import os

import httpx


class SmsNotConfigured(Exception):
    pass


def sms_text(code: str) -> str:
    return f"Код: {code}"


def send_code(phone: str, text: str) -> None:
    url = os.environ.get("SMS_WEBHOOK_URL", "").strip()
    if not url:
        raise SmsNotConfigured("код не отправлен")
    response = httpx.post(url, json={"phone": phone, "text": text}, timeout=10.0)
    response.raise_for_status()
