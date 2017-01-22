"""Python wrapper for Evernote's ENScript.exe.

Only tested on Windows.
"""
from __future__ import print_function
import sys
import subprocess

DEBUG = False


def debug(msg):
    """debugging print."""
    if DEBUG:
        print(msg)


class EverPy(object):
    """Python helper for evernote."""

    def __init__(self, path_enscript_exe, username=None, password=None):
        r"""
        Initialize EverPy object.

        If both database file name and user name are not specified, last login name is used and
        if there is none, USERNAME environment variable value is used as a user name.

        @param path_enscript_exe path the evernotes ENScript.exe
                                 usually "C:\Program Files (x86)\Evernote\Evernote\ENScript.exe"
        @param username if not using the default account you'll need to provide a username
        @param password if not using the default account you'll need to provide a password
        """
        super(EverPy, self).__init__()
        self.enscript_core_args = [path_enscript_exe]
        if username:
            self.enscript_core_args += ["/u", username]
        if password:
            self.enscript_core_args += ["/p", password]

    @staticmethod
    def get_title_from_content(content):
        """
        Get title from content similar to how Evernote does.

        @param content The content for which you want title
        @retval string representing title of content
        """
        for line in content.splitlines():
            if line:
                return line[:80]

    @staticmethod
    def append_notebook_type(arr, notebook_type, notebook_name):
        """
        Append notebook type to en_args.

        @param arr the list to append to
        @param notebook_type valid options are:
                personal - what you most likely want to user(default)
                business - specify business notebook
        @param notebook_name the name of the notebook
        @retval new array with notebook type and name appended
        """
        if notebook_type == 'personal':
            arr += ["/n", notebook_name]
        elif notebook_type == "business":
            arr += ["/b", notebook_name]
        else:
            sys.exit("Unsupport notebook type {0}".format(notebook_type))
        return arr

    def call_enscript(self, additional_args):
        """
        Call enscript with set arguments.

        @param additional_args should be a list
        @retval tuple with stdout and stderr
        """
        debug(additional_args)
        cmd = self.enscript_core_args + additional_args
        debug(cmd)
        debug("Running script \"{0}\"".format(" ".join(cmd)))
        out, err = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        if out:
            debug(out)
        if err:
            debug(err)
        return out, err

    def search_notes(self, query="any:"):
        """
        Show notes for search query in the Evernote window.

        @param query string query to search for (default='any:')
        """
        en_args = ["showNotes", "/q"]
        en_args.append(query)
        return self.call_enscript(en_args)

    def get_notebooks(self):
        """
        Method to get notebook list.

        @retval list of notebooks
        """
        en_args = ["listNotebooks"]
        out, err = self.call_enscript(en_args)
        if err:
            print(err)
        return out.splitlines()

    def create_notebook(self, notebook_name, notebook_type="synced"):
        """
        Create a notebook.

        @param notebook_name a string name for the notebook
        @param notebook_type 1 of the 3 Evernote notebook types (default:synced)
                    local    - does not sync with Evernote server. (local to machine)
                    synced   - standard notebook accessible on all devices
                    business - business notebook (For business users)
        """
        en_args = ["createNotebook", "/n", notebook_name, '/t', notebook_type]
        return self.call_enscript(en_args)

    def create_note_from_file(self, file_with_notes, notebook_type="personal", notebook_name=None, title=None,
                              tags=None, create_date=None, file_attachments=None):
        """
        Create note from a file.

        @param file_with_notes path to file containing the plain text note contents
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
        @param file_attachments (optional) list of file attachments.
        """
        en_args = ["createNote", "/s", file_with_notes]
        if notebook_name:
            en_args = self.append_notebook_type(en_args, notebook_type, notebook_name)
        print(en_args)
        if title:
            en_args += ["/i", title]
        if tags:
            for tag in tags:
                en_args += ["/t", tag]
        if create_date:
            # need to deal with formatting here maybe check user input via regex
            en_args += ["/c", create_date]
        if file_attachments:
            for attachment in file_attachments:
                en_args += ["/a", attachment]

        return self.call_enscript(en_args)

    def import_notes(self, enex_file, notebook_type="personal", notebook_name=None):
        """
        Import notes from specified export file or url.

        @param enex_file path to source .enex file or url.
        @param notebook_type optional types are
                    personal - what you most likely want to use (default)
                    business - specify business notebook
        @param notebook_name name of notebook to store note.
                    If does not exist, lazy create. If omitted, use default notebook.
        """
        en_args = ["importNotes", "/s", enex_file]
        if notebook_name:
            en_args = self.append_notebook_type(en_args, notebook_type, notebook_name)
        return self.call_enscript(en_args)

    def export_notes(self, query, export_file, query_scope="personal"):
        """
        Export specified notes into a file.

        @param query query to filter the notes.
        @param export_file path to export .enex file
        @param query_scope optional types are
                    personal - what you most likely want to use (default)
                    business - specify business notebook
        """
        en_args = ["exportNotes", "/q", query, "/f", export_file, "/s", query_scope]
        return self.call_enscript(en_args)

    def sync_database(self, log_file=None):
        """
        Synchronize database to the service.

        @param log_file log file name. Use standard log if omitted. Ignored in GUI implementation.

        @todo Needs to implemented eventually
        """
        pass
