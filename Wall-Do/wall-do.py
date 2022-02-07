# Entry Point

from downloader import AlphaDownloader
from logger import mainlogger
import logging

walldologger = logging.getLogger('main.walldo')
walldologger.debug('main module')
AlphaDownloader('iron man', 50, downloadDir = '/tmp/alphaWall/IronMan', trace=True).startDownload()

