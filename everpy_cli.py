"""Provide cli interface to everpy.

To use this you need a developer token until OAuth is implemented.
Get one here - https://www.evernote.com/api/DeveloperToken.action
"""
import argparse
import keyring
import getpass

import everpy_pro

PATH_TO_ENSCRIPT = "C:\Program Files (x86)\Evernote\Evernote\ENScript.exe"


def get_cmd_line_args():
    """Parse cmd line args into tuple."""
    parser = argparse.ArgumentParser(
        prog='everpy.py',
        description="A series of Evernote helper tools from command line"
    )

    # Create the a subparser
    subparsers = parser.add_subparsers(
        help="Choose between one of the following:",
        dest="option"
    )
    ####################################################
    # create the parser for the "search" command
    search_parser = subparsers.add_parser(
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
    # create the parser for the "managenotes" command
    subparsers.add_parser(
        'managenotes',
        help='Open the Evernote Client with a list of notes to manage.'
    )
    ####################################################

    ####################################################
    # create the parser for the "findandreplace" command
    fnr_parser = subparsers.add_parser(
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
    # create the parser for the "exportnotes" command
    exp_parser = subparsers.add_parser(
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

    ####################################################
    # create the parser for the "backup" command
    bkp_parser = subparsers.add_parser(
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
    # create the parser for the "deletenotebook" command
    del_parser = subparsers.add_parser(
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

    return(parser.parse_args())


def refresh_token():
    """Set new token."""
    keyring.set_password("everpy", "everpy", getpass.getpass("Password: "))
    return keyring.get_password("everpy", "everpy")


def get_token():
    """Get a token."""
    dev_token = keyring.get_password("everpy", "everpy")
    if not dev_token:
        dev_token = refresh_token()
    return dev_token


# Script execution starts here

# Get the dev token
dev_token = get_token()

cmd_line_args = get_cmd_line_args()

try:
    my_evernote = everpy_pro.EverPyPro(dev_token, PATH_TO_ENSCRIPT)
except:
    refresh_token()
    my_evernote = everpy_pro.EverPyPro(dev_token, PATH_TO_ENSCRIPT)

if cmd_line_args.option == "backup":
    my_evernote.everpy_extras.proper_backup(
        cmd_line_args.dest,
        iterations=cmd_line_args.keep
    )
elif cmd_line_args.option == "findandreplace":
    my_evernote.find_and_replace(
        cmd_line_args.find,
        cmd_line_args.repl,
        cmd_line_args.query
    )
elif cmd_line_args.option == "managenotes":
    out, err = my_evernote.everpy_extras.get_notes_to_manage()
    if out.strip():
        print(out)
    if err:
        print(err.strip())
elif cmd_line_args.option == "search":
    out, err = my_evernote.everpy_extras.search_notes(
        query=cmd_line_args.query
    )
    if out.strip():
        print(out)
    if err:
        print(err.strip())
elif cmd_line_args.option == "export":
    out, err = my_evernote.everpy_extras.export_notes(
        query=cmd_line_args.query,
        export_file=cmd_line_args.export_file,
        query_scope=cmd_line_args.scope
    )
    if out.strip():
        print(out)
    if err:
        print(err.strip())
elif cmd_line_args.option == "deletenotebook":
    if my_evernote.delete_notebook(
        name=cmd_line_args.name
    ):
        print("Success")
else:
    pass
