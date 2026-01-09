from abc import ABC, abstractmethod
from typing import Optional
from email_reader import EmailData
from pyqure import Key


class EmailRepository(ABC):
    @abstractmethod
    def get_first_email(self, folder: str) -> Optional[EmailData]:
        pass


EMAIL_REPOSITORY_KEY: Key[EmailRepository] = Key("email_repository", EmailRepository)
