import streamlit as st
from pyqure import pyqure, PyqureMemory

from inbox_zero.shared.email_reader import EmailData, ImapConfig
from inbox_zero.read_first_email.port import EMAIL_READER_PORT_KEY
from inbox_zero.read_first_email.adapter import EmailReaderImap
from inbox_zero.archive_email.port import EMAIL_ARCHIVER_PORT_KEY
from inbox_zero.archive_email.adapter import EmailArchiverImap
from inbox_zero.read_first_email.use_case import ReadFirstEmailUseCase
from inbox_zero.archive_email.use_case import ArchiveEmailUseCase
from inbox_zero.create_imap_account.port import IMAP_ACCOUNT_REPOSITORY_PORT_KEY
from inbox_zero.create_imap_account.adapter import ImapAccountRepositoryInMemory
from inbox_zero.create_imap_account.use_case import CreateImapAccountUseCase
from inbox_zero.list_imap_accounts.port import IMAP_ACCOUNT_READER_PORT_KEY
from inbox_zero.list_imap_accounts.adapter import ImapAccountReaderInMemory
from inbox_zero.list_imap_accounts.use_case import ListImapAccountsUseCase


def get_account_repository() -> ImapAccountRepositoryInMemory:
    if "account_repository" not in st.session_state:
        st.session_state.account_repository = ImapAccountRepositoryInMemory()
    return st.session_state.account_repository  # type: ignore[no-any-return]


def create_dependencies() -> PyqureMemory:
    memory: PyqureMemory = {}
    (provide, _) = pyqure(memory)

    provide(EMAIL_READER_PORT_KEY, EmailReaderImap())
    provide(EMAIL_ARCHIVER_PORT_KEY, EmailArchiverImap())

    account_repository = get_account_repository()
    provide(IMAP_ACCOUNT_REPOSITORY_PORT_KEY, account_repository)
    provide(IMAP_ACCOUNT_READER_PORT_KEY, ImapAccountReaderInMemory(account_repository.get_all()))

    return memory


def display_email(email: EmailData) -> None:
    st.subheader(email.subject)
    st.text(f"De: {email.sender}")
    st.text(f"Date: {email.date}")
    st.divider()
    st.markdown(email.body_text if email.body_text else email.body_html)

    if email.attachments:
        st.text(f"Pièces jointes: {', '.join(email.attachments)}")


def display_accounts_page(dependencies: PyqureMemory) -> None:
    st.header("Comptes IMAP")

    list_use_case = ListImapAccountsUseCase(dependencies)
    accounts = list_use_case.execute()

    if accounts:
        st.subheader("Comptes enregistrés")
        for i, account in enumerate(accounts):
            with st.container(border=True):
                st.text(f"Serveur: {account.host}:{account.port}")
                st.text(f"Email: {account.username}")
                st.text(f"SSL: {'Oui' if account.use_ssl else 'Non'}")
    else:
        st.info("Aucun compte enregistré.")

    st.divider()
    st.subheader("Ajouter un compte")

    with st.form("add_account_form"):
        host = st.text_input("Serveur IMAP", value="imap.gmail.com")
        port = st.number_input("Port", value=993, min_value=1, max_value=65535)
        username = st.text_input("Email")
        password = st.text_input("Mot de passe", type="password")
        use_ssl = st.checkbox("Utiliser SSL", value=True)

        submitted = st.form_submit_button("Ajouter le compte")

        if submitted:
            if username and password:
                config = ImapConfig(
                    host=str(host),
                    port=int(port),
                    username=str(username),
                    password=str(password),
                    use_ssl=bool(use_ssl),
                )
                create_use_case = CreateImapAccountUseCase(dependencies)
                create_use_case.execute(config)
                st.success(f"Compte {username} ajouté.")
                st.rerun()
            else:
                st.error("Veuillez remplir l'email et le mot de passe.")


def display_inbox_page(dependencies: PyqureMemory) -> None:
    st.header("Inbox")

    list_use_case = ListImapAccountsUseCase(dependencies)
    accounts = list_use_case.execute()

    if not accounts:
        st.warning("Aucun compte IMAP configuré. Ajoutez un compte dans l'onglet 'Comptes'.")
        return

    account_names = [account.username for account in accounts]
    selected_account = st.selectbox("Compte", account_names)

    if selected_account:
        config = next(acc for acc in accounts if acc.username == selected_account)
        folder = st.text_input("Dossier", value="INBOX")

        read_use_case = ReadFirstEmailUseCase(dependencies)
        archive_use_case = ArchiveEmailUseCase(dependencies)

        try:
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


def main() -> None:
    st.title("Inbox Zero")

    dependencies = create_dependencies()

    tab_inbox, tab_accounts = st.tabs(["Inbox", "Comptes"])

    with tab_inbox:
        display_inbox_page(dependencies)

    with tab_accounts:
        display_accounts_page(dependencies)


if __name__ == "__main__":
    main()
