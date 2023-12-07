import os
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import time
import saveload
import files
import datetime
import win32file
import webbrowser

# GLOBAL ######################################################################################################

totalSize = 0
liveSearch = saveload.getData('liveSearch')
listOfEverything = []

class SortedList:
    def findIndex(self, arr:list, item:int):
        lo = 0
        hi = len(arr)
        while lo < hi:
            mid = (lo+hi)//2
            if arr[mid] > item: 
                lo = mid+1 
            else: 
                hi = mid
        return lo

    def __init__(self):
        self.sortedList = []
    
    def add(self, number:int):
        insertionIndex = self.findIndex(self.sortedList, number)
        self.sortedList.insert(insertionIndex, number)
        return self.sortedList.index(number)

# FUNCTIONS ######################################################################################################

#toggles live search alongside the button title
def toggleLiveSearch():
    global liveSearch
    liveSearch = not liveSearch
    #change the button attributes
    liveSearchButton.config(text=f'LiveSearch {"ON" if liveSearch else "OFF"}')
    saveload.setData('liveSearch', liveSearch)
    if liveSearch:
        setLabels("Live search turned on.", "Interface will update while searching. Considerably slower.")
    else:
        setLabels("Live search turned off.", "Program will halt while searching. Much faster, but no indication of progress.")

#disable relevant buttons
def disableButtons():
    for button in globalButtons:
        button.config(state='disabled')

#the reverse
def enableButtons():
    for button in globalButtons:
        button.config(state='normal')

#takes an int time in seconds, then converts into a string that shows the hours, minutes and seconds.
def timeToString(seconds):
    int(seconds)
    hours = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return f"{f'{round(hours)} hours ' if hours>0 else ''}{f'{round(minutes)} minutes ' if minutes>0 else ''}{round(seconds, 2)} seconds"

#converts an integer size to a string format assuming that the size is in bytes
def sizeToString(size:int, precision:int=2):
    unit = "B"
    if size >= 1024:
        unit = "KB"
        size = size / 1024
    if size >= 1024:
        unit = "MB"
        size = size / 1024
    if size >= 1024:
        unit = "GB"
        size = size / 1024
    if precision == 0:
        return f"{round(size)}{unit}"
    return f"{round(size, precision)}{unit}"

#converts unixtime to a readable date string
def unixToString(unixtime:float):
    value = datetime.datetime.fromtimestamp(unixtime)
    return f"{value:%d/%m/%Y %H:%M:%S}"

#converts a unixtime to a readable date difference from the current date
def unixTimeDifferenceToString(unixtime:float):
    dateTime = datetime.datetime.fromtimestamp(unixtime)
    current_datetime = datetime.datetime.now()
    difference = current_datetime - dateTime
    months = difference.days // 30
    days = difference.days % 30
    hours, remainder = divmod(difference.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    if months > 0:
        return f"{months} {'month' if months == 1 else 'months'} ago"
    elif days > 0:
        return f"{days} {'day' if days == 1 else 'days'} ago"
    elif hours > 0:
        return f"{hours} {'hour' if hours == 1 else 'hours'} ago"
    elif minutes > 0:
        return f"{minutes} {'minute' if minutes == 1 else 'minutes'} ago"
    else:
        return f"{seconds} {'second' if seconds == 1 else 'seconds'} ago"

#set the first and second label
def setLabels(label1:str=None, label2:str=None):
    if(label1):
        statusLabel.config(text=label1)
    if(label2):
        statusLabel2.config(text=label2)

#walks through the directory in the inputbox and updates the directory list box accordingly
def walkDirectory():
    #clear everything in the listbox before putting anything
    dirlistbox.delete(0, tk.END)

    global listOfEverything
    listOfEverything.clear()
    completeList = SortedList()

    def insertListBox(size, folder, file):
        indexAdded = completeList.add(size)
        listOfEverything.insert(indexAdded, (size, folder, file))
        dirlistbox.insert(indexAdded, f"[{sizeToString(size)}] {file}")

    thisPath = dirBox.get()

    if(not os.path.exists(thisPath)):
        messagebox.showerror("Path not found", "Try another path.")
        return

    disableButtons()
    
    setLabels("Searching folder...", "This program is temporarily halted. If you want to update the interface while searching, turn on LiveSearch.")
    root.update()

    startTime = time.time()

    items = os.walk(thisPath)
    totalFiles = 0
    global totalSize
    totalSize = 0
    foldersSearched = 0

    for item in items:
        path = item[0] #path of folder
        subfolders = item[1] #list of subfolders
        files = item[2] #list of files
        foldersSearched+=1
        setLabels(label1=f"Searching {path}... ")
        for file in files: #this loops through every file in the folder.
            folder = path
            fullpath = path + "\\" + file
            size = os.path.getsize(fullpath)
            totalFiles+=1
            totalSize+=size
            setLabels(label2=f"File found ({totalFiles} found so far): {file}")
            insertListBox(size, folder, file)
            if liveSearch:
                root.update()
    
    totalTime = time.time()-startTime
    enableButtons()
    setLabels(f"{totalFiles} files, {foldersSearched-1} subfolders worth {sizeToString(totalSize)}", f"Time taken: {timeToString(totalTime)} at {int(totalFiles/totalTime)} files/sec (live search {'on' if liveSearch else 'off'})")

#opens a option to select the directory and then automatically calls walkDirectory()
def selectDirectory():
    filepath = filedialog.askdirectory(title='Select target directory...')
    if not filepath:
        return
    dirBox.delete(0, tk.END)
    dirBox.insert(0, filepath)
    walkDirectory()

#centers the window, and gives it a width and height
def centerWindow(window, width, height):
    # Get the screen width and height
    screenW = window.winfo_screenwidth()
    screenH = window.winfo_screenheight()
    x = (screenW // 2) - (width // 2)
    y = (screenH // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")

#display file menu when user clicks on a file.
def fileMenu(root, selectionIndex, size:tuple=(700,340)):
    contentTuple = listOfEverything[selectionIndex]
    #content tuple is of the format (size, folder, file)
    window = tk.Toplevel(root, bg=LIGHTPURPLE)
    centerWindow(window, size[0], size[1])
    window.title(contentTuple[2])
    window.focus_force()

    completeFilePath = os.path.join(contentTuple[1], contentTuple[2])
    filestats = os.stat(completeFilePath)
    global totalSize

    def delete():
        #removes from the central list, from the listbox, and deletes the file itself.
        if not files.delete(completeFilePath):
            return
        global totalSize
        totalSize -= contentTuple[0]
        listOfEverything.remove(contentTuple)
        dirlistbox.delete(selectionIndex)
        window.destroy()

    def refresh():
        fileMenu(root, selectionIndex)
        window.destroy()

    text = f"""Location:
{contentTuple[1]}
Size: {sizeToString(contentTuple[0])} ({(contentTuple[0]/totalSize)*100:.4g}% of target folder)
Created {unixTimeDifferenceToString(filestats.st_ctime)} ({unixToString(filestats.st_ctime)})  
Last modified {unixTimeDifferenceToString(filestats.st_mtime)} ({unixToString(filestats.st_mtime)})
Last accessed {unixTimeDifferenceToString(filestats.st_atime)} ({unixToString(filestats.st_atime)})
{"Readable" if os.access(completeFilePath, os.R_OK) else "Not Readable"}, {"Writable" if os.access(completeFilePath, os.W_OK) else "Not Writable"}, {"Executable" if os.access(completeFilePath, os.X_OK) else "Not Executable"}, {"Hidden" if (win32file.GetFileAttributes(completeFilePath) & win32file.FILE_ATTRIBUTE_HIDDEN) else "Visible"}"""

    pathLabel = tk.Label(window, text=text, font=('Microsoft Sans Serif', 13), bg=LIGHTPURPLE, fg=VERYWHITE)
    pathLabel.pack(pady=(4,4))

    buttonRow = tk.Frame(window, bg=LIGHTPURPLE)
    openFileExplorerButton = tk.Button(buttonRow, text="Open In File Explorer", font=('Microsoft Sans Serif', 12), command=lambda:files.showFileExplorer(contentTuple[1]))
    startFileButton = tk.Button(buttonRow, text="Open File", font=('Microsoft Sans Serif', 12), command=lambda:files.start(completeFilePath))
    deleteFileButton = tk.Button(buttonRow, text="Delete File", font=('Microsoft Sans Serif', 12), fg='red', command=delete)
    refreshInfoButton = tk.Button(buttonRow, text="Refresh Information", font=('Microsoft Sans Serif', 12), command=refresh)

    openFileExplorerButton.pack(pady=(4,4))
    startFileButton.pack(pady=(4,4))
    deleteFileButton.pack(pady=(4,4))
    refreshInfoButton.pack(pady=(4,4))
    buttonRow.pack()
    return window

def aboutWindow():
    window = tk.Toplevel(root, bg=LIGHTPURPLE)
    centerWindow(window, 400, 250)
    window.title("About...")
    window.focus_force()
    titleLabel = tk.Label(window, text='Darlene 1.0', font=('Helvetica', 15), bg=LIGHTPURPLE, fg=VERYWHITE)
    titleLabel.pack(pady=(10,2))
    desc = """Darlene is a tool that scans a given folder
and sorts every file, including those within 
nested folders, by size in descending order.
This helps to remove files you don't need, 
searching from the largest file downwards.
Useful for decluttering deeply nested folders.
    """
    def visitWebsite():
        webbrowser.open("https://github.com/desolaterobot/darlene")
    descLabel = tk.Label(window, text=desc, font=('Helvetica', 13), bg=LIGHTPURPLE, fg=VERYWHITE)
    descLabel.pack(pady=(2,2))
    visitGitHubButton = ttk.Button(window, text='Visit Github', command = visitWebsite, takefocus=False)
    visitGitHubButton.pack(pady=(2,2))
    

#happens whenever the listbox is clicked
def clickListBox(e):
    global listOfEverything
    selection = dirlistbox.curselection()
    if len(selection) == 0:
        setLabels('No folder selected.', 'Click on "Search for folder..." to select a folder to scan.')
        return
    if len(selection) == 1:
        fileMenu(root, selection[0])

# TKINTER ######################################################################################################

BGPURPLE = '#3D2C8D'
DARKPURPLE = '#1C0C5B'
WHITE = '#b3e4ff'
VERYWHITE = '#ffffff'
LIGHTPURPLE = '#7B6CF6'
BLACK = '#110036'

root = tk.Tk()

style=ttk.Style()
style.theme_use('default')
style.configure('TButton', font=('Helvetica', 12)) 
print(ttk.Style().theme_names())

targetLabel = tk.Label(root, text='Target Folder', font=('Helvetica', 14), bg=BGPURPLE, fg=WHITE)
targetLabel.pack(pady=(10,2))

dirBox = ttk.Entry(root, font=('Consolas', 13), width=80)
#dirBox.bind('<Return>', lambda e: refreshListBox(e, dirBox.get()))
dirBox.pack( pady=(10,2) )

#button frame, under the directory text box.
buttonFrame = tk.Frame(root, bg=BGPURPLE)
findDirectoryButton = ttk.Button(buttonFrame, text='Search for folder...', command = selectDirectory, takefocus=False)
findDirectoryButton.grid(column=0, row=0, padx=(2,2))
liveSearchButton = ttk.Button(buttonFrame, text=f'LiveSearch {"ON" if liveSearch else "OFF"}', command = toggleLiveSearch, takefocus=False)
liveSearchButton.grid(column=1, row=0, padx=(2,2))
aboutButton = ttk.Button(buttonFrame, text='About Darlene...', command = aboutWindow, takefocus=False)
aboutButton.grid(column=2, row=0, padx=(2,2))
globalButtons = [findDirectoryButton, liveSearchButton]
buttonFrame.pack(padx=10, pady=10)

#scrollable listbox frame: listbox on the left, vertical scrollbar on the left
listBoxFrame = tk.Frame(root, width=1100, height=500, bg=BGPURPLE)

verticalScrollBar = ttk.Scrollbar(listBoxFrame, orient=tk.VERTICAL)

dirlistbox = tk.Listbox(
    listBoxFrame, yscrollcommand=verticalScrollBar.set, 
    selectmode=tk.EXTENDED, width=140, height=20, font=('Consolas', 11),
    bg=DARKPURPLE, fg=WHITE, highlightbackground=WHITE,
    selectbackground=WHITE, selectforeground=DARKPURPLE, selectborderwidth=0,
)
dirlistbox.bind("<Double-Button-1>", clickListBox)

verticalScrollBar.config(command=dirlistbox.yview)
dirlistbox.grid(column=0, row=0)
verticalScrollBar.grid(column=1, row=0, sticky=tk.N+tk.S+tk.E+tk.W)
listBoxFrame.pack(padx=10, pady=(0,0))

statusLabel = tk.Label(root, text='No folder selected.', font=('Arial', 16), bg=BGPURPLE, fg=WHITE, anchor="w", justify="left", width=95)
statusLabel.pack(pady=(7,3))
statusLabel2 = tk.Label(root, text='Click on "Search for folder..." to select a folder to scan.', font=('Arial', 11), bg=BGPURPLE, fg=WHITE, anchor="w", justify="left", width=127)
statusLabel2.pack(pady=(0,2));

root.config(bg=BGPURPLE)
centerWindow(root, 1200, 600)

root.mainloop()