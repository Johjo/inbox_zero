from typing import Optional
from inbox_zero.shared.email_reader import EmailReader, EmailData, ImapConfig
from inbox_zero.read_first_email.port import EmailReaderPort


class EmailReaderImap(EmailReaderPort):
    def get_first_email(self, config: ImapConfig) -> Optional[EmailData]:
        email_reader = EmailReader(
            config.host, config.port, config.username, config.password, config.use_ssl
        )
        emails = email_reader.fetch_emails(folder=config.folder, limit=1)
        if len(emails) == 0:
            return None
        return emails[0]
