import pytest
from pyqure import pyqure, PyqureMemory

from inbox_zero.shared.email_reader import ImapConfig
from inbox_zero.list_imap_accounts.port import (
    ImapAccountReaderPort,
    IMAP_ACCOUNT_READER_PORT_KEY,
)
from inbox_zero.list_imap_accounts.use_case import ListImapAccountsUseCase


class ImapAccountReaderForTest(ImapAccountReaderPort):
    def __init__(self) -> None:
        self._accounts: list[ImapConfig] = []

    def add_account(self, config: ImapConfig) -> None:
        self._accounts.append(config)

    def get_all(self) -> list[ImapConfig]:
        return self._accounts.copy()


@pytest.fixture
def dependencies() -> PyqureMemory:
    memory: PyqureMemory = {}
    return memory


@pytest.fixture
def reader(dependencies: PyqureMemory) -> ImapAccountReaderForTest:
    (provide, inject) = pyqure(dependencies)
    reader = ImapAccountReaderForTest()
    provide(IMAP_ACCOUNT_READER_PORT_KEY, reader)
    return reader


def test_list_imap_accounts_when_empty(
    dependencies: PyqureMemory, reader: ImapAccountReaderForTest
) -> None:
    sut = ListImapAccountsUseCase(dependencies)

    result = sut.execute()

    assert result == []


def test_list_imap_accounts_with_one_account(
    dependencies: PyqureMemory, reader: ImapAccountReaderForTest
) -> None:
    config = ImapConfig(
        host="imap.gmail.com",
        port=993,
        username="user@gmail.com",
        password="password123",
        use_ssl=True,
    )
    reader.add_account(config)

    sut = ListImapAccountsUseCase(dependencies)

    result = sut.execute()

    assert len(result) == 1
    assert result[0].host == "imap.gmail.com"
    assert result[0].username == "user@gmail.com"


def test_list_imap_accounts_with_multiple_accounts(
    dependencies: PyqureMemory, reader: ImapAccountReaderForTest
) -> None:
    config1 = ImapConfig(
        host="imap.gmail.com",
        port=993,
        username="user1@gmail.com",
        password="password1",
        use_ssl=True,
    )
    config2 = ImapConfig(
        host="imap.outlook.com",
        port=993,
        username="user2@outlook.com",
        password="password2",
        use_ssl=True,
    )
    reader.add_account(config1)
    reader.add_account(config2)

    sut = ListImapAccountsUseCase(dependencies)

    result = sut.execute()

    assert len(result) == 2
    assert result[0].username == "user1@gmail.com"
    assert result[1].username == "user2@outlook.com"
