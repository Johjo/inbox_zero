from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Any
from imap_tools import MailBox, BaseMailBox, MailMessage  # type: ignore[attr-defined]
import imaplib


@dataclass(frozen=True)
class EmailUid:
    value: str


@dataclass
class EmailData:
    uid: EmailUid
    subject: str
    sender: str
    date: str
    body_text: str
    body_html: str
    attachments: List[str]


class MailBoxNoSSL(BaseMailBox):
    def __init__(self, host: str = 'localhost', port: int = 143) -> None:
        self._host = host
        self._port = port
        self._timeout: float | None = None
        super().__init__()  # type: ignore[no-untyped-call]

    def _get_mailbox_client(self) -> imaplib.IMAP4:
        return imaplib.IMAP4(self._host, self._port, timeout=self._timeout)


class EmailReader:
    def __init__(self, host: str, port: int, username: str, password: str, use_ssl: bool = True):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.use_ssl = use_ssl

    def _get_mailbox(self) -> Any:
        if self.use_ssl:
            return MailBox(self.host, port=self.port)  # type: ignore[no-untyped-call]
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

    def _parse_message(self, msg: Any) -> EmailData:
        attachment_names = [att.filename for att in msg.attachments]

        assert msg.uid is not None, "Email message must have a UID"

        return EmailData(
            uid=EmailUid(msg.uid),
            subject=msg.subject,
            sender=msg.from_,
            date=msg.date.isoformat() if msg.date else "",
            body_text=msg.text or "",
            body_html=msg.html or "",
            attachments=attachment_names,
        )

    def archive_first_email(self, folder: str = "INBOX", archive_folder: str = "Archive") -> bool:
        with self._get_mailbox().login(self.username, self.password, initial_folder=folder) as mailbox:
            messages = list(mailbox.fetch(limit=1, reverse=False))

            if not messages:
                return False

            msg = messages[0]
            mailbox.move(msg.uid, archive_folder)
            return True

    def archive_email(self, folder: str = "INBOX", uid: EmailUid = EmailUid(""), archive_folder: str = "Archive") -> bool:
        with self._get_mailbox().login(self.username, self.password, initial_folder=folder) as mailbox:
            mailbox.move(uid.value, archive_folder)
            return True

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
