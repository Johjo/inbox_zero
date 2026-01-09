from typing import Optional
from email_reader import EmailData
from ports.email_repository import EmailRepository


class ReadFirstEmailUseCase:
    def __init__(self, email_repository: EmailRepository):
        self.email_repository = email_repository

    def execute(self, folder: str = "INBOX") -> Optional[EmailData]:
        return self.email_repository.get_first_email(folder)
