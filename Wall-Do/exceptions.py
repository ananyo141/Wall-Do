# General Exception Classes for downloader

class DownloadError(Exception):
    def __init__(self, message, exc):
        self.exception = exc
        DownloadError.__init__(self, message)

    def __str__(self):
        return f'{self.message}\nError Code: {str(self.exception)}'

class MainPageError(DownloadError):
    " hit exception while requesting main page "
    def __init__(self, exception):
        DownloadError.__init__(self, "Unable to fetch Main Page", exception)

class ImageDownloadError(DownloadError):
    " hit exception while downloading image "
    def __init__(self, exception):
        DownloadError.__init__(self, "Error while downloading image", exception)

