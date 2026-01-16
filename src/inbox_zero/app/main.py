import streamlit as st
from pyqure import pyqure, PyqureMemory

from inbox_zero.shared.email_reader import EmailData, ImapConfig
from inbox_zero.read_first_email.port import EMAIL_READER_PORT_KEY
from inbox_zero.read_first_email.adapter import EmailReaderImap
from inbox_zero.archive_email.port import EMAIL_ARCHIVER_PORT_KEY
from inbox_zero.archive_email.adapter import EmailArchiverImap
from inbox_zero.read_first_email.use_case import ReadFirstEmailUseCase
from inbox_zero.archive_email.use_case import ArchiveEmailUseCase


def create_dependencies() -> PyqureMemory:
    memory: PyqureMemory = {}
    (provide, _) = pyqure(memory)

    provide(EMAIL_READER_PORT_KEY, EmailReaderImap())
    provide(EMAIL_ARCHIVER_PORT_KEY, EmailArchiverImap())

    return memory


def display_email(email: EmailData) -> None:
    st.subheader(email.subject)
    st.text(f"De: {email.sender}")
    st.text(f"Date: {email.date}")
    st.divider()
    st.markdown(email.body_text if email.body_text else email.body_html)

    if email.attachments:
        st.text(f"Pièces jointes: {', '.join(email.attachments)}")


def main() -> None:
    st.title("Inbox Zero")

    with st.sidebar:
        st.header("Configuration IMAP")
        host = st.text_input("Serveur IMAP", value="imap.gmail.com")
        port = st.number_input("Port", value=993, min_value=1, max_value=65535)
        username = st.text_input("Email")
        password = st.text_input("Mot de passe", type="password")
        use_ssl = st.checkbox("Utiliser SSL", value=True)
        folder = st.text_input("Dossier", value="INBOX")

    if not username or not password:
        st.info("Veuillez configurer vos identifiants IMAP dans la barre latérale.")
        return

    config = ImapConfig(
        host=str(host),
        port=int(port),
        username=str(username),
        password=str(password),
        use_ssl=bool(use_ssl)
    )

    try:
        dependencies = create_dependencies()
        read_use_case = ReadFirstEmailUseCase(dependencies)
        archive_use_case = ArchiveEmailUseCase(dependencies)

        email = read_use_case.execute(config, str(folder))

        if email is None:
            st.success("Inbox Zero atteint ! Aucun email à traiter.")
        else:
            display_email(email)

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Archiver", type="primary"):
                    archive_use_case.execute(config, str(folder), email.uid)
                    st.rerun()
            with col2:
                if st.button("Rafraîchir"):
                    st.rerun()

    except Exception as e:
        st.error(f"Erreur de connexion: {e}")


if __name__ == "__main__":
    main()
