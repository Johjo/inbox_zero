from inbox_zero.shared.email_reader import ImapConfig
from inbox_zero.create_imap_account.port import (
    ImapAccountRepositoryPort,
    IMAP_ACCOUNT_REPOSITORY_PORT_KEY,
)
from pyqure import pyqure, PyqureMemory


class CreateImapAccountUseCase:
    repository: ImapAccountRepositoryPort

    def __init__(self, dependencies: PyqureMemory) -> None:
        (provide, inject) = pyqure(dependencies)
        self.repository = inject(IMAP_ACCOUNT_REPOSITORY_PORT_KEY)

    def execute(self, config: ImapConfig) -> None:
        self.repository.save(config)
