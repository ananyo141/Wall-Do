"""
 This module contains the GUI components that make 
 up the interface for Wall-Do

"""

# Wildcard imports are fine as this module deals only with
# tk widgets; use namespaces in the main script
import sys, os, logging
from collections import namedtuple
from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox as msgb, filedialog as fldg
from PIL.ImageTk import Image, PhotoImage
from exceptions import TopLevelWidgetsOnly
from logger import mainlogger

# Create logger
guiLogger = logging.getLogger('main.gui')

# Create the menu for the main window; may need to use the more
# specialized menu framework if menu needs to be created in other
# windows too, subclass to define the handlers in main program
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
    fields = ('Directory: ', 'Search Key: ', 'Image Number: ')
    maxFieldWidth = max(map(len, fields))
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

        self.makeOptionMenu()
        self.makeDirInput()
        self.makeSearchInput()
        self.makeNumImageInput()
    
    def makeOptionMenu(self):
        optionFrame = Frame(self)
        optionFrame.pack(expand=True, fill=BOTH)

        options = ('wall.alphacoders.com', 'Others')
        self.optionMenuVar = StringVar()
        Label(optionFrame, text='Website: ', width=self.maxFieldWidth).pack(side=LEFT, **self.padding)
        opWidget = OptionMenu(optionFrame, self.optionMenuVar, 'https://wall.alphacoders.com', *options)
        opWidget.config(state='disabled')
        opWidget.pack(side=LEFT, fill=X, **self.padding)
    
    def makeDirInput(self):
        def chooseDir():
            inpDir = fldg.askdirectory(title='Enter directory')
            if inpDir:
                self.dirVar.set(os.path.normpath(inpDir))

        dirFrame = Frame(self)
        dirFrame.pack(expand=True, fill=BOTH)
        Label(dirFrame, text=self.fields[0], width=self.maxFieldWidth).pack(side=LEFT, **self.padding)
        Entry(dirFrame, textvariable=self.dirVar,
                width=self.entryWidgetWidth).pack(side=LEFT, expand=True, fill=X, **self.padding)

        Button(dirFrame, text='Browse', command=chooseDir,
                width=7).pack(side=RIGHT, **self.padding)

    def makeSearchInput(self):
        def clearPlaceholder(event):
            if self.searchVar.get() == self.searchVarPlaceholder:
                searchEnt.delete('0', 'end')

        (searchFrame := Frame(self)).pack(expand=True, fill=BOTH)
        Label(searchFrame, text=self.fields[1], width=self.maxFieldWidth).pack(side=LEFT, **self.padding)
        searchEnt = Entry(searchFrame, textvariable=self.searchVar,
            width=self.entryWidgetWidth)
        searchEnt.bind('<FocusIn>', clearPlaceholder)
        searchEnt.pack(side=LEFT, **self.padding)

    def makeNumImageInput(self):
        def numAdd():
            value = self.numImageVar.get()
            self.numImageVar.set(value + 5)
        def numSub():
            value = self.numImageVar.get() - 5
            value = 0 if value < 0 else value
            self.numImageVar.set(value)
        numberFrame = Frame(self)
        numberFrame.pack(expand=True, fill=BOTH)

        Label(numberFrame, text=self.fields[2],
            width=self.maxFieldWidth).pack(side=LEFT, **self.padding)
        Entry(numberFrame, textvariable=self.numImageVar,
            width=self.entryWidgetWidth).pack(side=LEFT, **self.padding)
        Button(numberFrame, text='+', width='1',
            command=numAdd).pack(side=LEFT, pady=self.padding.get('pady', 0))
        Button(numberFrame, text='-', width='1',
            command=numSub).pack(side=LEFT, pady=self.padding.get('pady', 0))

    def getValues(self):
        """
        Fetch the values from the gui fields and perform validation;
        Return named tuple of values if everything ok, else show
        error dialog and return None
        """
        def handleError(title, message):
            msgb.showerror(title=title, message=message)
            nonlocal invalidField       # change the nesting function's value
            invalidField = True         # from the nested function

        invalidField = False
        # validate search key
        searchKey = self.searchVar.get()
        if not searchKey or searchKey == self.searchVarPlaceholder:
            handleError('Required', 'Please Enter the search key')
        # validate input directory
        dirname = self.dirVar.get()
        if not os.path.exists(dirname):         # if directory is to be created
            parDir = os.path.dirname(dirname)   # check parent directory is writable
            checkAccessDir = os.curdir if not parDir else parDir
        else:
            checkAccessDir = dirname
        if not os.access(checkAccessDir, os.W_OK):
            handleError('Permission Error',
                        'Cannot write to given directory')
        # validate number input
        try:
            imageNum = self.numImageVar.get()
        except TclError:
            handleError('Invalid Input',
                        'Please enter integer value for number of images')
        else:
            if imageNum < 0:
                handleError('Negative Error',
                            'Negative number of images to download is not allowed')

        InputField = namedtuple('InputField', ['searchKey', 'dirname', 'imageNum'])
        guiLogger.info(f'{invalidField = }')
        return None if invalidField \
                    else InputField(searchKey=searchKey,
                                    dirname=dirname, imageNum=imageNum)

# Downloader Info
class GuiDetails(Frame):
    """
    A Subsection of the gui body that contains details about the
    current download, Session details, size, etc.; Progress bar,
    Label showing the current download image name, and 'Finished' if finished,
    """
    def __init__(self, parent=None, **kw):
        Frame.__init__(self, parent, **kw)
        self.sessionVar  = StringVar()
        self.progressVar = IntVar()
        self.currentVar  = StringVar()

        self.displaySessionDetails()
        self.displayProgressbar()
        self.displayStatus()

    def displaySessionDetails(self):
        Message(self, textvariable=self.sessionVar, 
                width=300, font=('consolas', 14, 'normal'),
        ).pack(expand=True,fill=BOTH)

    def displayProgressbar(self):
        Progressbar(self, var=self.progressVar, length=100, 
                    mode='determinate', orient='horizontal',
        ).pack(fill=X)

    def displayStatus(self):
        Message(self, textvariable=self.currentVar,
                width=300, font=('inconsolata', 20, 'bold'),
        ).pack(expand=True, fill=X)

# Image Viewer
class GuiImgViewer(Frame):
    """
    An Image viewer with a scrolled canvas at the center,
    support thumb caching, opens the image in a new window, with cursor 'hand2',
    and right click menu with options to open with system native app, delete,
    delete all and select delete
    """
    def __init__(self, parent=None, imgdir=os.curdir, 
                 canvsize=None, thumbsize=None, **kw):
        Frame.__init__(self, parent, **kw)
        self.imgdir = imgdir
        self.makeImgViewer(canvsize=canvsize, thumbsize=thumbsize)
        self.makeRightClickMenu()

    def makeImgViewer(self, canvsize=None, thumbsize=None, colsize=6):
        " Create the scrolled canvas with image thumbs "
        if canvsize is None: canvsize = (300,300)           # default canvas size
        if thumbsize is None: thumbsize = (90,60)           # default thumbsize
        canvWidth, canvHeight = canvsize
        canv = Canvas(self, width=canvWidth, height=canvHeight)

        # Use thumb caching, display in viewer
        imgObjs = self.makeThumbs(thumbsize, self.imgdir)

        # Calculate canvas scrollregion
        imgButtonWidth, imgButtonHeight = thumbsize
        requiredCanvWidth = imgButtonWidth * colsize
        requiredCanvHeight = imgButtonHeight * (len(imgObjs) // cosize)
        canv.config(scrollregion=(0, 0, requiredCanvWidth, requiredCanvHeight))

        # check if scrolls are needed
        needXScroll = canvWidth  < requiredCanvWidth
        needYScroll = canvHeight < requiredCanvHeight

        # Display the images in the given directory
        self.thumbsaves = []    # save thumbnails from being garbage collected
        rowPixel = 0            # calculate pixel offset from top of canvas
        while imgObjs:
            colPixel = 0        # calculate pixel offset from left of canvas
            imgRow, imgObjs = imgObjs[:colsize], imgObjs[colsize:]
            for imgTuple in imgRow:
                thumbPhoto = PhotoImage(imgTuple.obj)
                # make lambda remember each path
                handler = lambda path=imgTuple.path: \
                          ImageOpener(self, path).mainloop()
                imgButton = Button(canv, width=imgButtonWidth, image=thumbPhoto,
                            height=imgButtonHeight, command=handler)
                imgButton.pack()
                canv.create_window(colPixel, rowPixel, window=imgButton,
                    width=imgButtonWidth, height=imgButtonHeight, anchor=NW)
                self.thumbsaves.append(thumbPhoto)

                colPixel += imgButtonWidth
            rowPixel += imgButtonHeight

        if needYScroll:
            yscroll = Scrollbar(self, command=canv.yview)
            yscroll.pack(side=RIGHT, fill=Y)
            canv.config(yscrollcommand=yscroll.set)
        if needXScroll:
            xscroll = Scrollbar(self, command=canv.xview, orient='horizontal')
            xscroll.pack(side=BOTTOM, fill=X)
            canv.config(xscrollcommand=xscroll.set)
        canv.pack(expand=True, fill=BOTH)

        # save canvas obj for further config by user
        self.canvas = canv

    def makeRightClickMenu(self):
        pass

    @staticmethod
    def makeThumbs(thumbsize, imgdir=os.getcwd(), cachedir='.cache', enableCache=True):
        """
        Identify the images in the given directory and return
        a named tuple of (imgpath, imgobj) resized to given size;
        thumbsize is a tuple containing (width, height) of thumbnail
        """
        import mimetypes as mt
        Thumb = namedtuple('Thumb', ['path', 'obj', 'width', 'height'])

        cachedir = os.path.join(imgdir, cachedir)
        os.makedirs(cachedir, exist_ok=True)
        guiLogger.debug(f'{cachedir = }')
        thumbNameSpec = '%(fname)s_thumb%(width)dx%(height)d%(ext)s'
        thumblist = []

        for filename in os.listdir(imgdir):
            filepath = os.path.join(imgdir, filename)
            ftype, enc = mt.guess_type(filepath)
            # if file is a suitable image
            if os.path.isfile(filepath) and ftype and \
                ftype.split('/')[0] == 'image' and enc is None:
                head, ext = os.path.splitext(filepath)
                thumbname = thumbNameSpec % dict(
                    fname=head, width=size[0], height=size[1], ext=ext)
                thumbpath = os.path.join(cachedir, thumbname)

                # if cache exists
                if os.path.exists(thumbpath):
                    thumbObj = Image.open(thumbpath)
                # create cache
                else:
                    try:
                        thumbObj = Image.open(filepath)
                        thumbObj.thumb(size, Image.ANTIALIAS)
                        if enableCache:
                            thumbObj.save(thumbpath)
                    except Exception as exc:
                        guiLogger.error(f'Error creating thumbnail: {filepath}'
                                f'\nTraceback Details: {str(exc)}')
                        continue
                # Path to original file and resized thumbnail image object
                thumblist.append(Thumb(path=filepath, obj=thumbObj,
                                       width=thumbObj.width,
                                       height=thumbObj.height))
        return thumblist

# Toplevel Widget to display the image in a new window
class ImageOpener(Toplevel):
    def __init__(self, parent=None, **kw):
        Toplevel.__init__(parent, **kw)

if __name__ == '__main__':
    root = Tk()
    root.title("Tester")
    MakeMenu(root)
    (inp := GuiInput(root)).pack(expand=True, fill=BOTH)
    Button(root, text='Fetch', command=lambda: print(inp.getValues())).pack()
    mainloop()

