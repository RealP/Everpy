"""Some generic utilties."""
import keyring
import getpass

UN = "everpy"


def refresh_token():
    """Set new token."""
    keyring.set_password(UN, UN, getpass.getpass("Password: "))
    return keyring.get_password(UN, UN)


def get_token():
    """Get a token."""
    dev_token = keyring.get_password(UN, UN)
    if not dev_token:
        dev_token = refresh_token()
    return dev_token
