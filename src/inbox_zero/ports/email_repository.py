from abc import ABC, abstractmethod
from typing import Optional
from inbox_zero.email_reader import EmailData, EmailUid
from pyqure import Key


class EmailRepository(ABC):
    @abstractmethod
    def get_first_email(self, folder: str) -> Optional[EmailData]:
        pass

    @abstractmethod
    def archive_first_email(self, folder: str, uid: EmailUid) -> bool:
        pass


EMAIL_REPOSITORY_KEY: Key[EmailRepository] = Key("email_repository", EmailRepository)
