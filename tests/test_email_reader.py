import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import pytest
from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_for_logs
from email_reader import EmailReader


@pytest.fixture(scope="function")
def greenmail_container():
    container = DockerContainer("greenmail/standalone:2.1.0-alpha-2")
    container.with_exposed_ports(3025, 3143)
    container.with_env("GREENMAIL_OPTS", "-Dgreenmail.setup.test.all -Dgreenmail.hostname=0.0.0.0 -Dgreenmail.auth.disabled=false -Dgreenmail.verbose")

    container.start()

    time.sleep(5)

    yield container

    container.stop()


def send_test_email(container, subject="Test Email", body="This is a test email body"):
    smtp_port = container.get_exposed_port(3025)

    msg = MIMEMultipart()
    msg["From"] = "sender@test.com"
    msg["To"] = "test@test.com"
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP("localhost", smtp_port) as server:
        server.sendmail("sender@test.com", "test@test.com", msg.as_string())


def send_test_email_with_attachment(container):
    smtp_port = container.get_exposed_port(3025)

    msg = MIMEMultipart()
    msg["From"] = "sender@test.com"
    msg["To"] = "test@test.com"
    msg["Subject"] = "Email with Attachment"

    msg.attach(MIMEText("Email with attachment", "plain"))

    attachment = MIMEBase("application", "octet-stream")
    attachment.set_payload(b"Test file content")
    encoders.encode_base64(attachment)
    attachment.add_header("Content-Disposition", "attachment", filename="test.txt")
    msg.attach(attachment)

    with smtplib.SMTP("localhost", smtp_port) as server:
        server.sendmail("sender@test.com", "test@test.com", msg.as_string())


def test_fetch_emails_basic(greenmail_container):
    send_test_email(greenmail_container, subject="Hello World", body="Test body content")

    imap_port = greenmail_container.get_exposed_port(3143)

    reader = EmailReader(
        host="localhost",
        port=imap_port,
        username="test@test.com",
        password="test",
        use_ssl=False
    )

    emails = reader.fetch_emails()

    assert len(emails) == 1
    assert emails[0].subject == "Hello World"
    assert emails[0].sender == "sender@test.com"
    assert "Test body content" in emails[0].body_text


def test_fetch_multiple_emails(greenmail_container):
    send_test_email(greenmail_container, subject="Email 1", body="Body 1")
    send_test_email(greenmail_container, subject="Email 2", body="Body 2")
    send_test_email(greenmail_container, subject="Email 3", body="Body 3")

    imap_port = greenmail_container.get_exposed_port(3143)

    reader = EmailReader(
        host="localhost",
        port=imap_port,
        username="test@test.com",
        password="test",
        use_ssl=False
    )

    emails = reader.fetch_emails()

    assert len(emails) == 3
    subjects = [email.subject for email in emails]
    assert "Email 1" in subjects
    assert "Email 2" in subjects
    assert "Email 3" in subjects


def test_fetch_emails_with_limit(greenmail_container):
    send_test_email(greenmail_container, subject="Email 1")
    send_test_email(greenmail_container, subject="Email 2")
    send_test_email(greenmail_container, subject="Email 3")

    imap_port = greenmail_container.get_exposed_port(3143)

    reader = EmailReader(
        host="localhost",
        port=imap_port,
        username="test@test.com",
        password="test",
        use_ssl=False
    )

    emails = reader.fetch_emails(limit=2)

    assert len(emails) == 2


def test_email_with_attachment(greenmail_container):
    send_test_email_with_attachment(greenmail_container)

    imap_port = greenmail_container.get_exposed_port(3143)

    reader = EmailReader(
        host="localhost",
        port=imap_port,
        username="test@test.com",
        password="test",
        use_ssl=False
    )

    emails = reader.fetch_emails()

    assert len(emails) == 1
    assert emails[0].subject == "Email with Attachment"
    assert len(emails[0].attachments) == 1
    assert "test.txt" in emails[0].attachments


def test_download_attachments(greenmail_container, tmp_path):
    send_test_email_with_attachment(greenmail_container)

    imap_port = greenmail_container.get_exposed_port(3143)

    reader = EmailReader(
        host="localhost",
        port=imap_port,
        username="test@test.com",
        password="test",
        use_ssl=False
    )

    saved_files = reader.download_attachments(save_dir=str(tmp_path))

    assert len(saved_files) == 1
    assert saved_files[0].name == "test.txt"
    assert saved_files[0].read_bytes() == b"Test file content"
