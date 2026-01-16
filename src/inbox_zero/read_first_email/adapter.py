from typing import Optional
from inbox_zero.shared.email_reader import EmailReader, EmailData
from inbox_zero.read_first_email.port import EmailReaderPort


class EmailReaderImap(EmailReaderPort):
    def __init__(self, host: str, port: int, username: str, password: str, use_ssl: bool = True):
        self.email_reader = EmailReader(host, port, username, password, use_ssl)

    def get_first_email(self, folder: str) -> Optional[EmailData]:
        emails = self.email_reader.fetch_emails(folder=folder, limit=1)
        if len(emails) == 0:
            return None
        return emails[0]
