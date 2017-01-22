"""Python helper for Evernote using Evernote API and EnScript."""
from __future__ import print_function
import re

import evernote.edam.type.ttypes as Types
from evernote.edam.notestore.ttypes import NoteFilter, NotesMetadataResultSpec
from evernote.api.client import EvernoteClient
from bs4 import BeautifulSoup

from everpy_extras import EverPyExtras

DEBUG = False


def debug(msg):
    """
    Used for debugging.

    @param msg msg
    """
    if DEBUG:
        print(msg)


class EverPyPro(EverPyExtras):
    """Python helper for evernote.

    Requires more than just ENScript.
    It requires user allow this application to modify data using OAuth
    """

    def __init__(self, token, path_to_enscript, username=None, password=None):
        r"""
        Initialize EverPyPro object.

        If both database file name and user name are not specified, last login name is used and
        if there is none, USERNAME environment variable value is used as a user name.

        @param token developer token for authentication
        @param path_to_enscript path the evernotes ENScript.exe
                                 usually "C:\Program Files (x86)\Evernote\Evernote\ENScript.exe"
        @param username if not using the default account you'll need to provide a username
        @param password if not using the default account you'll need to provide a password
        """
        super(EverPyPro, self).__init__(path_to_enscript, username, password)
        # self.client = EvernoteClient(token=token, sandbox=False)
        self.client = EvernoteClient(token=token)
        self.user_store = self.client.get_user_store()
        self.note_store = self.client.get_note_store()

        self.note_book_dict = {}

    def learn_notebooks(self):
        """
        Build dictionary of notebooks.

        Call this method to re-sync if Evernote database changed.
        """
        notebooks = self.note_store.listNotebooks()
        for n in notebooks:
            self.note_book_dict[n.name] = {}
            for key, val in vars(n).iteritems():
                self.note_book_dict[n.name][key] = val

    def get_tags(self):
        """Return list of tags."""
        return [tag.name for tag in self.note_store.listTags()]

    def get_searches(self):
        """Return list of tags."""
        return [s.name for s in self.note_store.listSearches()]

    def test(self):
        """Test function."""

        # tags = self.note_store.listSearches()  # get list of all tags
        # allTags = [tag.name for tag in tags]  # put all the names of the tags in a list
        # print(allTags)

        # out = self.note_store.getSearch("hello")
        # print(out)

    def find_and_replace(self, find_string, replace_string, query="any:", content_only=True):
        """
        Find and replace across your notes.

        @param find_string string to find
        @param replace_string string to replace
        @param query the query in which to replace notes. (default:'any:'')
        @param content_only Modify only the content of the note not the structure (default:True)

        @todo find a way to modify the structure of the note when content_only is True
        """
        withContent, withResoucesData, withResoucesRecognition, withResoucesAlternateData = (True, False, False, False)
        n_filter = NoteFilter(words=query)
        result_list = self.note_store.findNotesMetadata(n_filter, 0, 10000, NotesMetadataResultSpec(includeTitle=True))
        if len(result_list.notes) > 249:
            raise Exception("Too many notes found!")
        for note in result_list.notes:
            new_note = self.note_store.getNote(note.guid, withContent, withResoucesData, withResoucesRecognition, withResoucesAlternateData)
            # Make a soup from the HTML part of the note
            original_content = re.search("<en-note>((.|\n)+)<\/en-note>", new_note.content).group(1)
            soup = BeautifulSoup(original_content, "html.parser")

            original_matches = soup.findAll(text=re.compile(find_string))
            if not original_matches:
                # Nothing was found in this note continue to the next
                continue

            print("Replacing content in note {0}".format(note.title))
            debug("new_note.content = {0}".format(new_note.content))
            debug("original_matches = {0}".format(original_matches))

            # Run a regex replacement for each match
            new_matches = [re.sub(find_string, replace_string, match) for match in original_matches]

            debug("new_matches = {0}".format(new_matches))

            # Get the matches from the soup AGAIN to change it.... :/ ??
            for i, m in enumerate(soup.findAll(text=re.compile(find_string))):
                m.replaceWith(new_matches[i])

            debug("soup = \r\n{0}".format(str(soup)))

            # Replace the original HTML part of the note with the new soup
            new_note.content = new_note.content.replace(original_content, str(soup))
            self.note_store.updateNote(new_note)

    def create_notebook(self, notebook_name):
        """
        Create a notebook.

        @param notebook_name a string name for the notebook
        """
        n_data = Types.Notebook()
        n_data.name = notebook_name
        n_book_guid = self.note_store.createNotebook(n_data)
        debug("Created notebook {0} guid = {1}".format(notebook_name, n_book_guid))
        self.learn_notebooks()  # Need to relearn notebooks now.

    def delete_notebook(self, name):
        """
        Delete notebook permanently by name.

        Permanently removes the notebook from the user's account. After this action, the notebook is no longer available for undeletion, etc. If the notebook contains any Notes, they will be moved to the current default notebook and moved into the trash (i.e. Note.active=false)
        """
        if not self.note_book_dict:
            self.learn_notebooks()
        try:
            n_guid = self.note_book_dict[name]["guid"]
        except KeyError:
            print("Couldn't find notebook {0}. Refreshing notebook list...".format(name))
            self.learn_notebooks()
            if name in self.note_book_dict.keys():
                print("Okay found it")
            else:
                return False
        update_sequence_num = self.note_store.expungeNotebook(n_guid)
        print("Deleted notebook update_sequence_num = {0}".format(update_sequence_num))
        return True

    def tag_notes_with_season(self):
        """
        Tag notes based on season of the year.

        Implementation details:
            search for notes between dates such as 12-01-1972 - 04-2-1973  then tag those notes as winter or whatever

        @todo This is really just an idea of what can be done
        """
        # spring_begin_day = "0301"
        # summer_begin_day = "0601"
        # fall_begin_day = "1001"
        # winter_begin_day = "1201"
        pass
