from inbox_zero.shared.email_reader import ImapConfig
from inbox_zero.list_imap_accounts.port import (
    ImapAccountReaderPort,
    IMAP_ACCOUNT_READER_PORT_KEY,
)
from pyqure import pyqure, PyqureMemory


class ListImapAccountsUseCase:
    reader: ImapAccountReaderPort

    def __init__(self, dependencies: PyqureMemory) -> None:
        (provide, inject) = pyqure(dependencies)
        self.reader = inject(IMAP_ACCOUNT_READER_PORT_KEY)

    def execute(self) -> list[ImapConfig]:
        return self.reader.get_all()
