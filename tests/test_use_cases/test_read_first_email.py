from typing import Optional, Dict, List
import pytest
from pyqure import Key, pyqure, PyqureMemory

from email_reader import EmailData, EmailUid
from ports.email_repository import EmailRepository, EMAIL_REPOSITORY_KEY
from use_cases.read_first_email import ReadFirstEmailUseCase


class EmailRepositoryForTest(EmailRepository):
    def __init__(self):
        self._emails: Dict[str, List[EmailData]] = {}

    def add_email(self, folder: str, email: EmailData) -> None:
        if folder not in self._emails:
            self._emails[folder] = []
        self._emails[folder].append(email)

    def get_first_email(self, folder: str) -> Optional[EmailData]:
        if folder not in self._emails or len(self._emails[folder]) == 0:
            return None
        return self._emails[folder][0]

    def archive_first_email(self, folder: str) -> bool:
        if folder not in self._emails or len(self._emails[folder]) == 0:
            return False

        email = self._emails[folder].pop(0)

        if "Archive" not in self._emails:
            self._emails["Archive"] = []
        self._emails["Archive"].append(email)

        return True


@pytest.fixture
def dependencies():
    memory: PyqureMemory = {}
    return memory


@pytest.fixture
def repository(dependencies):
    (provide, inject) = pyqure(dependencies)
    repo = EmailRepositoryForTest()
    provide(EMAIL_REPOSITORY_KEY, repo)
    return repo


def test_read_first_email_from_inbox(dependencies, repository):
    email = EmailData(
        uid=EmailUid("1"),
        subject="Test Subject",
        sender="sender@test.com",
        date="2024-01-09T10:00:00",
        body_text="Test body",
        body_html="<p>Test body</p>",
        attachments=[]
    )
    repository.add_email("INBOX", email)

    sut = ReadFirstEmailUseCase(dependencies)

    result = sut.execute("INBOX")

    assert result is not None
    assert result.subject == "Test Subject"
    assert result.sender == "sender@test.com"
    assert result.body_text == "Test body"


def test_read_first_email_when_inbox_is_empty(dependencies, repository):
    sut = ReadFirstEmailUseCase(dependencies)

    result = sut.execute("INBOX")

    assert result is None


def test_read_first_email_when_multiple_emails(dependencies, repository):
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

    repository.add_email("INBOX", first_email)
    repository.add_email("INBOX", second_email)

    sut = ReadFirstEmailUseCase(dependencies)

    result = sut.execute("INBOX")

    assert result is not None
    assert result.subject == "First Email"
    assert result.sender == "sender1@test.com"


def test_read_first_email_from_different_folder(dependencies, repository):
    email = EmailData(
        uid=EmailUid("1"),
        subject="Sent Email",
        sender="me@test.com",
        date="2024-01-09T10:00:00",
        body_text="Sent body",
        body_html="<p>Sent body</p>",
        attachments=[]
    )
    repository.add_email("SENT", email)

    sut = ReadFirstEmailUseCase(dependencies)

    result = sut.execute("SENT")

    assert result is not None
    assert result.subject == "Sent Email"
