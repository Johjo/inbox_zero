from abc import ABC, abstractmethod
from typing import Optional
from inbox_zero.shared.email_reader import EmailData, ImapConfig
from pyqure import Key


class EmailReaderPort(ABC):
    @abstractmethod
    def get_first_email(self, config: ImapConfig) -> Optional[EmailData]:
        pass


EMAIL_READER_PORT_KEY: Key[EmailReaderPort] = Key("email_reader_port", EmailReaderPort)
