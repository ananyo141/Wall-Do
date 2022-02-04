# General Exception Classes for downloader

class DownloadError(Exception):
    " Base Exception Class for Downloader "

class MainPageError(DownloadError):
    " hit exception while requesting main page "
    def __init__(self, pageNum):
        DownloadError.__init__(self, f"Unable to fetch main page {pageNum}")

class ImageDownloadError(DownloadError):
    " hit exception while downloading image "
    def __init__(self, imageLink):
        DownloadError.__init__(self, f"Error while downloading image: {imageLink}")

