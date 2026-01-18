from inbox_zero.shared.email_reader import ImapConfig
from inbox_zero.list_imap_accounts.adapter import ImapAccountReaderInMemory


def test_get_all_when_empty() -> None:
    sut = ImapAccountReaderInMemory(accounts=[])

    result = sut.get_all()

    assert result == []


def test_get_all_with_one_account() -> None:
    config = ImapConfig(
        host="imap.gmail.com",
        port=993,
        username="user@gmail.com",
        password="password123",
        use_ssl=True,
    )
    sut = ImapAccountReaderInMemory(accounts=[config])

    result = sut.get_all()

    assert len(result) == 1
    assert result[0].host == "imap.gmail.com"
    assert result[0].username == "user@gmail.com"


def test_get_all_with_multiple_accounts() -> None:
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
    sut = ImapAccountReaderInMemory(accounts=[config1, config2])

    result = sut.get_all()

    assert len(result) == 2
    assert result[0].username == "user1@gmail.com"
    assert result[1].username == "user2@outlook.com"


def test_get_all_returns_copy() -> None:
    config = ImapConfig(
        host="imap.gmail.com",
        port=993,
        username="user@gmail.com",
        password="password123",
        use_ssl=True,
    )
    sut = ImapAccountReaderInMemory(accounts=[config])

    result = sut.get_all()
    result.clear()

    assert len(sut.get_all()) == 1
