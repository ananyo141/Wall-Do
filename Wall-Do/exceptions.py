# General Exception Classes for downloader

class DownloadError(Exception):
    def __init__(self, message, exc):
        self.exception = exc
        DownloadError.__init__(self, message)

    def __str__(self):
        return f'{self.message}\nError Code: {str(self.exception)}'

class MainPageError(DownloadError):
    " hit exception while requesting main page "
    def __init__(self, pageNum, exception):
        DownloadError.__init__(self, f"Unable to fetch main page {pageNum}", exception)

class ImageDownloadError(DownloadError):
    " hit exception while downloading image "
    def __init__(self, imageLink, exception):
        DownloadError.__init__(self, f"Error while downloading image: {imageLink}", exception)

