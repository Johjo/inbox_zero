from typing import Optional
from inbox_zero.email_reader import EmailData
from inbox_zero.ports.email_repository import EMAIL_REPOSITORY_KEY
from pyqure import pyqure, PyqureMemory


class ReadFirstEmailUseCase:
    def __init__(self, dependencies: PyqureMemory):
        (provide, inject) = pyqure(dependencies)
        self.email_repository = inject(EMAIL_REPOSITORY_KEY)

    def execute(self, folder: str = "INBOX") -> Optional[EmailData]:
        return self.email_repository.get_first_email(folder)
