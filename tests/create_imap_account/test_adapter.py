from inbox_zero.shared.email_reader import ImapConfig
from inbox_zero.create_imap_account.adapter import ImapAccountRepositoryInMemory


def test_save_one_account() -> None:
    config = ImapConfig(
        host="imap.gmail.com",
        port=993,
        username="user@gmail.com",
        password="password123",
        use_ssl=True,
    )
    sut = ImapAccountRepositoryInMemory()

    sut.save(config)

    accounts = sut.get_all()
    assert len(accounts) == 1
    assert accounts[0].host == "imap.gmail.com"
    assert accounts[0].username == "user@gmail.com"


def test_save_multiple_accounts() -> None:
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
    sut = ImapAccountRepositoryInMemory()

    sut.save(config1)
    sut.save(config2)

    accounts = sut.get_all()
    assert len(accounts) == 2
    assert accounts[0].username == "user1@gmail.com"
    assert accounts[1].username == "user2@outlook.com"


def test_get_all_returns_copy() -> None:
    config = ImapConfig(
        host="imap.gmail.com",
        port=993,
        username="user@gmail.com",
        password="password123",
        use_ssl=True,
    )
    sut = ImapAccountRepositoryInMemory()
    sut.save(config)

    result = sut.get_all()
    result.clear()

    assert len(sut.get_all()) == 1


def test_get_all_when_empty() -> None:
    sut = ImapAccountRepositoryInMemory()

    result = sut.get_all()

    assert result == []
