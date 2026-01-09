from typing import Optional
from email_reader import EmailReader, EmailData
from ports.email_repository import EmailRepository


class EmailRepositoryImap(EmailRepository):
    def __init__(self, host: str, port: int, username: str, password: str, use_ssl: bool = True):
        self.email_reader = EmailReader(host, port, username, password, use_ssl)

    def get_first_email(self, folder: str) -> Optional[EmailData]:
        emails = self.email_reader.fetch_emails(folder=folder, limit=1)
        if len(emails) == 0:
            return None
        return emails[0]

    def archive_first_email(self, folder: str) -> bool:
        return self.email_reader.archive_first_email(folder=folder)
