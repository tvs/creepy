# -*- coding: utf-8 -*-
"""
CS 453: Project 1 - Web Crawler
"""

import sys
import time

from Queue import Queue
import os
from threading import Thread
import urlparse
try: # Try using psyco JIT compilation!
    import psyco
    psyco.full()
except:
    pass

from Fetcher import Fetcher
from Parser import Parser
from RobotStorage import RobotStorage
from PageStorage import PageStorage

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
    def __init__(self, seeds, num_threads=1, threshold=0):
        self.threshold = int(threshold) # Max. Number of Pages to Crawl
        self.robotstorage = RobotStorage(__user_agent__)
        self.pagestorage = PageStorage()
        self.urllist = [] # List of URLs crawled or in queue
        self.frontier = Queue() # Crawler's Request Queue
        for n in range(num_threads): # Pool of Threads
            worker = Thread(target=self.crawl, args=(n, ))
            worker.setDaemon(True)
            worker.start()

        for link in seeds:
            self.queue_url(link)
        self.frontier.join()

    def crawl(self, tid):
        """Crawl given URL"""
        while True:
            try:
                url = self.frontier.get()
                if _verbose:
                    print "  Crawler #%d: %s" % (tid, url)

                robot = self.robotstorage.get_robot(url)
                if robot.is_allowed(url):
                    # Delay processing
                    d_time = robot.delay_remaining(time.time())
                    if d_time > 0:
                        if _verbose > 1:
                            print "\n###*** Delaying for %f seconds" % d_time
                        time.sleep(d_time)

                    # Update the last request time
                    robot.update_last_request(time.time())

                    # Download the Page
                    page = Fetcher(url, verbose=_verbose)
                    doc = page.get_content()
                    if doc:
                        self.pagestorage.store(url, doc)
                        # Parse Page for Links
                        p = Parser(url, doc)
                        links = p.get_links()
                        if _verbose > 1:
                            print "    # links on %s: %d" % (url, len(links))
                        for link in links:
                            self.queue_url(link)
                else:
                    if _verbose > 1:
                        print "*** URL not allowed:", url
            except:
                pass
            finally:
                self.frontier.task_done()

    def queue_url(self, url):
        """Add url to the queue for crawling"""
        if not (self.threshold > 0 and len(self.urllist) >= self.threshold):
            if url not in self.urllist and self.validate_url(url):
                self.urllist.append(url)
                self.frontier.put(url)

    def validate_url(self, url):
        """Validate given url"""
        u = urlparse.urlparse(url)
        return u.scheme in ['http', 'https'] and u.netloc and not u.fragment

class Watcher:
    """Watch for Signal and quit the program"""
    def __init__(self):
        self.child = os.fork()
        if self.child == 0:
            return
        else:
            self.watch()

    def watch(self):
        try:
            os.wait()
        except KeyboardInterrupt:
            print "Keyboard Interrupted, Quitting..."
            self.kill()
        sys.exit()

    def kill(self):
        try:
            os.kill(self.child, signal.SIGKILL)
        except OSError: pass

if __name__ == "__main__":
    import optparse
    parser = optparse.OptionParser(description="Web Crawler",
                                   usage="usage: %prog [options] <seedfile | seeds>",
                                   version=__version__)
    parser.add_option('-v', '--verbose', help="Verbose Output [default: %default]", action="count", default=_verbose)
    parser.add_option('-d', '--debug', help="Debug Mode [default: %default]", action="count", default=_debug)
    parser.add_option('-T', '--page_threshold', help="Max. number of pages to crawl [default: %default]", metavar="THRESHOLD", default=10)
    parser.add_option('-N', '--num_threads', help="Number of threads to use [default: %default]", metavar="NUM_THREADS", default=1)

    (options, args) = parser.parse_args()
    if not args:
        parser.print_help()
        sys.exit(1)

    _verbose = options.verbose
    _debug = options.debug
    Watcher() # Watch for Keyboard Interrupt

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
    c = Crawler(seeds, threshold=int(options.page_threshold), num_threads=int(options.num_threads))
    print "### Number of URLs crawled:", len(c.urllist)
