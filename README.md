#Everpy
An enhanced Evernote CLI

Features include
 + Regular Expression Find and replaces across all or a subset of notes.
 + Proper backups retaining notebook information

*Comnig soon template generation...*

##Setup
###Python Requirements:
    
    pip install evernote
    pip install bs4
    pip install keyring
    
###Configuration:
You will need to edit the `PATH_TO_ENSCRIPT` variable at the top of everpy_cli.py if your ENScript is not in the `C:\Program Files (x86)\Evernote\Evernote\` directory.

You need to get a developer token from Evernote. The first time you run the app you will be prompted for this key. 

*[Get your key here](https://www.evernote.com/api/DeveloperToken.action).*

##Usage
####Find and replace example

    python everpy_cli.py findandreplace -find "123 fake st" -replace "545 new st" -query "notebook:Personal"

####Backup example

    python everpy_cli.py backup -dest "C:\Users\User\Desktop"
    
For more info run

    python everpy_cli.py -h
    
