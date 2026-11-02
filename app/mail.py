import os
import smtplib
from email.message import EmailMessage


class MailNotConfigured(Exception):
    pass


def mail_text(code: str) -> str:
    return f"Код: {code}"


def send_message(email: str, subject: str, text: str) -> None:
    host = os.environ.get("MAIL_SMTP_HOST", "").strip()
    user = os.environ.get("MAIL_SMTP_USER", "").strip()
    password = os.environ.get("MAIL_SMTP_PASSWORD", "").strip()
    mail_from = os.environ.get("MAIL_FROM", "").strip() or user
    port_raw = os.environ.get("MAIL_SMTP_PORT", "465").strip() or "465"
    if not host or not user or not password:
        raise MailNotConfigured("письмо не отправлено")
    port = int(port_raw)

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = mail_from
    message["To"] = email
    message.set_content(text)

    if port == 465:
        with smtplib.SMTP_SSL(host, port, timeout=10) as smtp:
            smtp.login(user, password)
            smtp.send_message(message)
        return

    with smtplib.SMTP(host, port, timeout=10) as smtp:
        smtp.starttls()
        smtp.login(user, password)
        smtp.send_message(message)


def send_code(email: str, text: str) -> None:
    send_message(email, "Код входа", text)
