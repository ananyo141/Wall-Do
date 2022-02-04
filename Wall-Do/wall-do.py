# Entry Point

from downloader import AlphaDownloader
from logger import mainlogger
import logging

walldologger = logging.getLogger('main.walldo')
walldologger.debug('main module')
AlphaDownloader('ironman', 30, downloadDir = '/tmp/ironman').startDownload()

