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

class InvalidDownloadNum(DownloadError):
    " invalid number of images to download "
    def __init__(self, num):
        DownloadError.__init__(self, f'Invalid number to download: {num}')

class MaxRetriesCrossed(DownloadError):
    " Maximum retries crossed and still failed to download all images "

class SearchReturnedNone(DownloadError):
    " Website returned none found for given search key "

# Exception Classes for GUI components
class GuiError(Exception):
    " Base Exception Class for GUI "

class TopLevelWidgetsOnly(GuiError):
    """ 
    Error class that require the widget to be
    passed to be a toplevel tk widget 
    """
