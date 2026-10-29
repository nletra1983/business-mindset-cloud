import os

import httpx


class MailNotConfigured(Exception):
    pass


def mail_text(code: str) -> str:
    return f"Код: {code}"


def send_code(email: str, text: str) -> None:
    url = os.environ.get("MAIL_WEBHOOK_URL", "").strip()
    if not url:
        raise MailNotConfigured("код не отправлен")
    response = httpx.post(url, json={"email": email, "text": text}, timeout=10.0)
    response.raise_for_status()
