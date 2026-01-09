from abc import ABC, abstractmethod
from typing import Optional
from email_reader import EmailData


class EmailRepository(ABC):
    @abstractmethod
    def get_first_email(self, folder: str) -> Optional[EmailData]:
        pass
