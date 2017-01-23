"""Some examples of how to use modules."""

# from everpy_extras import EverPyExtras
from everpy_pro import EverPyPro
import everpy_utilities

PATH_TO_ENSCRIPT = "C:\Program Files (x86)\Evernote\Evernote\ENScript.exe"


def createnote(epy):
    """Example of how to make a note from python."""
    content = open("README.md", "r").read()
    notebook = "_INBOX"
    title = "Everpy Generated Note"
    tags = ["everpy"]
    attachments = ["README.md"]
    epy.create_note_from_content(content, notebook_name=notebook, title=title, tags=tags, file_attachments=attachments)


def main():
    """Example usages."""
    dev_token = everpy_utilities.get_token()
    try:
        my_evernote = EverPyPro(dev_token, PATH_TO_ENSCRIPT)
    except:
        everpy_utilities.refresh_token()
        my_evernote = EverPyPro(dev_token, PATH_TO_ENSCRIPT)

    # Find and replace
    # my_evernote.find_and_replace("evernote", "Evernote", "any:")

    # Creating a note.
    # createnote(my_evernote)

    # Opening client with specific search attributes
    # my_evernote.get_notes_to_manage()
    # or
    # my_evernote.search_notes("stack:Work intitle:\"new employee\"")

    # Creating a note from an hmtl template
    # my_evernote.create_note(open("template.html", "r").read(), title="Template", notebook="_INBOX", tags=["everpy"], attachments=["template.html"])

    ##############################
    # VVVV Tests may not work VVVV.
    my_evernote.simple_template2()
    # my_evernote.create_textnote_from_file("template.html", notebook_name="_INBOX")
    # my_evernote.learn_notebooks()
    # print(my_evernote.note_book_dict)
if __name__ == '__main__':
    main()
