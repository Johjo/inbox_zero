from abc import ABC, abstractmethod
from inbox_zero.shared.email_reader import ImapConfig
from pyqure import Key


class ImapAccountRepositoryPort(ABC):
    @abstractmethod
    def save(self, config: ImapConfig) -> None:
        pass


IMAP_ACCOUNT_REPOSITORY_PORT_KEY: Key[ImapAccountRepositoryPort] = Key(
    "imap_account_repository_port", ImapAccountRepositoryPort
)
