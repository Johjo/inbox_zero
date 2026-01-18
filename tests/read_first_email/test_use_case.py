from typing import Optional, Dict, List
import pytest
from pyqure import pyqure, PyqureMemory

from inbox_zero.shared.email_reader import EmailData, EmailUid, ImapConfig
from inbox_zero.read_first_email.port import EmailReaderPort, EMAIL_READER_PORT_KEY
from inbox_zero.read_first_email.use_case import ReadFirstEmailUseCase


class EmailReaderForTest(EmailReaderPort):
    def __init__(self) -> None:
        self._emails: Dict[str, List[EmailData]] = {}

    def add_email(self, folder: str, email: EmailData) -> None:
        if folder not in self._emails:
            self._emails[folder] = []
        self._emails[folder].append(email)

    def get_first_email(self, config: ImapConfig) -> Optional[EmailData]:
        folder = config.folder
        if folder not in self._emails or len(self._emails[folder]) == 0:
            return None
        return self._emails[folder][0]


@pytest.fixture
def dependencies() -> PyqureMemory:
    memory: PyqureMemory = {}
    return memory


@pytest.fixture
def email_reader(dependencies: PyqureMemory) -> EmailReaderForTest:
    (provide, inject) = pyqure(dependencies)
    reader = EmailReaderForTest()
    provide(EMAIL_READER_PORT_KEY, reader)
    return reader


@pytest.fixture
def config() -> ImapConfig:
    return ImapConfig(
        host="localhost",
        port=993,
        username="test@test.com",
        password="password",
        use_ssl=True,
        folder="INBOX"
    )


def test_read_first_email_from_inbox(
    dependencies: PyqureMemory, email_reader: EmailReaderForTest, config: ImapConfig
) -> None:
    email = EmailData(
        uid=EmailUid("1"),
        subject="Test Subject",
        sender="sender@test.com",
        date="2024-01-09T10:00:00",
        body_text="Test body",
        body_html="<p>Test body</p>",
        attachments=[]
    )
    email_reader.add_email("INBOX", email)

    sut = ReadFirstEmailUseCase(dependencies)

    result = sut.execute(config)

    assert result is not None
    assert result.subject == "Test Subject"
    assert result.sender == "sender@test.com"
    assert result.body_text == "Test body"


def test_read_first_email_when_inbox_is_empty(
    dependencies: PyqureMemory, email_reader: EmailReaderForTest, config: ImapConfig
) -> None:
    sut = ReadFirstEmailUseCase(dependencies)

    result = sut.execute(config)

    assert result is None


def test_read_first_email_when_multiple_emails(
    dependencies: PyqureMemory, email_reader: EmailReaderForTest, config: ImapConfig
) -> None:
    first_email = EmailData(
        uid=EmailUid("1"),
        subject="First Email",
        sender="sender1@test.com",
        date="2024-01-09T10:00:00",
        body_text="First",
        body_html="<p>First</p>",
        attachments=[]
    )
    second_email = EmailData(
        uid=EmailUid("2"),
        subject="Second Email",
        sender="sender2@test.com",
        date="2024-01-09T11:00:00",
        body_text="Second",
        body_html="<p>Second</p>",
        attachments=[]
    )

    email_reader.add_email("INBOX", first_email)
    email_reader.add_email("INBOX", second_email)

    sut = ReadFirstEmailUseCase(dependencies)

    result = sut.execute(config)

    assert result is not None
    assert result.subject == "First Email"
    assert result.sender == "sender1@test.com"


def test_read_first_email_from_different_folder(
    dependencies: PyqureMemory, email_reader: EmailReaderForTest
) -> None:
    config = ImapConfig(
        host="localhost",
        port=993,
        username="test@test.com",
        password="password",
        use_ssl=True,
        folder="SENT"
    )
    email = EmailData(
        uid=EmailUid("1"),
        subject="Sent Email",
        sender="me@test.com",
        date="2024-01-09T10:00:00",
        body_text="Sent body",
        body_html="<p>Sent body</p>",
        attachments=[]
    )
    email_reader.add_email("SENT", email)

    sut = ReadFirstEmailUseCase(dependencies)

    result = sut.execute(config)

    assert result is not None
    assert result.subject == "Sent Email"
