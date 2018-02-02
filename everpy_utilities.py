"""Some generic utilties."""
import keyring
import getpass
import re

UN = "everpy"


def refresh_token():
    """Set new token."""
    print("Set a new a token")
    keyring.set_password(UN, UN, getpass.getpass("Password: "))
    return keyring.get_password(UN, UN)


def get_token():
    """Get a token."""
    dev_token = keyring.get_password(UN, UN)
    if not dev_token:
        dev_token = refresh_token()
    return dev_token


def get_template_tokens(content):
    regex = r"\$\{(\d+.*?)\}"
    tokens = {}
    with open("Templates/simple_sections.txt", "r") as f:
        content = f.read()
        matches = re.finditer(regex, content)
        for match_num, match in enumerate(matches):
            match_num = match_num + 1
            tok = match.group(1)
            tok_id, tok_name = None, None
            if len(tok.split(":")) == 2:
                tok_id, tok_name = tok.split(":")
            else:
                tok_id, tok_name = tok, None
            tokens[tok_id] = {"name": tok_name, "val": None}
    return tokens

if __name__ == '__main__':

    # Test methods
    token = get_token()
    print(token)