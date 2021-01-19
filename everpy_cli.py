"""Provide cli interface to everpy.

To use this you need a developer token until OAuth is implemented.
Get one here - https://www.evernote.com/api/DeveloperToken.action



Tests
----------
Everpy
python everpy_cli.py search -query "any:"
python everpy_cli.py export -query "intitle:\"En Scratch Paper\"" -file test.enex -scope personal

Everpy extras
python everpy_cli.py managenotes
python everpy_cli.py backup -dest "C:/Users/Paul/Desktop"

Everpy pro
python everpy_cli.py findandreplace -find "(?i)(evernote)" -replace "Evernote" -query "intitle:test"
python everpy_cli.py deletenotebook -name "deletemebook"

@todo Figure out how to deal with tags and file attachments from comamnd line
"""
import argparse
from everpy_pro import EverPyPro
import everpy_utilities

PATH_TO_ENSCRIPT = "C:/Program Files (x86)/Evernote/Evernote/ENScript.exe"


def add_enscript_cmds(sp):
    """Add the Everpy commands."""
    ####################################################
    # create the parser for the "search" command
    search_parser = sp.add_parser(
        'search',
        help='Run a search and open Evernote client with results'
    )
    search_parser.add_argument(
        "-query",
        dest="query",
        required=True,
        help="Evernote search query"
    )
    ####################################################

    ####################################################
    # create the parser for the "exportnotes" command
    exp_parser = sp.add_parser(
        'export',
        help='Export notes from a specified query'
    )
    exp_parser.add_argument(
        "-query",
        dest="query",
        required=True,
        help="Evernote search query"
    )
    exp_parser.add_argument(
        "-file",
        dest='export_file',
        required=True,
        help="Path to export .enex file"
    )
    exp_parser.add_argument(
        "-scope",
        dest='scope',
        default="personal",
        help="Use `business` to also search business notebooks. (default:`personal`)"
    )
    ####################################################


def add_everpy_extra_cmds(sp):
    """Add the Everpy Extra commands."""
    ####################################################
    # create the parser for the "backup" command
    bkp_parser = sp.add_parser(
        'backup',
        help='Do a proper backup of your notes'
    )
    bkp_parser.add_argument(
        "-dest",
        dest="dest",
        required=True,
        help="Path to save evernote export folder"
    )
    bkp_parser.add_argument(
        "-keep",
        dest='keep',
        default="5,",
        help="How many copies to keep (default:5)"
    )
    ####################################################

    ####################################################
    # create the parser for the "managenotes" command
    sp.add_parser(
        'managenotes',
        help='Open the Evernote Client with a list of notes to manage.'
    )
    ####################################################


def add_everpypro_cmd(sp):
    """Add the Everpy Pro commands."""
    ####################################################
    # create the parser for the "findandreplace" command
    fnr_parser = sp.add_parser(
        'findandreplace',
        help='Find and replace across notes'
    )
    fnr_parser.add_argument(
        "-find",
        dest="find",
        required=True,
        help="Regex search term"
    )
    fnr_parser.add_argument(
        "-replace",
        dest="repl",
        required=True,
        help="Replace value"
    )
    fnr_parser.add_argument(
        "-query",
        dest="query",
        default="any:",
        help="Evernote search query (default:`any:`)"
    )
    ####################################################

    ####################################################
    # create the parser for the "deletenotebook" command
    del_parser = sp.add_parser(
        'deletenotebook',
        help='Delete notebook permanently by name.'
    )
    del_parser.add_argument(
        "-name",
        dest="name",
        required=True,
        help="Name of the notebook to delete"
    )
    ####################################################


    ####################################################
    # create the parser for the "template" command
    tem_parser = sp.add_parser(
        'template',
        help='Create a template from an Everpy template file.'
    )
    tem_parser.add_argument(
        "-file",
        dest="template_file",
        required=True,
        help="Path to the template file"
    )
    tem_parser.add_argument(
        "-notebook",
        dest="notebook",
        default=None,
        help="Name of the notebook to save template"
    )
    tem_parser.add_argument(
        "-title",
        dest="title",
        default=None,
        help="The notes title"
    )
    tem_parser.add_argument(
        "-tags",
        dest="tags",
        default=None,
        help="tags"
    )
    tem_parser.add_argument(
        "-attachments",
        nargs='+',
        dest="attachments",
        default=None,
        help="attachments"
    )
    ####################################################


def get_cmd_line_args():
    """Parse cmd line args into tuple."""
    parser = argparse.ArgumentParser(
        prog='everpy.py',
        description="A series of Evernote helper tools from command line"
    )
    # Create the a subparser
    main_subparser = parser.add_subparsers(
        help="Choose between one of the following:",
        dest="option"
    )
    add_enscript_cmds(main_subparser)
    add_everpy_extra_cmds(main_subparser)
    add_everpypro_cmd(main_subparser)
    return (parser.parse_args())


def main():
    """Start of script."""
    # Get a dev token
    dev_token = everpy_utilities.get_token()
    # Parse args
    cmd_line_args = get_cmd_line_args()

    try:
        my_evernote = EverPyPro(dev_token, PATH_TO_ENSCRIPT)
    except:
        dev_token = everpy_utilities.refresh_token()
        my_evernote = EverPyPro(dev_token, PATH_TO_ENSCRIPT)

    ########################################################
    #              Deal with Everpy Commands               #
    if cmd_line_args.option == "search":
        out, err = my_evernote.search_notes(
            query=cmd_line_args.query
        )
        if out.strip():
            print(out)
        if err:
            print(err.strip())
    elif cmd_line_args.option == "export":
        out, err = my_evernote.export_notes(
            query=cmd_line_args.query,
            export_file=cmd_line_args.export_file,
            query_scope=cmd_line_args.scope
        )
        if out.strip():
            print(out)
        if err:
            print(err.strip())
    ########################################################
    #            Deal with Everpy Extra Commands           #
    elif cmd_line_args.option == "backup":
        my_evernote.proper_backup(
            cmd_line_args.dest,
            iterations=cmd_line_args.keep
        )
    elif cmd_line_args.option == "managenotes":
        out, err = my_evernote.get_notes_to_manage()
        if out.strip():
            print(out)
        if err:
            print(err.strip())
    ########################################################
    #            Deal with Everpy Pro Commands           #
    elif cmd_line_args.option == "deletenotebook":
        if my_evernote.delete_notebook(
            name=cmd_line_args.name
        ):
            print("Success")
    elif cmd_line_args.option == "findandreplace":
        my_evernote.find_and_replace(
            cmd_line_args.find,
            cmd_line_args.repl,
            cmd_line_args.query
        )
    elif cmd_line_args.option == "findandreplace":
        my_evernote.find_and_replace(
            cmd_line_args.find,
            cmd_line_args.repl,
            cmd_line_args.query
        )
    elif cmd_line_args.option == "template":
        my_evernote.create_template(
            cmd_line_args.template_file,
            notebook=cmd_line_args.notebook,
            title=cmd_line_args.title,
            tags=cmd_line_args.tags,
            file_attachments=cmd_line_args.attachments
        )
    else:
        pass
if __name__ == '__main__':
    main()
