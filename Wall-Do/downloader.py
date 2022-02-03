# This module contains all the required backend stuff (logic)
# required to handle and download from website.

# URL signature looks like:
# https://wall.alphacoders.com/search.php?search={searchKey}&page={PageNo}

"""
TODO:
For numpages, hit up the query string and scrape the page
Every Page will give a number of link tags, get them
Download the images with the links

"""

import os, sys, logging
import threading, requests, bs4
from exceptions import *

'''
A Wallpaper Downloader Class for https://wall.alphacoders.com
'''
class AlphaDownloader:
    queryStr = \
        'https://wall.alphacoders.com/search.php?search=%(searchKey)s&page=%(pageNo)d'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) ' 
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/72.0.3626.28 Safari/537.36'
    }
    # For current session (total)
    totalDownloads = 0
    totalTime = None

    def __init__(self, searchKey, numPages=5, downloadDir=os.getcwd()):
        " initialize attributes for object "
        self.reset(searchKey, numPages, downloadDir)

    def reset(self, searchKey, numPages, downloadDir):
        " reset settings for different download config "
        self.searchKey = searchKey
        self.numPages  = numPages

        # Make sure download dir exists
        os.makedirs(downloadDir, exist_ok=True)
        self.downloadDir   = downloadDir
        # For current run
        self.numDownloaded = 0
        self.lastDownloadTime = None

    def startDownload(self): 
        " toplevel method for starting download "
    
    def downloadImage(self, link, name=None):
        " download given image link "

    def downloadSq(self, start, stop, step):
        " Target Function for threading (Downloads sequentially) "

    def fetchLinks(self, start, stop=None, step=1):
        """ 
        Generate the image links for pages start to stop (non-inclusive)
        Optional: Stop: if not given, scrape links for start page only,
                  Step: default 1, can travel backwards if given negative value 
        """
        if stop is None:
            stop = start + 1

        for pageNum in range(start, stop, step):
            # fetch page
            pageUrl  = queryStr % dict(searchKey = self.searchKey, pageNo = pageNum)
            try:
                pageResponse = requests.get(pageUrl, headers = self.headers))
                pageResponse.raise_for_status()
            except Exception as exc:
                raise MainPageError(exc)

if __name__ == '__main__':
    AlphaDownloader('ironman').startDownload()

