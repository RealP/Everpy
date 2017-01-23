"""Python helper for Evernote using Evernote API and EnScript."""
from __future__ import print_function
import re
import os
import binascii
import hashlib
from mimetypes import MimeTypes

import evernote.edam.type.ttypes as Types
from evernote.edam.notestore.ttypes import NoteFilter, NotesMetadataResultSpec
from evernote.api.client import EvernoteClient
from bs4 import BeautifulSoup

import everpy_utilities
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
        self.client = EvernoteClient(token=token, sandbox=False)
        self.user_store = self.client.get_user_store()
        self.note_store = self.client.get_note_store()

        self.note_header = "<?xml version='1.0' encoding='UTF-8'?><!DOCTYPE en-note SYSTEM 'http://xml.evernote.com/pub/enml2.dtd'><en-note>"
        self.note_footer = "</en-note>"

        self.note_book_dict = {}
        self.mimer = MimeTypes()
        self.learn_notebooks()

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

    def create_notebook_pro(self, notebook_name):
        """
        Create a notebook.

        @param notebook_name a string name for the notebook

        @todo there is a lot more that can be done here
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

    def get_resource(self, res):
        """Get a resource object to attach to note.

        @param res resource or attachment to attach.
        """
        resource_data = open(res, "rb").read()
        md5 = hashlib.md5()
        md5.update(resource_data)
        hash_val = md5.digest()
        hash_hex = binascii.hexlify(hash_val)

        data = Types.Data()
        data.size = len(resource_data)
        data.bodyHash = hash_hex
        data.body = resource_data

        resource_attributes = Types.ResourceAttributes()
        resource_attributes.fileName = res
        resource_attributes.sourceURL = "file://" + os.path.abspath(res)

        resource = Types.Resource()
        resource.attributes = resource_attributes
        mime, encoding = self.mimer.guess_type(res)
        if not mime:
            mime = "application/octet-stream"
        resource.mime = mime
        resource.data = data

        return resource

    def create_note(self, content, title=None, notebook=None, tags=[], attachments=[]):
        """Create a note and send to server."""
        note = Types.Note()
        note_body = self.note_header + content
        if title:
            note.title = title
        if notebook:
            note.notebookGuid = self.note_book_dict[notebook]["guid"]
        if tags:
            note.tagNames = tags
        if attachments:
            resources = [self.get_resource(a) for a in attachments]
            # Add Resource objects to note body
            note_body += "<br />" * 2
            note.resources = resources
            for resource in resources:
                note_body += "Attachment with hash {hash}: <br /><en-media type=\"{mime}\" hash=\"{hash}\" /><br />".format(
                    hash=resource.data.bodyHash,
                    mime=resource.mime
                )

        note_body += self.note_footer
        note.content = note_body
        self.note_store.createNote(note)

    def simple_template(self):
        """Create a simple note template.

        This is experimental for now.
        It should create a template then open that template for viewing
        """
        template = open("Templates/simple_sections.txt", "r").read()
        i = 1
        note_content = ""
        section_title = raw_input("Section {0} title (q:quit)".format(i))
        while(section_title != "q"):
            note_content += template.replace("{{sectiontitle}}", section_title)
            i += 1
            section_title = raw_input("Section {0} title (q:quit)".format(i))
        self.create_note(note_content)

    def simple_template2(self):
        """Create a simple note template.

        This is experimental for now.
        It should create a template then open that template for viewing
        """
        template = open("Templates/simple_sections.txt", "r").read()
        template_tokens = everpy_utilities.get_template_tokens(template)

        new_tokens = []
        another = ""
        while(another != "q"):
            # Why do i need to do this strange stuff with the dict to get it working?
            temp_dict = dict()
            for token, token_content in template_tokens.iteritems():
                temp_dict[token] = {}
                temp_dict[token]["name"] = token_content["name"]
                temp_dict[token]["val"] = raw_input("{0}: ".format(token_content["name"]))
            new_tokens.append(temp_dict)
            another = raw_input("Another (q:quit)")

        content = self.create_content_with_tokens(template, new_tokens)
        print(content)
        self.create_note(content, title="Test template")
        # print(content)
        # section_title = raw_input("Section {0} title (q:quit)".format(i))
        # while(section_title != "q"):
        #     note_content += template.replace("{{sectiontitle}}", section_title)
        #     i += 1
        #     section_title = raw_input("Section {0} title (q:quit)".format(i))

    def create_content_with_tokens(self, template, tokens):
        content = ""
        for token in tokens:
            temp_content = template
            print(token)
            for key, val in token.iteritems():
                findval = "${" + key
                if val["name"]:
                    findval += ":" + val["name"]
                findval += "}"
                temp_content = temp_content.replace(findval, val["val"])
            content += temp_content
        return content
