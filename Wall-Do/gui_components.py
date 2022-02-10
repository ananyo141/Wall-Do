"""
 This file contains the GUI components that make 
 up the interface for Wall-Do

"""

# Wildcard imports are fine as this module deals with only
# tk widgets; use namespaces in the main script
import sys
from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox as msgb, filedialog as fldg
from exceptions import TopLevelWidgetsOnly


# Create the menu for the main window; May need to use the more
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
                                             'Licensed Under MIT License\n'
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

if __name__ == '__main__':
    root = Tk()
    root.title("Tester")
    MakeMenu(root)
    mainloop()
