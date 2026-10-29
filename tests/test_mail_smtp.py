import os
from unittest.mock import MagicMock, patch

import pytest

from app.mail import MailNotConfigured, send_code


def test_send_code_requires_smtp_settings(monkeypatch):
    for name in (
        "MAIL_SMTP_HOST",
        "MAIL_SMTP_PORT",
        "MAIL_SMTP_USER",
        "MAIL_SMTP_PASSWORD",
        "MAIL_FROM",
        "MAIL_WEBHOOK_URL",
    ):
        monkeypatch.delenv(name, raising=False)
    with pytest.raises(MailNotConfigured):
        send_code("a@example.com", "Код: 1234")


def test_send_code_uses_smtp_ssl_on_465(monkeypatch):
    monkeypatch.setenv("MAIL_SMTP_HOST", "smtp.example.com")
    monkeypatch.setenv("MAIL_SMTP_PORT", "465")
    monkeypatch.setenv("MAIL_SMTP_USER", "bot@example.com")
    monkeypatch.setenv("MAIL_SMTP_PASSWORD", "secret")
    monkeypatch.setenv("MAIL_FROM", "bot@example.com")

    smtp = MagicMock()
    smtp.__enter__.return_value = smtp
    with patch("app.mail.smtplib.SMTP_SSL", return_value=smtp) as factory:
        send_code("person@example.com", "Код: 1234")

    factory.assert_called_once_with("smtp.example.com", 465, timeout=10)
    smtp.login.assert_called_once_with("bot@example.com", "secret")
    smtp.send_message.assert_called_once()
    message = smtp.send_message.call_args.args[0]
    assert message["To"] == "person@example.com"
    assert message["From"] == "bot@example.com"
    assert message.get_content().strip() == "Код: 1234"
