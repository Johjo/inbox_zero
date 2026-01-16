from inbox_zero.shared.email_reader import EmailReader, EmailUid, ImapConfig
from inbox_zero.archive_email.port import EmailArchiverPort


class EmailArchiverImap(EmailArchiverPort):
    def archive_email(self, config: ImapConfig, folder: str, uid: EmailUid) -> bool:
        email_reader = EmailReader(
            config.host, config.port, config.username, config.password, config.use_ssl
        )
        return email_reader.archive_email(folder=folder, uid=uid)
