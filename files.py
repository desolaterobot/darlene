#functions related to files.

import os
import shutil
import tkinter.messagebox

def delete(path):
    if os.path.isfile(path):
        try:
            os.remove(path)
        except Exception as e:
            tkinter.messagebox.showerror("Error deleting file", f"File: {path}\n{str(e)}")
            return False
    else:
        try:
            shutil.rmtree(path)
        except Exception as e:
            tkinter.messagebox.showerror("Error deleting folder", f"Folder: {path}\n{str(e)}")
            return False
    return True

def start(filepath):
    if os.path.isfile(filepath):
        os.system(f'start "" "{filepath}"')

def showFileExplorer(path):
    if not os.path.isfile(path):
        os.system(f'start "" "{path}"')