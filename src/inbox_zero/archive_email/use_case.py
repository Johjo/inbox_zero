from inbox_zero.archive_email.port import EMAIL_ARCHIVER_PORT_KEY
from inbox_zero.shared.email_reader import EmailUid
from pyqure import pyqure, PyqureMemory


class ArchiveEmailUseCase:
    def __init__(self, dependencies: PyqureMemory):
        (provide, inject) = pyqure(dependencies)
        self.email_archiver = inject(EMAIL_ARCHIVER_PORT_KEY)

    def execute(self, folder: str, uid: EmailUid) -> bool:
        return self.email_archiver.archive_email(folder, uid)
