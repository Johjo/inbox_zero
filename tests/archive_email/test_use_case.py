from typing import Dict, List
import pytest
from pyqure import pyqure, PyqureMemory

from inbox_zero.shared.email_reader import EmailData, EmailUid
from inbox_zero.archive_email.port import EmailArchiverPort, EMAIL_ARCHIVER_PORT_KEY
from inbox_zero.archive_email.use_case import ArchiveEmailUseCase


class EmailArchiverForTest(EmailArchiverPort):
    def __init__(self):
        self._emails: Dict[str, List[EmailData]] = {}
        self._archived: Dict[str, List[EmailData]] = {}

    def add_email(self, folder: str, email: EmailData) -> None:
        if folder not in self._emails:
            self._emails[folder] = []
        self._emails[folder].append(email)

    def archive_email(self, folder: str, uid: EmailUid) -> bool:
        if folder not in self._emails or len(self._emails[folder]) == 0:
            return False

        email_to_archive = None
        email_index = None
        for index, email in enumerate(self._emails[folder]):
            if email.uid == uid:
                email_to_archive = email
                email_index = index
                break

        if email_to_archive is None or email_index is None:
            return False

        self._emails[folder].pop(email_index)

        if "Archive" not in self._archived:
            self._archived["Archive"] = []
        self._archived["Archive"].append(email_to_archive)

        return True

    def get_emails_count(self, folder: str) -> int:
        if folder not in self._emails:
            return 0
        return len(self._emails[folder])

    def get_archived_count(self) -> int:
        if "Archive" not in self._archived:
            return 0
        return len(self._archived["Archive"])

    def get_first_archived(self) -> EmailData | None:
        if "Archive" not in self._archived or len(self._archived["Archive"]) == 0:
            return None
        return self._archived["Archive"][0]

    def get_first_email(self, folder: str) -> EmailData | None:
        if folder not in self._emails or len(self._emails[folder]) == 0:
            return None
        return self._emails[folder][0]


@pytest.fixture
def dependencies():
    memory: PyqureMemory = {}
    return memory


@pytest.fixture
def email_archiver(dependencies):
    (provide, inject) = pyqure(dependencies)
    archiver = EmailArchiverForTest()
    provide(EMAIL_ARCHIVER_PORT_KEY, archiver)
    return archiver


def test_archive_email_from_inbox(dependencies, email_archiver):
    email = EmailData(
        uid=EmailUid("1"),
        subject="Test Subject",
        sender="sender@test.com",
        date="2024-01-09T10:00:00",
        body_text="Test body",
        body_html="<p>Test body</p>",
        attachments=[]
    )
    email_archiver.add_email("INBOX", email)

    sut = ArchiveEmailUseCase(dependencies)

    result = sut.execute("INBOX", EmailUid("1"))

    assert result is True
    assert email_archiver.get_emails_count("INBOX") == 0
    assert email_archiver.get_archived_count() == 1
    archived_email = email_archiver.get_first_archived()
    assert archived_email is not None
    assert archived_email.subject == "Test Subject"


def test_archive_email_when_inbox_is_empty(dependencies, email_archiver):
    sut = ArchiveEmailUseCase(dependencies)

    result = sut.execute("INBOX", EmailUid("1"))

    assert result is False


def test_archive_email_when_multiple_emails(dependencies, email_archiver):
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

    email_archiver.add_email("INBOX", first_email)
    email_archiver.add_email("INBOX", second_email)

    sut = ArchiveEmailUseCase(dependencies)

    result = sut.execute("INBOX", EmailUid("1"))

    assert result is True
    assert email_archiver.get_emails_count("INBOX") == 1
    assert email_archiver.get_archived_count() == 1
    remaining_email = email_archiver.get_first_email("INBOX")
    assert remaining_email is not None
    assert remaining_email.subject == "Second Email"
    archived_email = email_archiver.get_first_archived()
    assert archived_email is not None
    assert archived_email.subject == "First Email"


def test_archive_email_from_different_folder(dependencies, email_archiver):
    email = EmailData(
        uid=EmailUid("1"),
        subject="Sent Email",
        sender="me@test.com",
        date="2024-01-09T10:00:00",
        body_text="Sent body",
        body_html="<p>Sent body</p>",
        attachments=[]
    )
    email_archiver.add_email("SENT", email)

    sut = ArchiveEmailUseCase(dependencies)

    result = sut.execute("SENT", EmailUid("1"))

    assert result is True
    assert email_archiver.get_emails_count("SENT") == 0
    assert email_archiver.get_archived_count() == 1
