from typing import Optional
from inbox_zero.shared.email_reader import EmailData, ImapConfig
from inbox_zero.read_first_email.port import EmailReaderPort, EMAIL_READER_PORT_KEY
from pyqure import pyqure, PyqureMemory


class ReadFirstEmailUseCase:
    email_reader: EmailReaderPort

    def __init__(self, dependencies: PyqureMemory) -> None:
        (provide, inject) = pyqure(dependencies)
        self.email_reader = inject(EMAIL_READER_PORT_KEY)

    def execute(self, config: ImapConfig, folder: str = "INBOX") -> Optional[EmailData]:
        return self.email_reader.get_first_email(config, folder)
