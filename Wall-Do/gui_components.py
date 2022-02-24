"""
 This module contains the GUI components that make 
 up the interface for Wall-Do

"""

# Wildcard imports are fine as this module deals only with
# tk widgets; use namespaces in the main script
import sys, os, logging, mimetypes as mt
from collections import namedtuple
from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox as msgb, filedialog as fldg
from PIL.ImageTk import Image, PhotoImage
from exceptions import TopLevelWidgetsOnly
from downloader import AlphaDownloader
from logger import mainlogger

Image.MAX_IMAGE_PIXELS = 1024 * 1024 * 100   # 100 MB max

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
        fileMenu.add_separator()
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

    def __notImplemented(self):
        """
        private function to act as a placeholder to a non-redefined
        method
        """
        msgb.showerror(title='Not Implemented',
                       message='This feature is not yet implemented')
    # Subclass Methods
    def importFile(self):
        self.__notImplemented()

    def exportFile(self):
        self.__notImplemented()
    
    def pingEdit(self):
        self.__notImplemented()

    def stopEdit(self):
        self.__notImplemented()

    def resumeEdit(self):
        self.__notImplemented()

# Reusable Frame components
# Make up the gui input body
class GuiInput(Frame):
    fields = ('Directory: ', 'Search Key: ', 'Image Number: ')
    maxFieldWidth = max(map(len, fields))
    entryWidgetWidth = 30
    padding = dict(
        padx=4,
        pady=4,
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
            inpDir = fldg.askdirectory(title='Enter directory', mustexist=False)
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
                searchEnt.delete('0', END)
        def enterPlaceholder(event):
            if self.searchVar.get() == '':
                searchEnt.insert(END, self.searchVarPlaceholder)

        searchFrame = Frame(self)
        searchFrame.pack(expand=True, fill=BOTH)
        Label(searchFrame, text=self.fields[1], width=self.maxFieldWidth).pack(side=LEFT, **self.padding)
        searchEnt = Entry(searchFrame, textvariable=self.searchVar,
            width=self.entryWidgetWidth)
        searchEnt.bind('<FocusIn>',  clearPlaceholder)
        searchEnt.bind('<FocusOut>', enterPlaceholder)
        searchEnt.pack(side=LEFT, **self.padding)

    def makeNumImageInput(self):
        def numAdd():
            try:
                value = self.numImageVar.get()
                self.numImageVar.set(value + 5)
            except:
                msgb.showerror(title='Check Value', message='Invalid Field')
        def numSub():
            try:
                value = self.numImageVar.get() - 5
                value = 0 if value < 0 else value
                self.numImageVar.set(value)
            except:
                msgb.showerror(title='Check Value', message='Invalid Field')
        numberFrame = Frame(self)
        numberFrame.pack(expand=True, fill=BOTH)

        Label(numberFrame, text=self.fields[2],
            width=self.maxFieldWidth).pack(side=LEFT, **self.padding)
        Entry(numberFrame, textvariable=self.numImageVar,
            width=self.entryWidgetWidth).pack(side=LEFT, **self.padding)
        Button(numberFrame, text='+', width='2',
            command=numAdd).pack(side=LEFT, **self.padding)
        Button(numberFrame, text='-', width='2',
            command=numSub).pack(side=LEFT, **self.padding)

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
        self.idFileDict = dict()   # keep track of canvas ids and filenames
        self.imgdir = imgdir
        self.makeImgViewer(canvsize=canvsize, thumbsize=thumbsize)
        self.makeRightClickMenu()

    def config(imgdir):
        self.imgdir = imgdir

    def makeImgViewer(self, canvsize=None, thumbsize=None, colsize=4):
        " Create the scrolled canvas with image thumbs "
        if canvsize is None: canvsize = (300,300)           # default canvas size
        if thumbsize is None: thumbsize = (90,60)           # default thumbsize
        canvWidth, canvHeight = canvsize
        canv = Canvas(self, width=canvWidth, height=canvHeight,
                      bd=2, relief=GROOVE)

        # Use thumb caching, display in viewer
        imgObjs = self.makeThumbs(thumbsize, self.imgdir)

        # Calculate canvas scrollregion
        imgButtonWidth, imgButtonHeight = thumbsize
        requiredCanvWidth = imgButtonWidth * colsize
        requiredCanvHeight = imgButtonHeight * (len(imgObjs) // colsize)
        canv.config(scrollregion=(0, 0, requiredCanvWidth, requiredCanvHeight))

        guiLogger.debug(f'{imgButtonWidth = }, {imgButtonHeight = }')
        guiLogger.debug(f'{requiredCanvWidth = }, {requiredCanvHeight = }')

        # check if scrolls are needed
        needXScroll = canvWidth  < requiredCanvWidth;        guiLogger.debug(f'{needXScroll = }')
        needYScroll = canvHeight < requiredCanvHeight;       guiLogger.debug(f'{needYScroll = }')

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
                            command=handler, cursor='hand2')
                imgButton.pack()
                canv_id = canv.create_window(colPixel, rowPixel, window=imgButton,
                    width=imgButtonWidth, height=imgButtonHeight, anchor=NW)
                self.idFileDict[canv_id] = imgTuple.path

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

        guiLogger.debug(f'{self.idFileDict = }')
        canv.pack(expand=True, fill=BOTH)
        # save canvas obj for further config by user
        self.canv = canv

    def makeRightClickMenu(self):
        """
        Create Right Click menu for Image Viewer
        """
        def onRightClick(event):
            self.rightClickEvent = event
            try:
                rightClickMenu.tk_popup(event.x_root, event.y_root)
            finally:
                rightClickMenu.grab_release()

        rightClickMenu = Menu(self.canv, tearoff=False)
        rightClickMenu.add_command(label='Open with Default App', 
                                   command=self.rightDefaultApp)
        rightClickMenu.add_separator()
        rightClickMenu.add_command(label='Delete', 
                                   command=self.rightDelete)
        rightClickMenu.add_command(label='Delete All', 
                                   command=self.rightDeleteAll)

        self.canv.bind('<Button-3>', onRightClick)

    def rightDefaultApp(self):
        " Open the image in native system app "
        import webbrowser
        canv_id = self.canv.find_closest(self.event.x, self.event.y)
        webbrowser.open(self.idFileDict[canv_id])

    def rightDelete(self):
        " Delete the selected image "
        canv_id = self.canv.find_closest(self.event.x, self.event.y)
        # may use send2trash to delete to recycle bin
        os.unlink(self.idFileDict[canv_id])

    def rightDeleteAll(self):
        " Delete the all images "
        for filename in os.listdir(self.imgdir):
            ftype, enc = mt.guess_type(filename)
            if ftype and ftype.split('/')[0] == 'image':
                os.unlink(os.path.join(self.imgdir, filename))

    @staticmethod
    def makeThumbs(thumbsize, imgdir=os.getcwd(), cachedir='.cache', enableCache=True):
        """
        Identify the images in the given directory and return
        a named tuple of (imgpath, imgobj) resized to given size;
        thumbsize is a tuple containing (width, height) of thumbnail
        """
        Thumb = namedtuple('Thumb', ['path', 'obj', 'width', 'height'])

        cachedir = os.path.join(imgdir, cachedir)
        os.makedirs(cachedir, exist_ok=True)
        thumbNameSpec = '%(fname)s_thumb%(width)dx%(height)d%(ext)s'
        thumblist = []

        for filename in os.listdir(imgdir):
            filepath = os.path.join(imgdir, filename)
            ftype, enc = mt.guess_type(filepath)
            # if file is a suitable image
            if os.path.isfile(filepath) and ftype and \
                ftype.split('/')[0] == 'image' and enc is None:
                head, ext = os.path.splitext(filename)
                thumbname = thumbNameSpec % dict(
                    fname=head, width=thumbsize[0], height=thumbsize[1], ext=ext)
                thumbpath = os.path.join(cachedir, thumbname)
                guiLogger.debug(f'{thumbpath = }')

                # if cache exists
                if os.path.exists(thumbpath):
                    thumbObj = Image.open(thumbpath)
                # create cache
                else:
                    try:
                        thumbObj = Image.open(filepath)
                        thumbObj.thumbnail(thumbsize, Image.ANTIALIAS)
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

# Automatic Scrollbar that hides and returns
# when widget associated is resized
class AutoScrollbar(Scrollbar):
   def set(self, low, high):
       if float(low) <= 0 and float(high) >= 1:
           self.tk.call("grid", "remove", self)
       else:
           self.grid()
       Scrollbar.set(self, low, high)
   
   def pack(self):
       raise (TclError, "Can't use pack; only grid")

   def place(self):
       raise (TclError, "Can't use place; only grid")

# Toplevel Widget to display the image in a new window
# Resize the image to the screen width
class ImageOpener(Toplevel):
    def __init__(self, parent, imgPath, **kw):
        Toplevel.__init__(self, parent, **kw)
        self.imgPath = imgPath
        self.showImage()
        self.focus_set()
        try:
            self.state('zoomed')    # for windows
        except TclError:
            self.state('iconic')    # for unix

    def showImage(self):
        " Show the image in fullscreen filling screen "
        screenWidth, screenHeight = (self.winfo_screenwidth() - 25), (self.winfo_screenheight() - 70)
        guiLogger.info(f'{screenWidth = }, {screenHeight = }')
        image = Image.open(self.imgPath)
        image = image.resize((screenWidth, screenHeight), Image.ANTIALIAS)
        photo = PhotoImage(image)

        yscroll = AutoScrollbar(self)
        xscroll = AutoScrollbar(self, orient='horizontal')
        canv = Canvas(self, yscrollcommand=yscroll.set,
                            xscrollcommand=xscroll.set,
                            scrollregion=(0, 0, screenWidth, screenHeight))
        yscroll.config(command=canv.yview)
        xscroll.config(command=canv.xview)
        canv.create_image(0, 0, image=photo, anchor=NW)
        guiLogger.info(f'{photo.width() = }')
        guiLogger.info(f'{image.width = }')

        canv.grid(row=0, column=0, sticky=NSEW)
        yscroll.grid(row=0, column=1, sticky=NS)
        xscroll.grid(row=1, column=0, sticky=EW)

        # Expand canvas
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.photo = photo  # save from garbage collection

"""
GUI oriented Downloader that updates status with tk variables
Use multiple inheritance for is-a relationships,
the guidownloader is both a frame and a downloader
"""
class GuiDownloader(Frame, AlphaDownloader):
    def __init__(self, parent=None):
        # Base Class Init
        Frame.__init__(self, parent)
        AlphaDownloader.__init__(self, trace=False)

        self.sessionVar  = StringVar(value='Enter a search keyword '
                                        'to start downloading!')
        self.progressVar = DoubleVar()
        self.currentVar  = StringVar()

        self.makeGuiInput()
        self.makeGuiDetails()
        self.makeGuiViewer()
        self.makeDownloadButton()

    # Downloader Info
    def makeGuiInput(self):
        " Position the gui input frame "
        self.guiInput = GuiInput(self)
        self.guiInput.pack()

    def makeGuiDetails(self):
        " Create the Gui details section "
        Message(self, textvariable=self.sessionVar, 
                width=300, font=('consolas', 12, 'bold italic'),
        ).pack(expand=True,fill=BOTH)
        Progressbar(self, var=self.progressVar, length=100, 
                    mode='determinate', orient='horizontal',
        ).pack(fill=BOTH)
        Message(self, textvariable=self.currentVar,
                width=350, font=('inconsolata', 15, 'italic'),
        ).pack(expand=True, fill=BOTH)

    def makeGuiViewer(self):
        pass

    def downloadImage(self, link, name=''):
        AlphaDownloader.downloadImage(self, link, name)
        with self.mutex:
            self.currentVar.set(f'Downloaded\n{link}...')
            self.progressVar.set((self.numDownloaded / self.numImages) * 100)
            downloadLogger.debug(f'{self.numDownloaded = }')

    def startDownload(self, *args, **kw):
        AlphaDownloader.startDownload(self, *args, **kw)
        self.sessionVar.set(self.printFormat % self.sessionDict)
        self.currentVar.set('Finished')

if __name__ == '__main__':
    import webbrowser
    root = Tk()
    root.title("Tester")
    MakeMenu(root)
    inp = GuiInput(root)
    inp.pack(expand=True, fill=BOTH)
    Button(root, text='Fetch', command=lambda: print(inp.getValues())).pack()
    Button(root, text='Window', command=lambda: ImageOpener(root, fname).mainloop()).pack()
    Button(root, text='Native', command=lambda: webbrowser.open(fname)).pack()
    fname = fldg.askopenfilename() or sys.exit("No image chosen")
    mainloop()

