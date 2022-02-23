#!/usr/bin/env python3

# Entry Point For the Wall-Do

import os, sys, logging, json, threading, time
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as msgb, filedialog as fldg
import gui_components as guiC
from downloader import AlphaDownloader, GuiDownloader
from exceptions import SearchReturnedNone

from logger import mainlogger
walldologger = logging.getLogger('main.walldo')
walldologger.info('Entry Point: Wall-Do')

class MakeMenuHandlers(guiC.MakeMenu):
    def __init__(self, *args, downloaderObj=None, **kw):
        guiC.MakeMenu.__init__(self, *args, **kw)
        self.downloaderObj = downloaderObj
    
    def config(downloader):
        self.downloaderObj = downloader

    def importFile(self):
        """
        Get a json filename from the user and save a dict of image names
        and links to self dict reference if entered
        """
        imgMetaFile = fldg.askopenfile(title='Enter Import Data',
                                       filetypes=(('JSON Metadata', '*.json'),
                                                  ('All', '*')))
        if not imgMetaFile:
            msgb.showerror(title='No Files Imported', 
                           message='Please enter metadata from a previous run')
        else:
            try:
                imageMetaDict = json.load(imgMetaFile)
            except json.decoder.JSONDecodeError:
                msgb.showerror(title='Invalid File', 
                               message='Parse Error, is it a valid json file?')
            else:
                self.downloaderObj.restoreMetadata(imageMetaDict)


    def exportFile(self):
        " Save the download metadata dictionary to a given file "
        from datetime import datetime as dt
        imgMetaFile = fldg.asksaveasfile(defaultextension='.json',
                initialfile=f'WallDoData_({dt.now().strftime("%d-%m-%Y_%H:%M:%S")})',
                filetypes=(('JSON Metadata', '*.json'), ('All', '*')))
        if imgMetaFile:
            json.dump(self.downloaderObj.imageMetaDict, imgMetaFile, indent=4)
            msgb.showinfo(title='Success', message='Saved session metadata as '
                          f"'{imgMetaFile.name}'")

    def pingEdit(self):
        " Ping the site for links for a single page and return status "
        startTime = time.perf_counter_ns()
        self.downloaderObj.fetchLinks(1)
        msgb.showinfo(title='Ping', message='Website pinged in '
                      f'{time.perf_counter_ns() - startTime} ns')

def interactive():
    """
    Handle commandline arguments if invoked as commandline tool
    """
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('searchKey',           help='Search String')
    parser.add_argument('-n', '--number',      help='Number of wallpapers to download', default=30, type=int)
    parser.add_argument('-t', '--threads',     help='Number of images per thread',      default=5,  type=int)
    parser.add_argument('-d', '--downloadDir', help='Save Directory',                   default=None)

    args = parser.parse_args()
    downloadDir = args.search if args.downloadDir is None else args.downloadDir
    try:
        AlphaDownloader(args.searchKey, args.number, downloadDir, trace=True).startDownload(args.threads)
    except SearchReturnedNone:
        sys.exit(f"No Images found for {args.search}")

def makeGUI():
    """
    Handle the gui if invoked without any arguments
    """
    def startDownloadHandler():
        def updateCanv():
            while True:
                guiC.GuiImgViewer(root, inputs.dirname).pack()
                time.sleep(0.5)
        inputs = guiInpFrame.getValues()
        walldologger.debug(f'{inputs = }')
        if inputs:
            downloaderObj.reset(searchKey=inputs.searchKey, numImages=inputs.imageNum,
                downloadDir=inputs.dirname)
            threading.Thread(target=downloaderObj.startDownload, args=()).start()
            threading.Thread(target=updateCanv, args=()).start()

    root = tk.Tk()
    root.title('Wall-Do! - A Wallpaper Downloader')
    root.geometry('400x650')
    root.protocol('WM_DELETE_WINDOW', lambda: sys.exit(0))

    # Place Menu
    # Place Input Fields
    guiInpFrame = guiC.GuiInput(root)
    guiInpFrame.pack()
    # Place Detail Fields
    detailsFrame = guiC.GuiDetails(root)
    downloaderObj = GuiDownloader(sessionVar=detailsFrame.sessionVar, 
        progressVar=detailsFrame.progressVar, currentVar=detailsFrame.currentVar)
    menu = MakeMenuHandlers(root, downloaderObj=downloaderObj)
    detailsFrame.pack(expand=True) #, fill='both')
    # Place Viewer
    ttk.Button(root, text='Start Download', command=startDownloadHandler).pack(pady=8)
    tk.mainloop()

if __name__ == '__main__':
    if len(sys.argv) > 1: interactive()
    else: makeGUI()

