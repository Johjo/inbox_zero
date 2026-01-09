import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pytest
from testcontainers.core.container import DockerContainer

from adapters.email_repository_imap import EmailRepositoryImap


def send_test_email(smtp_port, subject="Test Email", body="This is a test email body"):
    msg = MIMEMultipart()
    msg["From"] = "sender@test.com"
    msg["To"] = "test@test.com"
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP("localhost", smtp_port, timeout=10) as server:
        server.sendmail("sender@test.com", "test@test.com", msg.as_string())


@pytest.fixture(scope="function")
def greenmail():
    container = DockerContainer("greenmail/standalone:2.1.0-alpha-2")
    container.with_exposed_ports(3025, 3143)
    container.with_env("GREENMAIL_OPTS", "-Dgreenmail.setup.test.all -Dgreenmail.hostname=0.0.0.0 -Dgreenmail.auth.disabled=false -Dgreenmail.verbose")

    container.start()

    time.sleep(10)

    yield container

    container.stop()


def test_get_first_email_from_inbox(greenmail):
    smtp_port = greenmail.get_exposed_port(3025)
    imap_port = greenmail.get_exposed_port(3143)

    send_test_email(smtp_port, subject="First Email", body="First body")

    repository = EmailRepositoryImap(
        host="localhost",
        port=imap_port,
        username="test@test.com",
        password="test",
        use_ssl=False
    )

    result = repository.get_first_email("INBOX")

    assert result is not None
    assert result.subject == "First Email"
    assert result.sender == "sender@test.com"
    assert "First body" in result.body_text


def test_get_first_email_when_inbox_is_empty(greenmail):
    imap_port = greenmail.get_exposed_port(3143)

    repository = EmailRepositoryImap(
        host="localhost",
        port=imap_port,
        username="test@test.com",
        password="test",
        use_ssl=False
    )

    result = repository.get_first_email("INBOX")

    assert result is None


def test_get_first_email_when_multiple_emails(greenmail):
    smtp_port = greenmail.get_exposed_port(3025)
    imap_port = greenmail.get_exposed_port(3143)

    send_test_email(smtp_port, subject="First Email", body="First body")
    send_test_email(smtp_port, subject="Second Email", body="Second body")
    send_test_email(smtp_port, subject="Third Email", body="Third body")

    repository = EmailRepositoryImap(
        host="localhost",
        port=imap_port,
        username="test@test.com",
        password="test",
        use_ssl=False
    )

    result = repository.get_first_email("INBOX")

    assert result is not None
    assert result.subject == "First Email"
    assert result.sender == "sender@test.com"
