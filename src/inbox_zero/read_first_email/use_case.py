from typing import Optional
from inbox_zero.shared.email_reader import EmailData
from inbox_zero.read_first_email.port import EMAIL_READER_PORT_KEY
from pyqure import pyqure, PyqureMemory


class ReadFirstEmailUseCase:
    def __init__(self, dependencies: PyqureMemory):
        (provide, inject) = pyqure(dependencies)
        self.email_reader = inject(EMAIL_READER_PORT_KEY)

    def execute(self, folder: str = "INBOX") -> Optional[EmailData]:
        return self.email_reader.get_first_email(folder)
