"""
 This module contains all the required backend stuff (logic)
 required to handle and download from website.

 URL signature looks like:
 https://wall.alphacoders.com/search.php?search={searchKey}&page={PageNo}

"""

import os, sys, logging, time
import threading, requests, bs4
from logger import mainlogger
from exceptions import InvalidDownloadNum

# get module logger
downloadLogger = logging.getLogger('main.downloader')

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

    def __init__(self, searchKey, numImages, downloadDir=os.curdir, trace=False):
        " initialize attributes for object "
        self.downloadSession = requests.Session()
        self.downloadSession.headers.update(self.headers)
        self.reset(searchKey, numImages, downloadDir, trace)

    def reset(self, searchKey, numImages, downloadDir=os.curdir, trace=False):
        " reset settings for different download config "
        if numImages <= 0:
            raise InvalidDownloadNum

        self.searchKey = searchKey;                         downloadLogger.info(f'{self.searchKey = }')
        self.numImages = numImages;                         downloadLogger.info(f'{self.numImages = }')
        self.trace = trace

        # Make sure download dir exists
        os.makedirs(downloadDir, exist_ok=True);            downloadLogger.info(f'{downloadDir = }')
        self.downloadDir = downloadDir

        # For current run
        self.numPages = 0
        self.numDownloaded = 0
        self.downloadSize  = 0
        self.lastDownloadTime = None

    """
    ********************* Stats: *********************
    Current Run:
    Downloaded: 112, Time taken: 55 secs
    Number of Pages: 11, Downloaded: 112.000000 MB

    Session Details:
    Total Downloads: 289, Total Size: 289.585 MB
    """
    # FIXME: downloading beyond given limit
    # FIXME: duplicate downloads
    def startDownload(self):
        " toplevel method for starting download "
        start = time.time()
        ImgPerThread = 5

        threads = []
        imgArg  = []
        self.numPages = 1
        while self.numDownloaded < self.numImages:
            for imgTuple in self.fetchLinks(self.numPages):
                if self.numDownloaded >= self.numImages:
                    break
                imgArg.append(imgTuple)
                if len(imgArg) == ImgPerThread:
                    thread = threading.Thread(target=self.downloadSq, args=(imgArg,))
                    threads.append(thread)
                    thread.start();             downloadLogger.info(f'{len(imgArg) = }')
                    imgArg = []
            self.numPages += 1

            downloadLogger.debug(f'{self.numDownloaded = }')
            downloadLogger.debug(f'{self.numDownloaded < self.numImages = }')
            downloadLogger.info(f'{self.numPages = }')

        for thread in threads: thread.join()
        self.lastDownloadTime = time.time() - start
        self.totalDownloads += self.numDownloaded

        if self.trace:
            print('\n', ' Stats: '.center(50, '*'))
            print("Current Run:\n"
                  "Downloaded: %d, Time taken: %d secs\n"
                  "Number of Pages: %d, Downloaded: %f MB\n\n"
                  "Session Details:\n"
                  "Total Downloads: %d, Total Size: %.3f MB\n"
                  % (self.numDownloaded, self.lastDownloadTime,
                     self.numPages, self.bytesToMiB(self.downloadSize),
                     self.totalDownloads, self.bytesToMiB(self.totalSize)))

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
            image.raise_for_status();                                   downloadLogger.info(f'{image.status_code = }')
        except Exception as exc:
            downloadLogger.critical(f'Error saving image: {link}\n{str(exc)}')
            return

        imgfilename = os.path.join(self.downloadDir, name + '.jpg');    downloadLogger.info(f'{imgfilename = }')
        if os.path.exists(imgfilename):
            downloadLogger.warning(f'{imgfilename} already exists; possible bug')
            return

        #assert not os.path.exists(imgfilename), "Attempt to download existing image"

        with open(imgfilename, 'wb') as imgfile:
            for chunk in image.iter_content(self.chunksize):
                imgfile.write(chunk)

        imgSize = os.path.getsize(imgfilename)
        self.downloadSize  += imgSize
        self.totalSize     += imgSize
        self.numDownloaded += 1

        if self.trace:
            print(f'Downloaded: {name}...')

    def fetchLinks(self, start, stop=None, step=1):
        """
        Generate the image links for pages start to stop (non-inclusive)
        Optional: Stop: if not given, scrape links for start page only,
                  Step: default 1, can travel backwards if given negative value
        """
        if stop is None:    # generate links for given page only
            stop = start + 1
        downloadLogger.info(f'{start = }, {stop = }, {step = }')
        for pageNum in range(start, stop, step):
            # fetch page
            pageUrl  = self.queryStr % dict(searchKey = self.searchKey, pageNo = pageNum);  downloadLogger.info(f'{pageUrl = }')
            try:
                pageResponse = self.downloadSession.get(pageUrl)
                pageResponse.raise_for_status();                                   downloadLogger.info(f'{pageResponse.status_code = }')
            except Exception as exc:
                downloadLogger.critical(f'Error Downloading Page: {pageNum}\n{str(exc)}')
                continue
            # parse and get the image links
            mainPageSoup = bs4.BeautifulSoup(pageResponse.text, 'lxml')
            # get the image elements with class='img-responsive'
            imageTags = mainPageSoup.select('img.img-responsive');                 downloadLogger.debug(f'{len(imageTags) = }')
            # generate imagename, imagelink for every image found
            for imageTag in imageTags:
                imageName = imageTag.get('alt').rstrip(' HD Wallpaper | Background Image')[:50]
                imageLink = imageTag.get('src').replace('thumbbig-', '')
                yield imageName, imageLink

    @staticmethod
    def bytesToMiB(sizeInBy):
        " Return size in bytes to MiB "
        return sizeInBy / (1024 * 1000)

"""
GUI oriented Downloader that updates status with tk variables
"""
def DownloaderWithVar(AlphaDownloader):
    def __init__(self, searchKey, numImages, downloadDir=os.curdir,
                       progressVar=None, currentVar=None):
        AlphaDownloader.__init__(searchKey, numImages, downloadDir, trace=False)
        self.reset(searchKey, numImages, downloadDir, progressVar, currentVar)

    def reset(self, searchKey, numImages, downloadDir=os.curdir,
                       progressVar=None, currentVar=None):
        AlphaDownloader.reset(self, searchKey, numImages, downloadDir, trace=False)
        self.progressVar = progressVar
        self.currentVar  = currentVar

    def downloadImage(self, link, name=None):
        AlphaDownloader.downloadImage(self, link, name)
        if self.progressVar:
            self.progressVar.set((self.numDownloaded // self.numImages) * 100)
        if self.currentVar:
            self.currentVar.set(f'Downloaded {link}...')

if __name__ == '__main__':
    AlphaDownloader('ironman', 30, '/tmp/alphaWall', trace=True).startDownload()

