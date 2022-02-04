
"""
 This module contains all the required backend stuff (logic)
 required to handle and download from website.

 URL signature looks like:
 https://wall.alphacoders.com/search.php?search={searchKey}&page={PageNo}

"""

import os, sys, logging, time
import threading, requests, bs4
from exceptions import MainPageError, ImageDownloadError
from logger import mainlogger

downloadLogger = logging.getLogger('main.download')

"""
A Wallpaper Downloader Class for https://wall.alphacoders.com
"""
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

    def __init__(self, searchKey, numImages, downloadDir=os.curdir,
                       progressVar=None, currentVar=None, trace=False):
        " initialize attributes for object "
        self.downloadSession = requests.Session()
        self.downloadSession.headers.update(self.headers)
        self.reset(searchKey, numImages, downloadDir, progressVar, currentVar, trace)

    def reset(self, searchKey, numImages, downloadDir=os.curdir,
                       progressVar=None, currentVar=None, trace=False):
        " reset settings for different download config "
        self.searchKey = searchKey
        self.numImages = numImages
        self.progressVar = progressVar
        self.currentVar  = currentVar
        self.trace = trace

        # Make sure download dir exists
        os.makedirs(downloadDir, exist_ok=True)
        self.downloadDir   = downloadDir

        # For current run
        self.numPages = 0
        self.numDownloaded = 0
        self.lastDownloadTime = None

    def startDownload(self): 
        " toplevel method for starting download "
        start = time.time()
        ImgPerThread = 5
        
        imgArg = []
        threads = []
        self.numPages = 1
        while self.numDownloaded < self.numImages:
            for imgTuple in self.fetchLinks(self.numPages):
                if self.numDownloaded >= self.numImages: 
                    break
                imgArg.append(imgTuple)
                if len(imgArg) == ImgPerThread:
                    thread = threading.Thread(target=self.downloadSq, args=(imgArg,))
                    threads.append(thread)
                    thread.start()
                    imgArg = []
            self.numPages += 1

        for thread in threads: thread.join()

        self.lastDownloadTime = time.time() - start
        self.totalDownloads += self.numDownloaded

        if self.trace:
            print('\n', ' Statistics: '.center(50, '*'))
            print("Current Run:\n"
                  "Downloaded: %d, Time taken: %d secs\n"
                  "Number of Pages: %d\n"
                  "Session Details:\n"
                  "Total Downloads: %d, Total Size: %d\n"
                  % (self.numDownloaded, self.lastDownloadTime,
                  self.numPages, self.totalDownloads, self.totalSize))
    
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
            image = requests.get(link, headers = self.headers)
            #image = self.downloadSession.get(link)
            image.raise_for_status();                                   downloadLogger.info(f'{image.status_code = }')
        except Exception as exc:
            raise ImageDownloadError(link) from exc

        imgfilename = os.path.join(self.downloadDir, name + '.jpg')
        downloadLogger.info(f'{imgfilename = }')
        with open(imgfilename, 'wb') as imgfile:
            for chunk in image.iter_content(self.chunksize):
                imgfile.write(chunk)
        if self.trace:
            print(f'Downloaded: {name}...')
        self.numDownloaded += 1

    def fetchLinks(self, start, stop=None, step=1):
        """ 
        Generate the image links for pages start to stop (non-inclusive)
        Optional: Stop: if not given, scrape links for start page only,
                  Step: default 1, can travel backwards if given negative value 
        """
        if stop is None:    # generate links for one page only
            stop = start + 1
        downloadLogger.info(f'{start = }, {stop = }, {step = }')
        for pageNum in range(start, stop, step):
            # fetch page
            pageUrl  = self.queryStr % dict(searchKey = self.searchKey, pageNo = pageNum);  downloadLogger.info(f'{pageUrl = }')
            try:
                pageResponse = self.downloadSession.get(pageUrl)
                pageResponse.raise_for_status();                                   downloadLogger.info(f'{pageResponse.status_code = }')
            except Exception as exc:
                raise MainPageError(pageNum) from None
            # parse and get the image links
            mainPageSoup = bs4.BeautifulSoup(pageResponse.text, 'lxml')
            imageTags = mainPageSoup.select('img.img-responsive');                 downloadLogger.debug(f'{pageUrl = } {len(imageTags) = }')
            # generate imagename, imagelink for every image found
            for imageTag in imageTags:
                imageName = imageTag.get('alt').rstrip(' HD Wallpaper | Background Image')[:50]
                imageLink = imageTag.get('src').replace('thumbbig-', '')
                yield imageName, imageLink
            
if __name__ == '__main__':
    AlphaDownloader('ironman', 30, '/tmp/alphaWall', trace=True).startDownload()

