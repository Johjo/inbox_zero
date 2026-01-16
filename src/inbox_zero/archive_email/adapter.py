from inbox_zero.shared.email_reader import EmailReader, EmailUid
from inbox_zero.archive_email.port import EmailArchiverPort


class EmailArchiverImap(EmailArchiverPort):
    def __init__(self, host: str, port: int, username: str, password: str, use_ssl: bool = True):
        self.email_reader = EmailReader(host, port, username, password, use_ssl)

    def archive_email(self, folder: str, uid: EmailUid) -> bool:
        return self.email_reader.archive_email(folder=folder, uid=uid)
