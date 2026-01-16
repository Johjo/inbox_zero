from inbox_zero.archive_email.port import EmailArchiverPort, EMAIL_ARCHIVER_PORT_KEY
from inbox_zero.shared.email_reader import EmailUid, ImapConfig
from pyqure import pyqure, PyqureMemory


class ArchiveEmailUseCase:
    email_archiver: EmailArchiverPort

    def __init__(self, dependencies: PyqureMemory) -> None:
        (provide, inject) = pyqure(dependencies)
        self.email_archiver = inject(EMAIL_ARCHIVER_PORT_KEY)

    def execute(self, config: ImapConfig, folder: str, uid: EmailUid) -> bool:
        return self.email_archiver.archive_email(config, folder, uid)
