# -*- coding: utf-8 -*-
"""
CS 453: Project 1 - Web Crawler
"""

import sys
import time
import os
import re
import urlparse
try: # Try using psyco JIT compilation!
    import psyco
    psyco.full()
except:
    pass

from Fetcher import Fetcher
from Parser import Parser
from RobotStorage import RobotStorage

__version__ = "0.1"
__authors__ = "Travis Hall <trvs.hll@gmail.com>, Brittany Miller <miller317@gmail.com> and Bhadresh Patel <bhadresh@wsu.edu>"
__date__ = "Sep 5, 2010"
__user_agent__ = "creepybot"

_verbose = False
_debug = False

class Crawler:
    """
    A simple Web Crawler
    """
    def __init__(self, seeds, threshold=0):
        self.crawled = [] # Already Crawled URLs
        self.frontier = [] # Crawler Request Queue
        self.threshold = int(threshold) # Max. Number of Pages to Crawl
        self.robotstorage = RobotStorage(__user_agent__)
        for url in seeds:
            self.queue_url(url)

    def crawl(self):
        """From the current queue start crawling pages"""
        url = self.get_next_url()
        while url != None:
            if _verbose:
                print "  Crawling:", url
            robot = self.robotstorage.get_robot(url)
            if robot.is_allowed(url):                
                # Delay processing
                d_time = robot.delay_remaining(time.time())
                if d_time > 0:
                    if _verbose > 1:
                        print "\n###*** Delaying for %f seconds" % d_time
                    time.sleep(d_time)
                
                self.crawled.append(url)
                
                # Update the last request time
                robot.update_last_request(time.time())
                
                # Download the Page
                page = Fetcher(url, verbose=_verbose)
                doc = page.get_content()                
                if doc:
                    # @TODO: Store Document
                    
                    # Parse Page for Links
                    p = Parser(url, doc)
                    links = p.get_links()
                    if _verbose:
                        print "    # links found: ", len(links)
                    self.queue_links(links)
            else:
                if _verbose > 1:
                    print "*** URL not allowed:", url
            
            # Get Next URL
            if self.threshold > 0 and len(self.crawled) >= self.threshold:
                if _verbose:
                    print "\n###*** Quitting... Threshold reached:", self.threshold, "***###\n"
                url = None
            else:
                url = self.get_next_url()

    def get_next_url(self):
        """Get Next url from the queue"""
        return self.frontier.pop(0) if len(self.frontier) > 0 else None

    def queue_url(self, url):
        """Add url to the queue for crawling"""
        if url not in self.crawled and self.validate_url(url):
            self.frontier.append(url)

    def queue_links(self, links):
        """Add links to the queue for crawling"""
        for link in links:
            self.queue_url(link)

    def validate_url(self, url):
        """Validate given url"""
        u = urlparse.urlparse(url)
        return u.scheme in ['http', 'https'] and u.netloc and not u.fragment
        
if __name__ == "__main__":
    import optparse
    parser = optparse.OptionParser(description="Web Crawler",
                        usage="usage: %prog [options] <seedfile | seeds>",
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

    seeds = []
    for arg in args:
        if os.path.isfile(arg):
            fp = open(args[0], "r")
            fcontent = fp.read()
            fp.close()
            seeds.extend(fcontent.splitlines())
        else:
            seeds.append(arg)

    if len(seeds) == 0:
        print "Please provide Seed URL or File that contains seed urls"
        parser.print_help()
        sys.exit(1)

    print "### Number of seeds:", len(seeds)
    c = Crawler(seeds, options.page_threshold)
    c.crawl()
    print "### Number of URLs crawled:", len(c.crawled)
    print "### Number of URLs pending:", len(c.frontier)
