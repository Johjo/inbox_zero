from inbox_zero.shared.email_reader import ImapConfig
from inbox_zero.create_imap_account.port import ImapAccountRepositoryPort


class ImapAccountRepositoryInMemory(ImapAccountRepositoryPort):
    def __init__(self) -> None:
        self._accounts: list[ImapConfig] = []

    def save(self, config: ImapConfig) -> None:
        self._accounts.append(config)

    def get_all(self) -> list[ImapConfig]:
        return self._accounts.copy()
