"""
The purpose of Everpy extras is to provide functionality that is a result of multiple calls to ENScript.exe.

Some ideas are:
    1. Find and replace text in notes.
    2. Tag notes based on Season. ie)winter spring summer fall
    3. Get notes to tag
    4. Automated backup
"""
import tempfile
import os
from everpy import EverPy
from datetime import datetime


def roll_files(backup_file, number_of_backups):
    """
    Rotate files.

    @param backup_file file to roll
    @param number_of_backups files to keep
    """
    path_pieces = backup_file.split(os.sep)
    file_name = path_pieces[-1]
    file_path = os.sep.join(path_pieces[:-1])
    items_in_dir = os.listdir(file_path)
    current_number_of_backups = len([i for i in items_in_dir if file_name in i])

    backup_file_base = file_path + os.sep + file_name

    if current_number_of_backups > number_of_backups:
        # Delete oldest rename all others
        os.remove(backup_file_base + "." + str(number_of_backups))

    # Roll the files
    for i in range(current_number_of_backups - 1, 0, -1):
        os.rename(backup_file_base + "." + str(i), backup_file_base + "." + str(i + 1))
    os.rename(backup_file_base, backup_file_base + ".1")


class EverPyExtras(EverPy):
    """Provide extra Evernote commands."""

    def __init__(self, path_enscript_exe, username=None, password=None):
        r"""
        Initialize EverPyExtras object.

        If both database file name and user name are not specified, last login name is used and
        if there is none, USERNAME environment variable value is used as a user name.

        @param path_enscript_exe path the Evernote ENScript.exe
                                 usually "C:\Program Files (x86)\Evernote\Evernote\ENScript.exe"
        @param username if not using the default account you'll need to provide a username
        @param password if not using the default account you'll need to provide a password
        """
        super(EverPyExtras, self).__init__(path_enscript_exe, username, password)

    @staticmethod
    def _build_query_from_items(*args):
        """
        Concatenate strings and lists containing strings into one string with spaces as separator.

        @param *args optional number of list or strings containing search queries.
        """
        query = ""
        for query_item in args:
            if isinstance(query_item, list):
                query += " ".join(query_item) + " "
            elif isinstance(query_item, str):
                query += query_item + " "
        return query

    def get_notes_to_manage(self):
        """Note(s) that need to be filtered managed etc.

        A possible enhancement to this function would be to find all
        tags with less than 3 notes and display that list. Then possibly use
        google to find related words and help suggest notes to tag with a specific tag.

        @todo The crappy_note_title_query list should be customizable elsewhere.
        """
        untagged_notes_query = "-tag:*"
        crappy_note_title_query = [
            "intitle:\"Pictures\"",
            "intitle:\"Documents\"",
            "intitle:\"Snapshot\"",
            "intitle:\"Unitled\"",
            "intitle:\"Fwd\"",
            "#look_into",
            "todo:false",
        ]
        search_query = "any: " + self._build_query_from_items(untagged_notes_query, crappy_note_title_query)
        return EverPy.search_notes(self, search_query)

    def proper_backup(self, backup_location, iterations=5):
        """
        Do a proper backup of all notes retaining Notebook names.

        @param backup_location Path to save backup
        @param iterations how many backup iterations to keep (default:5) (not currently being used)

        @todo This should also retain stack information
        """
        if (not backup_location.endswith(os.sep)):
            backup_location += os.sep
        # Get a list of all notebooks
        notebooks = EverPy.get_notebooks(self)
        # Create a folder with time-stamp
        ts = "{:%m-%d-%Y__%H-%M-%S}".format(datetime.now())
        backup_folder = "{0}enotebk__{1}".format(backup_location, ts)
        os.mkdir(backup_folder)
        for notebook in notebooks:
            print("Backing up {0}".format(notebook))
            EverPy.export_notes(
                self,
                "notebook:\"{0}\"".format(notebook),
                "{0}{1}{2}.enex".format(backup_folder, os.sep, notebook)
            )

    def automate_backup(self, query, backup_location, file_name, frequency, iterations):
        """
        Automate backup of notes.

        @param query Query for notes to backup
        @param backup_location Path to save backup
        @param file_name for backup
        @param frequency how often to backup in minutes
        @param iterations how many backup iterations to keep

        @todo this is not really automated what so ever needs to start some sort of service
        """
        if (not file_name.endswith(".enex")):
            file_name += ".enex"
        backup_file = backup_location + os.sep + file_name
        roll_files(backup_file, iterations)
        EverPy.export_notes(self, query, backup_file)

    def create_note_from_content(self, content, notebook_type="personal", notebook_name=None, title=None,
                                 tags=[], create_date=None, file_attachments=[]):
        """
        Create note from a python object.

        @param content object with string method
        @param notebook_type (optional) types are
                    personal - what you most likely want to user(default)
                    business - specify business notebook
        @param notebook_name (optional) name of notebook to store note.
                    If does not exist, lazy create. If omitted, use default notebook.
        @param title (optional) specifies note title.
                    If omitted, note title will be generated automatically.
        @param tags (optional) specify list of tags to tag note with.
                    If tag does not exist, lazy create it.
        @param create_date (optional) note creation date/time. { "YYYY/MM/DD hh:mm:ss" | filetime }.
                    If omitted, use current time.
        @param file_attachments list of file attachments.
        """
        if not title:
            title = self.get_title_from_content(content)

        f = tempfile.NamedTemporaryFile(suffix=".txt", delete=False)
        f.write(content)
        f.close()

        self.create_textnote_from_file(f.name, notebook_type=notebook_type, notebook_name=notebook_name, title=title,
                                   tags=tags, create_date=create_date, file_attachments=file_attachments)
        os.remove(f.name)
