"""
 This module contains the GUI components that make 
 up the interface for Wall-Do

"""

# Wildcard imports are fine as this module deals only with
# tk widgets; use namespaces in the main script
import sys, os, logging, threading
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

# Automatic Scrollbar that hides and returns
# when associated widget is resized
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
        screenWidth, screenHeight = (self.winfo_screenwidth() - 20), (self.winfo_screenheight() - 80)
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

    def startDownload(self, *args, **kw):
        self.xoffset = 0    # initialize canvas pixel offsets
        self.yoffset = 0    # for inserting image buttons
        self.thumbsaves = []

        self.canv.delete(ALL)
        AlphaDownloader.startDownload(self, *args, **kw)
        self.sessionVar.set(self.printFormat % self.sessionDict)
        self.currentVar.set('Finished')

    def downloadImage(self, link, name=''):
        AlphaDownloader.downloadImage(self, link, name)
        with self.mutex:
            self.currentVar.set(f'Downloaded\n{link}...')
            self.progressVar.set((self.numDownloaded / self.numImages) * 100)
            guiLogger.debug(f'{self.numDownloaded = }')
            # Populate the canvas
            self.createThumbnailOnCanvas()

    # Downloader Info
    def makeGuiInput(self):
        " Position the gui input frame "
        self.guiInput = GuiInput(self)
        self.guiInput.pack()

    def makeGuiDetails(self):
        " Create the Gui details section "
        Message(self, textvariable=self.sessionVar, 
                width=300, font=('consolas', 12, 'bold italic'),
        ).pack()
        Progressbar(self, var=self.progressVar, length=100,
                    mode='determinate', orient='horizontal',
        ).pack(fill=X, padx=14, pady=14)
        Message(self, textvariable=self.currentVar,
                width=350, font=('inconsolata', 15, 'italic'),
        ).pack()

    def makeGuiViewer(self, canvsize=(300,300)):
        " Create the viewer canvas "
        canvFrame = Frame(self)
        canvFrame.pack(expand=True, fill=BOTH)
        canv = Canvas(canvFrame, bd=2, 
                      width=canvsize[0], 
                      height=canvsize[1], 
                      relief=GROOVE)
        yscroll = Scrollbar(canvFrame, command=canv.yview)
        canv.config(yscrollcommand=yscroll.set)

        yscroll.pack(side=RIGHT, fill=Y)
        canv.pack(side=LEFT, expand=True, fill=BOTH)

        self.idFileDict = dict()    # save button ids and their
        self.canv = canv            # corresponding image filenames
        self.canvsize = canvsize
        self.makeRightClickMenu()

    def onRightClick(self, event):
        " Right click popup; handler for bind calls "
        self.rightClickEvent = event
        try:
            self.rightClickMenu.tk_popup(event.x_root, event.y_root)
        finally:
            self.rightClickMenu.grab_release()

    def makeRightClickMenu(self):
        " Create Right click menu for image viewer canvas "
        rightClickMenu = Menu(self.canv, tearoff=False)
        rightClickMenu.add_command(label='Open with Default App', 
                                   command=self.rightDefaultApp)
        rightClickMenu.add_separator()
        rightClickMenu.add_command(label='Delete', 
                                   command=self.rightDelete)
        rightClickMenu.add_command(label='Delete All', 
                                   command=self.rightDeleteAll)
        self.canv.bind('<Button-3>', self.onRightClick)

    def _getButtonId(self, x, y):
        """ 
        find the (actual) position of the button relative to the
        canvas scrollregion-start, not just the viewing region,
        and return its tk canvas id
        """
        return self.canv.find_closest(self.canv.canvasx(x),
                self.canv.canvasy(y))

    def rightDefaultApp(self):
        " Open the image in system native image viewer "
        import webbrowser
        canvId = self._getButtonId(event.x, event.y)
        webbrowser.open(self.idFileDict[canvId])

    def rightDelete(self):
        " Delete the selected image "
        canvId = self._getButtonId(event.x, event.y)
        # may use send2trash to delete to recycle bin
        os.unlink(self.idFileDict[canvId])

    def rightDeleteAll(self):
        " Delete the all downloaded images "
        for filename in self.idFileDict.values():
            os.unlink(filename)

    def createThumbnailOnCanvas(self):
        " Create a thumbnail entry on canvas viewer "
        thumbTuple = self.makeThumb(self.imgfilename)
        # create imagebutton
        thumbPhoto = PhotoImage(thumbTuple.obj)
        handler = lambda: ImageOpener(self.canv, 
                          thumbTuple.path).mainloop()
        imgButtonWidth, imgButtonHeight = thumbTuple.width, thumbTuple.height
        imgButton = Button(self.canv, command=handler, image=thumbPhoto,
                    width=imgButtonWidth, cursor='hand2')
        imgButton.pack(fill=BOTH)
        buttonID = self.canv.create_window(self.xoffset, self.yoffset, 
                    window=imgButton, width=imgButtonWidth, 
                    height=imgButtonHeight, anchor=NW)

        self.idFileDict[buttonID] = thumbTuple.path
        self.canv.tag_bind(buttonID, '<Button-3>', self.onRightClick)
        self.thumbsaves.append(thumbPhoto)

        self.xoffset += imgButtonWidth
        self.canv.config(scrollregion =
                (0, 0, self.canvsize[0], self.yoffset))
        # save room for one image button to prevent clipping
        insertUptoCanvasWidth = self.canvsize[0] - imgButtonWidth
        if self.xoffset > insertUptoCanvasWidth:        # if width exceeds canvas
            self.yoffset += imgButtonHeight             # reset col offset and increase
            guiLogger.debug(f'{self.xoffset = }, {self.yoffset = }') # row offset, increase
            self.xoffset = 0                            # scrollregion accordingly

    def makeDownloadButton(self):
        " Create the download button for the gui downloader "
        def handler():
            inputs = self.guiInput.getValues()
            if inputs:
                threading.Thread(
                    target=self.startDownload, 
                    args=(inputs.searchKey,
                        inputs.imageNum, inputs.dirname)
                ).start()

        Button(self, text='Start', command=handler).pack(side=BOTTOM)

    @staticmethod
    def makeThumb(imgPath, thumbsize=(90,60), cachedir='.cache', enableCache=True):
        """
        Create thumbnail of the given image path and return
        a named tuple of (imgpath, imgobj, width, height) resized to given size;
        thumbsize is a tuple containing (width, height) of thumbnail
        """
        Thumb = namedtuple('Thumb', ['path', 'obj', 'width', 'height'])

        cachedir = os.path.join(os.path.dirname(imgPath), cachedir)
        os.makedirs(cachedir, exist_ok=True)
        thumbNameSpec = '%(fname)s_thumb%(width)dx%(height)d%(ext)s'

        head, ext = os.path.splitext(os.path.basename(imgPath))
        thumbname = thumbNameSpec % dict(
            fname=head, width=thumbsize[0], height=thumbsize[1], ext=ext,
        )
        thumbpath = os.path.join(cachedir, thumbname)
        guiLogger.debug(f'{thumbpath = }')

        # if cache exists
        if os.path.exists(thumbpath):
            thumbObj = Image.open(thumbpath)
        # create cache
        else:
            try:
                thumbObj = Image.open(imgPath)
                thumbObj.thumbnail(thumbsize, Image.ANTIALIAS)
                if enableCache:
                    thumbObj.save(thumbpath)
            except Exception as exc:
                guiLogger.error(f'Error creating thumbnail: {imgPath}'
                                f'\nTraceback Details: {str(exc)}')
                return None
        # Path to original file and resized thumbnail image object
        return Thumb(path=imgPath, obj=thumbObj,
                     width=thumbObj.width,
                     height=thumbObj.height)

