"""
 This module contains all the required backend stuff (logic)
 required to handle and download from the wallpaper website.

 URL signature looks like:
 https://wall.alphacoders.com/search.php?search={searchKey}&page={PageNo}
 The website may internally store some popular keywords like 'spiderman'
 in collections and serve them with collection ids, need to look out for those
 variations.

"""

import os, sys, logging, time
import threading, requests, bs4
from logger import mainlogger
from exceptions import (InvalidDownloadNum, MaxRetriesCrossed,
                SearchReturnedNone)

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
    prefixes = ('Movie ', 'Video ', 'Comics ', 'TV Show ')
    chunksize = 10000000
    # For current session (total)
    totalSize = 0
    totalDownloads = 0
    printFormat = ("Current Run :\n"
                  "Images Downloaded : %(numDownloaded)d, Time taken: %(lastDownloadTime)d secs\n"
                  "Number of Pages   : %(numPages)d, Downloaded: %(downloadSize).3f MB\n\n"
                  "Session Details:\n"
                  "Total Images   : %(totalDownloads)d, Total Size: %(totalSize).3f MB\n")

    def __init__(self, trace=False):
        " initialize attributes for object "
        self.imageMetaDict = dict()
        self.trace = trace
        self.mutex = threading.Lock()
        self._queryStrServed = None
        self.downloadSession = requests.Session()
        self.downloadSession.headers.update(self.headers)

    def startDownload(self, 
                      searchKey, 
                      numImages, 
                      downloadDir  = os.curdir, 
                      maxretries   = 2, 
                      imgPerThread = 5):
        """ 
        toplevel method for starting download, handle and check actual
        download success 
        """
        # PreDownload Hooks
        if numImages <= 0:
            raise InvalidDownloadNum

        # Make sure download dir exists
        os.makedirs(downloadDir, exist_ok=True)
        downloadLogger.info(f'{downloadDir = }')
        self.downloadDir = downloadDir

        # For current run
        self.searchKey = searchKey
        self.numImages = numImages
        self.numPages = 0
        self.numDownloaded = 0
        self.downloadSize  = 0
        self.lastDownloadTime = None

        MaxRetries = maxretries
        start = time.time()
        self._queryStrServed = None   # query string returned by website
                                      # (may be collection id)
        retries = 0
        # Try until actual number of images downloaded is less than
        # given number; and retries is less than max retries
        while self.numDownloaded < self.numImages and retries < MaxRetries:
            self._runDownload(searchKey, imgPerThread)
            retries += 1

        self.lastDownloadTime = time.time() - start
        self.totalDownloads += self.numDownloaded
        self.sessionDict = dict(
                numDownloaded    = self.numDownloaded,
                lastDownloadTime = self.lastDownloadTime,
                numPages         = self.numPages,
                downloadSize     = self.bytesToMiB(self.downloadSize),
                totalDownloads   = self.totalDownloads,
                totalSize        = self.bytesToMiB(self.totalSize),
        )

        if self.trace:
            print('\n', ' Stats: '.center(50, '*'))
            print(self.printFormat % self.sessionDict)

        if retries >= MaxRetries and self.numDownloaded < self.numImages:
            raise MaxRetriesCrossed("Max Retries; check log for error details")

    def _downloadSq(self, imgList):
        " Target Function for threading "
        for imgname, imglink in imgList:
            self.downloadImage(imglink, imgname)

    def _runDownload(self, ImgPerThread=5):
        """
        Threaded Download Logic;
        Perform Download assuming every link works, doesn't check if the actual number of download
        satisfies the required number given
        Not to be invoked directly, use wrapper method startDownload()

        """
        threads  = []
        imgArg   = []
        finished = False
        imgLinksFetched = 0 

        while not finished:
            self.numPages += 1
            for imgTuple in self.fetchLinks(self.searchKey, self.numPages):
                if imgLinksFetched >= self.numImages:
                    finished = True
                else:
                    imgArg.append(imgTuple)
                # if length becomes equal to image per thread
                # or image links are fetched but not processed
                # (not a multiple of imgPerThread)
                if len(imgArg) == ImgPerThread \
                        or (finished and imgArg):
                    downloadLogger.info(f'{len(imgArg) = }')
                    downloadLogger.debug(f'{imgLinksFetched = }')
                    downloadLogger.debug(f'{self.numPages = }')

                    thread = threading.Thread(target=self._downloadSq, args=(imgArg,))
                    threads.append(thread)
                    thread.start()
                    imgArg = []
                imgLinksFetched += 1
                if finished: break    # break inner loop if download
                                      # number satisfied
        for thread in threads: thread.join()

    def downloadImage(self, link, name=''):
        " download given image link "
        # Use the trailing id of the image link: ('1149.jpg')
        # to make the image name truly unique
        imgfilename = os.path.join(self.downloadDir,
                            name + '_' + os.path.basename(link))

        # Abort Download (return) if:
        # 1) Filename exists,
        if os.path.exists(imgfilename):
            downloadLogger.warning(f'{imgfilename} exists; possible bug')
            return
        try:
            image = self.downloadSession.get(link)
            image.raise_for_status()
        # 2) Download error
        except Exception as exc:
            downloadLogger.error(f'Error saving image: {link}\n{str(exc)}')
            return

        # save downloaded image (try to delegate os-specific filename
        # restrictions to underlying platform by encoding filename)
        with open(imgfilename.encode(), 'wb') as imgfile:
            for chunk in image.iter_content(self.chunksize):
                imgfile.write(chunk)

        with self.mutex:
            imgSize = os.path.getsize(imgfilename)
            self.downloadSize  += imgSize
            self.totalSize     += imgSize
            self.numDownloaded += 1
            self.imageMetaDict[name] = link

        if self.trace:
            print(f'Downloaded: {name}...')
        self.imgfilename = imgfilename      # save filename for subclass

    def restoreMetadata(self, imageMetaDict, imgPerThread=5):
        " Download images from a previously saved name-image dict "
        imgList = [(name, link) for name, link in imageMetaDict.items()]
        threads = []
        while imgList:
            imgArg, imgList = imgList[:imgPerThread], imgList[imgPerThread:]
            thread = threading.Thread(target=self._downloadSq, args=(imgArg,))
            thread.start()
            threads.append(thread)
        for thread in threads: thread.join()
        msgb.showinfo(title='Imported', 
                      message='Previous session was successfully restored')

    def fetchLinks(self, searchKey, start=1, stop=None, step=1):
        """
        Generate the image links for pages start to stop (non-inclusive)
        Optional: Stop: if not given, scrape links for start page only,
                  Step: default 1, can travel backwards if given negative value
        """
        if stop is None:    # generate links for given page only
            stop = start + 1
        downloadLogger.info(f'{start = }, {stop = }, {step = }')
        for pageNum in range(start, stop, step):
            # construct page url, if first pass, use base query, else fetched
            # query string
            pageInfoDict = dict(searchKey=searchKey, pageNo=pageNum)
            pageUrl = self._queryStrServed + f'&page={pageNum}' \
                            if self._queryStrServed \
                            else self.queryStr % pageInfoDict
            downloadLogger.info(f'{pageUrl = }')
            # fetch page
            try:
                pageResponse = self.downloadSession.get(pageUrl)
                pageResponse.raise_for_status()
                downloadLogger.info(f'{pageResponse.status_code = }')
            except Exception as exc:
                downloadLogger.error(f'Error Downloading Page: {pageNum}\n{str(exc)}')
                continue
            # parse and get the image links
            mainPageSoup = bs4.BeautifulSoup(pageResponse.text, 'lxml')

            # get the served query string (may give a collection id for
            # selected keywords)
            if self._queryStrServed is None:
                try:
                    pageUrl = mainPageSoup.select('div.page_container')[0].get('data-url')
                except IndexError:
                    raise SearchReturnedNone("Target Not found") from None
                self._queryStrServed = pageUrl
            downloadLogger.debug(f'{pageUrl = }')

            # get the image elements with class='img-responsive'
            imageTags = mainPageSoup.select('img.img-responsive')
            downloadLogger.debug(f'{len(imageTags) = }')
            # generate imagename, imagelink for every image found
            for imageTag in imageTags:
                imageName = imageTag.get('alt').rstrip(' HD Wallpaper | Background Image')[:50]
                # strip unnecessary prefixes (if present)
                for prefix in self.prefixes:
                    if imageName.startswith(prefix):
                        imageName = imageName.lstrip(prefix)
                        break

                imageLink = imageTag.get('src').replace('thumbbig-', '')
                yield imageName, imageLink

    @staticmethod
    def bytesToMiB(sizeInBy):
        " Return size in bytes to MiB "
        return sizeInBy / (1024 * 1024)

