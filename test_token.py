from evernote.api.client import EvernoteClient

developer_token = "S=s1:U=92c92:E=168a7b75736:C=16150062b08:P=1cd:A=en-devtoken:V=2:H=73f5bda51480eea884d7a242c3e8c106"

# Set up the NoteStore client
client = EvernoteClient(token=developer_token)
user_store = client.get_user_store()
note_store = client.get_note_store()

# Make API calls
notebooks = note_store.listNotebooks()
for notebook in notebooks:
    print "Notebook: ", notebook.name