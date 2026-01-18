from abc import ABC, abstractmethod
from inbox_zero.shared.email_reader import ImapConfig
from pyqure import Key


class ImapAccountReaderPort(ABC):
    @abstractmethod
    def get_all(self) -> list[ImapConfig]:
        pass


IMAP_ACCOUNT_READER_PORT_KEY: Key[ImapAccountReaderPort] = Key(
    "imap_account_reader_port", ImapAccountReaderPort
)
