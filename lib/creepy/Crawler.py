# -*- coding: utf-8 -*-
"""
CS 453: Project 1 - Web Crawler
"""

import sys
import time
import os
import re
try: # Try using psyco JIT compilation!
    import psyco
    psyco.full()
except:
    pass

from Fetcher import Fetcher
from Parser import Parser
from RobotStorage import RobotStorage

__version__ = "0.1"
__authors__ = "Travis Hall <trvs.hll@gmail.com>, Brittany Miller ‎<miller317@gmail.com>‎ and Bhadresh Patel <bhadresh@wsu.edu>"
__date__ = "Sep 5, 2010"
__user_agent__ = "creepy"

_verbose = False
_debug = False

class Crawler:
    def __init__(self, seed, threshold=0):
        self.crawled = [] # Already Crawled URLs
        self.queue = [] # Crawl Queue
        self.threshold = int(threshold) # Max. Number of Pages to Crawl
        self.robotstorage = RobotStorage(__user_agent__)
        for url in seed:
            self.queue_url(url)

    def crawl(self):
        """From the current queue start crawling pages"""
        url = self.get_next_url()
        while url != None:
            if self.robotstorage.is_allowed(url):
                if _verbose > 2:
                    print "  Crawling:", url
                self.crawled.append(url)
                page = Fetcher(url)
                doc = page.get_content()
                p = Parser(url, doc)
                links = p.get_links()
                print "    # links found: ", len(links)
                self.queue_links(links)

                # Next
                if self.threshold > 0 and len(self.crawled) >= self.threshold:
                    if _verbose > 2:
                        print "\n###*** Quitting... Threshold reached:", self.threshold, "***###\n"
                    url = None
                else:
                    url = self.get_next_url()
                
            else:
                if _verbose > 2:
                    print "*** URL not allowed:", url
                url = self.get_next_url()
    

    def get_next_url(self):
        """Get Next url from the queue"""
        return self.queue.pop(0) if len(self.queue) > 0 else None

    def queue_url(self, url):
        """
        Add url to the queue for crawling

        @TODO: Add logic to verify url syntax & discard invalid url
        """
        if url not in self.crawled:
            self.queue.append(url)

    def queue_links(self, links):
        """
        Add links to the queue for crawling

        @TODO: Add logic to make link into URL
        """
        for link in links:
            self.queue_url(link)

if __name__ == "__main__":
    import optparse
    parser = optparse.OptionParser(description="Web Crawler",
                        usage="usage: %prog [options] <seedfile | seedurls>",
                        version=__version__)
    parser.add_option('-v', '--verbose', help="Verbose Output [default: %default]", action="count", default=_verbose)
    parser.add_option('-d', '--debug', help="Debug Mode [default: %default]", action="count", default=_debug)
    parser.add_option('-T', '--page_threshold', help="Max. number of pages to crawl [default: %default]", metavar="THRESHOLD", default=10)

    (options, args) = parser.parse_args()
    if not args:
        parser.print_help()
        sys.exit(1)

    _verbose = options.verbose
    _debug = options.debug

    seed = []
    for arg in args:
        if os.path.isfile(arg):
            fp = open(args[0], "r")
            fcontent = fp.read()
            fp.close()
            seed.extend(fcontent.splitlines())
        else:
            seed.append(arg)

    if len(seed) == 0:
        print "Please provide Seed URL or File that contains seed urls"
        parser.print_help()
        sys.exit(1)

    print "### Number of seed URLs:", len(seed)
    c = Crawler(seed, options.page_threshold)
    c.crawl()
    print "### Number of URLs crawled:", len(c.crawled)
    print "### Number of URLs pending:", len(c.queue)
