import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any
import pytest
from testcontainers.core.container import DockerContainer

from inbox_zero.shared.email_reader import ImapConfig
from inbox_zero.read_first_email.adapter import EmailReaderImap


def send_test_email(smtp_port: int, subject: str = "Test Email", body: str = "This is a test email body") -> None:
    msg = MIMEMultipart()
    msg["From"] = "sender@test.com"
    msg["To"] = "test@test.com"
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP("localhost", smtp_port, timeout=10) as server:
        server.sendmail("sender@test.com", "test@test.com", msg.as_string())


@pytest.fixture(scope="function")
def greenmail() -> Any:
    container = DockerContainer("greenmail/standalone:2.1.0-alpha-2")
    container.with_exposed_ports(3025, 3143)
    container.with_env("GREENMAIL_OPTS", "-Dgreenmail.setup.test.all -Dgreenmail.hostname=0.0.0.0 -Dgreenmail.auth.disabled=false -Dgreenmail.verbose")

    container.start()

    time.sleep(10)

    yield container

    container.stop()


def test_get_first_email_from_inbox(greenmail: Any) -> None:
    smtp_port = int(greenmail.get_exposed_port(3025))
    imap_port = int(greenmail.get_exposed_port(3143))

    send_test_email(smtp_port, subject="First Email", body="First body")

    config = ImapConfig(
        host="localhost",
        port=imap_port,
        username="test@test.com",
        password="test",
        use_ssl=False,
        folder="INBOX"
    )

    email_reader = EmailReaderImap()
    result = email_reader.get_first_email(config)

    assert result is not None
    assert result.subject == "First Email"
    assert result.sender == "sender@test.com"
    assert "First body" in result.body_text


def test_get_first_email_when_inbox_is_empty(greenmail: Any) -> None:
    imap_port = int(greenmail.get_exposed_port(3143))

    config = ImapConfig(
        host="localhost",
        port=imap_port,
        username="test@test.com",
        password="test",
        use_ssl=False,
        folder="INBOX"
    )

    email_reader = EmailReaderImap()
    result = email_reader.get_first_email(config)

    assert result is None


def test_get_first_email_when_multiple_emails(greenmail: Any) -> None:
    smtp_port = int(greenmail.get_exposed_port(3025))
    imap_port = int(greenmail.get_exposed_port(3143))

    send_test_email(smtp_port, subject="First Email", body="First body")
    send_test_email(smtp_port, subject="Second Email", body="Second body")
    send_test_email(smtp_port, subject="Third Email", body="Third body")

    config = ImapConfig(
        host="localhost",
        port=imap_port,
        username="test@test.com",
        password="test",
        use_ssl=False,
        folder="INBOX"
    )

    email_reader = EmailReaderImap()
    result = email_reader.get_first_email(config)

    assert result is not None
    assert result.subject == "First Email"
    assert result.sender == "sender@test.com"
