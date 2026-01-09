from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
from imap_tools import MailBox, BaseMailBox, MailMessage
import imaplib


@dataclass
class EmailData:
    subject: str
    sender: str
    date: str
    body_text: str
    body_html: str
    attachments: List[str]


class MailBoxNoSSL(BaseMailBox):
    def __init__(self, host: str = 'localhost', port: int = 143):
        self._host = host
        self._port = port
        self._timeout = None
        super().__init__()

    def _get_mailbox_client(self) -> imaplib.IMAP4:
        return imaplib.IMAP4(self._host, self._port, timeout=self._timeout)


class EmailReader:
    def __init__(self, host: str, port: int, username: str, password: str, use_ssl: bool = True):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.use_ssl = use_ssl

    def _get_mailbox(self):
        if self.use_ssl:
            return MailBox(self.host, port=self.port)
        else:
            return MailBoxNoSSL(self.host, port=self.port)

    def fetch_emails(self, folder: str = "INBOX", limit: Optional[int] = None) -> List[EmailData]:
        emails = []

        with self._get_mailbox().login(self.username, self.password, initial_folder=folder) as mailbox:
            messages = mailbox.fetch(limit=limit, reverse=False)

            for msg in messages:
                email_data = self._parse_message(msg)
                emails.append(email_data)

        return emails

    def _parse_message(self, msg: MailMessage) -> EmailData:
        attachment_names = [att.filename for att in msg.attachments]

        return EmailData(
            subject=msg.subject,
            sender=msg.from_,
            date=msg.date.isoformat() if msg.date else "",
            body_text=msg.text or "",
            body_html=msg.html or "",
            attachments=attachment_names,
        )

    def download_attachments(self, folder: str = "INBOX", save_dir: str = "./attachments") -> List[Path]:
        saved_files = []
        save_path = Path(save_dir)
        save_path.mkdir(parents=True, exist_ok=True)

        with self._get_mailbox().login(self.username, self.password, initial_folder=folder) as mailbox:
            for msg in mailbox.fetch():
                for att in msg.attachments:
                    file_path = save_path / att.filename
                    with open(file_path, "wb") as f:
                        f.write(att.payload)
                    saved_files.append(file_path)

        return saved_files
