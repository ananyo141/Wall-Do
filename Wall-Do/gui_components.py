"""
 This module contains the GUI components that make 
 up the interface for Wall-Do

"""

# Wildcard imports are fine as this module deals with only
# tk widgets; use namespaces in the main script
import sys, os
from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox as msgb, filedialog as fldg
from exceptions import TopLevelWidgetsOnly

# Create the menu for the main window; may need to use the more
# specialized menu framework if menu needs to be created in other
# windows too
class MakeMenu:
    def __init__(self, topWidget):
        if not isinstance(topWidget, (Toplevel, Tk)):
            raise TopLevelWidgetsOnly("Not a Toplevel widget")
        self.topWidget = topWidget
        self.menubar = Menu(self.topWidget, tearoff=False)
        self.topWidget.config(menu=self.menubar)
        self.makemenu()

    def makemenu(self):
        self.makeFileMenu()
        self.makeToolsMenu()
        self.makeAboutMenu()

    def makeFileMenu(self):
        def quitButton():
            msgb.askyesno(title='Confirmation', 
                message='Are you sure you want to exit?') and sys.exit(0)

        fileMenu  = Menu(self.menubar, tearoff=False)
        self.menubar.add_cascade(label='File', menu=fileMenu, underline=0)
        fileMenu.add_command(label='Import',   command=self.importFile, underline=0)
        fileMenu.add_command(label='Export',   command=self.exportFile, underline=0)
        fileMenu.add_command(label='Quit',     command=quitButton,      underline=0)

    def makeToolsMenu(self):
        toolMenu = Menu(self.menubar, tearoff=False)
        self.menubar.add_cascade(label='Tools', menu=toolMenu, underline=0)
        toolMenu.add_command(label='Ping Site', command=self.pingEdit,   underline=0)
        toolMenu.add_command(label='Stop',      command=self.stopEdit,   underline=0)
        toolMenu.add_command(label='Resume',    command=self.resumeEdit, underline=0)

    def makeAboutMenu(self):
        self.menubar.add_command(label='About', command=self.aboutDialog, underline=0)

    def aboutDialog(self):
        msgb.showinfo(title='About', message='Author: Ananyobrata Pal\n'
                                             'Licensed Under: MIT License\n'
                                             '(c) Copyright: 2022-present')

    def importFile(self):
        raise NotImplementedError

    def exportFile(self):
        raise NotImplementedError
    
    def pingEdit(self):
        raise NotImplementedError

    def stopEdit(self):
        raise NotImplementedError

    def resumeEdit(self):
        raise NotImplementedError

# Reusable Frame components
# Make up the gui input body
class GuiInput(Frame):
    maxFieldWidth = max(map(len, ('Directory: ', 'search key: ', 'image number: ')))
    entryWidgetWidth = 30
    padding = dict(
        padx=4,
        pady=4
    )
    def __init__(self, parent, **kw):
        Frame.__init__(self, master=parent, **kw)
        self.dirVar = StringVar(value=os.getcwd())
        self.searchVarPlaceholder = 'Enter Search Key here'
        self.searchVar = StringVar(value=self.searchVarPlaceholder)
        self.numImageVar = IntVar(value=30)

        self.makeDirInput()
        self.makeSearchInput()
        self.makeNumImageInput()
    
    def makeDirInput(self):
        def chooseDir():
            inpDir = fldg.askdirectory(title='Enter directory')
            if inpDir:
                self.dirVar.set(os.path.normpath(inpDir))

        dirFrame = Frame(self)
        dirFrame.pack(expand=True, fill=BOTH)
        Label(dirFrame, text='Directory:', width=self.maxFieldWidth).pack(side=LEFT, **self.padding)
        Entry(dirFrame, textvariable=self.dirVar, 
                width=self.entryWidgetWidth).pack(side=LEFT, expand=True, fill=X, **self.padding)

        Button(dirFrame, text='Browse', command=chooseDir, 
                width=7).pack(side=RIGHT,  **self.padding)

    def makeSearchInput(self):
        def clearPlaceholder(event):
            if self.searchVar.get() == self.searchVarPlaceholder:
                searchEnt.delete('0', 'end')

        (searchFrame := Frame(self)).pack(expand=True, fill=BOTH)
        Label(searchFrame, text='Search Key: ', width=self.maxFieldWidth).pack(side=LEFT, **self.padding)
        searchEnt = Entry(searchFrame, textvariable=self.searchVar,
            width=self.entryWidgetWidth)
        searchEnt.bind('<FocusIn>', clearPlaceholder)
        searchEnt.pack(side=LEFT, **self.padding)

    def makeNumImageInput(self):
        numberFrame = Frame(self)
        numberFrame.pack(expand=True, fill=BOTH)

        Label(numberFrame, text='Image Number: ', width=self.maxFieldWidth).pack(side=LEFT, **self.padding)
        Entry(numberFrame, textvariable=self.numImageVar, width=self.entryWidgetWidth).pack(side=LEFT, **self.padding)

    def getValues(self):
        try:
            return (self.dirVar.get(), self.searchVar.get(), self.numImageVar.get())
        except TclError:
            msgb.showerror(title='Invalid Input', message='Please enter integer value for number of images')

# Downloader Info
class GuiDetails(Frame):
    pass

# Image Viewer
class GuiImgViewer(Frame):
    pass

if __name__ == '__main__':
    root = Tk()
    root.title("Tester")
    MakeMenu(root)
    (inp := GuiInput(root)).pack(expand=True, fill=BOTH)
    Button(root, text='Fetch', command=lambda: print(inp.getValues())).pack()
    mainloop()
