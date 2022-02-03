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

import os, sys, logging, time
import threading, requests, bs4
from exceptions import MainPageError, ImageDownloadError
from logger import mainlogger

downloadLogger = logging.getLogger('main.download')

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
    chunksize = 10000000
    # For current session (total)
    totalSize = 0
    totalDownloads = 0

    # FIXME: NumPages and NumImages should be an exclusive choice
    def __init__(self, searchKey, numImages=10, numPages=5, downloadDir=os.getcwd()):
        " initialize attributes for object "
        self.downloadSession = requests.Session()
        self.downloadSession.headers.update(self.headers)
        self.reset(searchKey, numPages, downloadDir)

    def reset(self, searchKey, numPages, downloadDir):
        " reset settings for different download config "
        self.searchKey = searchKey
        self.numImages = numImages
        self.numPages  = numPages

        # Make sure download dir exists
        os.makedirs(downloadDir, exist_ok=True)
        self.downloadDir   = downloadDir
        # For current run
        self.numDownloaded = 0
        self.lastDownloadTime = None

    def startDownload(self): 
        " toplevel method for starting download "
        start = time.time()
        ImgPerPage   = 30
        ImgPerThread = 5

        imgList = []
        #for imgname, imglink in self.fetchLinks(se

        self.lastDownloadTime = time.time() - start
        self.totalDownloads += self.numDownloaded
    
    def downloadSq(self, imgList):
        """ 
        Target Function for threading 
        Downloads sequentially without threading
        """
        for imgname, imglink in imgList:
            self.downloadImage(imglink, imgname)

    def downloadImage(self, link, name=None):
        " download given image link "
        if name is None:
            name = os.path.basename(link).rstrip('.jpg')
        try:
            image = self.downloadSession.get(link)
            image.raise_for_status()
        except Exception as exc:
            raise ImageDownloadError(link, exc)

        imgfilename = os.path.join(self.downloadDir, name + '.jpg')
        downloadLogger.info(f'{imgfilename = }')
        with open(imgfilename, 'wb') as imgfile:
            for chunk in image.iter_content(self.chunksize):
                imgfile.write(chunk)
        self.numDownloaded += 1

    def fetchLinks(self, start, stop=None, step=1):
        """ 
        Generate the image links for pages start to stop (non-inclusive)
        Optional: Stop: if not given, scrape links for start page only,
                  Step: default 1, can travel backwards if given negative value 
        """
        if stop is None:
            stop = start + 1
        downloadLogger.info(f'{start = }, {stop = }, {step = }')
        for pageNum in range(start, stop, step):
            # fetch page
            pageUrl  = self.queryStr % dict(searchKey = self.searchKey, pageNo = pageNum);  downloadLogger.info(f'{pageUrl = }')
            try:
                pageResponse = self.downloadSession.get(pageUrl)
                pageResponse.raise_for_status()
            except Exception as exc:
                raise MainPageError(pageNum, exc)
            # parse and get the image links
            mainPageSoup = bs4.BeautifulSoup(pageResponse.text, 'lxml')
            imageTags = mainPageSoup.select('img.img-responsive');                 downloadLogger.debug(f'{pageUrl = } {len(imageTags) = }')
            # generate imagename, imagelink for every image found
            for imageTag in imageTags:
                imageName = imageTag.get('alt').rstrip(' HD Wallpaper | Background Image')[:50]
                imageLink = imageTag.get('src').replace('thumbbig-', '')
                yield imageName, imageLink
            
if __name__ == '__main__':
    AlphaDownloader('ironman').startDownload()

