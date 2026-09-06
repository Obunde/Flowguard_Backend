"""Outbound SMTP. Only used to email onboarding credentials. Config: SMTP_*
in app/core/config.py. `send_email` is module-level so tests can monkeypatch
it.
"""
import logging
import smtplib
from email.message import EmailMessage

from app.core.config import settings

logger = logging.getLogger("flowgard.email")


class EmailNotConfiguredError(RuntimeError):
    """SMTP_HOST unset. Routes turn this into a 503."""


def send_email(*, to: str, subject: str, body: str) -> None:
    """Send a plain-text email. Blocking — onboarding invites only."""
    if not settings.smtp_host:
        raise EmailNotConfiguredError("SMTP_HOST is not set")

    message = EmailMessage()
    message["From"] = settings.smtp_from
    message["To"] = to
    message["Subject"] = subject
    message.set_content(body)

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
        if settings.smtp_use_tls:
            server.starttls()
        if settings.smtp_user:
            server.login(settings.smtp_user, settings.smtp_password)
        server.send_message(message)

    logger.info("sent %r email to %s", subject, to)
