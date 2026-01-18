import pytest
from pyqure import pyqure, PyqureMemory

from inbox_zero.shared.email_reader import ImapConfig
from inbox_zero.create_imap_account.port import (
    ImapAccountRepositoryPort,
    IMAP_ACCOUNT_REPOSITORY_PORT_KEY,
)
from inbox_zero.create_imap_account.use_case import CreateImapAccountUseCase


class ImapAccountRepositoryForTest(ImapAccountRepositoryPort):
    def __init__(self) -> None:
        self._accounts: list[ImapConfig] = []

    def save(self, config: ImapConfig) -> None:
        self._accounts.append(config)

    def get_all(self) -> list[ImapConfig]:
        return self._accounts.copy()


@pytest.fixture
def dependencies() -> PyqureMemory:
    memory: PyqureMemory = {}
    return memory


@pytest.fixture
def repository(dependencies: PyqureMemory) -> ImapAccountRepositoryForTest:
    (provide, inject) = pyqure(dependencies)
    repo = ImapAccountRepositoryForTest()
    provide(IMAP_ACCOUNT_REPOSITORY_PORT_KEY, repo)
    return repo


def test_create_imap_account(
    dependencies: PyqureMemory, repository: ImapAccountRepositoryForTest
) -> None:
    config = ImapConfig(
        host="imap.gmail.com",
        port=993,
        username="user@gmail.com",
        password="password123",
        use_ssl=True,
    )

    sut = CreateImapAccountUseCase(dependencies)

    sut.execute(config)

    accounts = repository.get_all()
    assert len(accounts) == 1
    assert accounts[0].host == "imap.gmail.com"
    assert accounts[0].port == 993
    assert accounts[0].username == "user@gmail.com"
    assert accounts[0].password == "password123"
    assert accounts[0].use_ssl is True


def test_create_multiple_imap_accounts(
    dependencies: PyqureMemory, repository: ImapAccountRepositoryForTest
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

    sut = CreateImapAccountUseCase(dependencies)

    sut.execute(config1)
    sut.execute(config2)

    accounts = repository.get_all()
    assert len(accounts) == 2
    assert accounts[0].username == "user1@gmail.com"
    assert accounts[1].username == "user2@outlook.com"
