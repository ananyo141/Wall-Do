#!/usr/bin/env python3

# Entry Point For the Wall-Do

import os, sys, logging
from downloader import AlphaDownloader

from logger import mainlogger
walldologger = logging.getLogger('main.walldo')
walldologger.info('Entry Point: Wall-Do')
import exceptions as exp

def interactive():
    """
    Handle commandline arguments if invoked as commandline tool

    """
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('searchKey',           help='Search String')
    parser.add_argument('-n', '--number',      help='Number of wallpapers to download', default=30, type=int)
    parser.add_argument('-t', '--threads',     help='Number of images per thread',      default=5,  type=int)
    parser.add_argument('-d', '--downloadDir', help='Save Directory',                   default=None)

    args = parser.parse_args()
    downloadDir = args.search if args.downloadDir is None else args.downloadDir
    try:
        AlphaDownloader(args.searchKey, args.number, downloadDir, trace=True).startDownload(args.threads)
    except exp.SearchReturnedNone:
        sys.exit(f"No Images found for {args.search}")

def makeGUI():
    raise NotImplementedError

def main():
    """
    Driver Function
    """
    if len(sys.argv) > 1:
        interactive()
    else:
        makeGUI()

if __name__ == '__main__':
    main()

