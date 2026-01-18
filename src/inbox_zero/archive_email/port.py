from abc import ABC, abstractmethod
from inbox_zero.shared.email_reader import EmailUid, ImapConfig
from pyqure import Key


class EmailArchiverPort(ABC):
    @abstractmethod
    def archive_email(self, config: ImapConfig, uid: EmailUid) -> bool:
        pass


EMAIL_ARCHIVER_PORT_KEY: Key[EmailArchiverPort] = Key("email_archiver_port", EmailArchiverPort)
