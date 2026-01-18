from inbox_zero.shared.email_reader import ImapConfig
from inbox_zero.list_imap_accounts.port import ImapAccountReaderPort


class ImapAccountReaderInMemory(ImapAccountReaderPort):
    def __init__(self, accounts: list[ImapConfig]) -> None:
        self._accounts = accounts

    def get_all(self) -> list[ImapConfig]:
        return self._accounts.copy()
