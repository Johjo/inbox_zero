from ports.email_repository import EmailRepository, EMAIL_REPOSITORY_KEY
from pyqure import pyqure, PyqureMemory


class ArchiveFirstEmailUseCase:
    def __init__(self, dependencies: PyqureMemory):
        (provide, inject) = pyqure(dependencies)
        self.email_repository = inject(EMAIL_REPOSITORY_KEY)

    def execute(self, folder: str = "INBOX") -> bool:
        return self.email_repository.archive_first_email(folder)
