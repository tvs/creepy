# -*- coding: utf-8 -*-
"""
CS 453: Project 1 - Web Crawler
"""

import sys
import time
import signal
from Queue import Queue
import os
import threading
import urlparse
import re
try: # Try using psyco JIT compilation!
    import psyco
    psyco.full()
except:
    pass

from Fetcher import Fetcher
from Parser import Parser
from RobotStorage import RobotStorage
from PageStorage import PageStorage

__version__ = "1.0"
__authors__ = "Travis Hall <trvs.hll@gmail.com>, Brittany Miller <miller317@gmail.com> and Bhadresh Patel <bhadresh@wsu.edu>"
__date__ = "Sep 5, 2010"
__user_agent__ = "creepybot"

_debug = False

class Crawler:
    """
    A simple Web Crawler
    """
    def __init__(self, seeds, store_loc, num_threads=1, threshold=0, verbose=False):
        self.verbose = verbose
        self.threshold = int(threshold) # Max. Number of Pages to Crawl
        self.robotstorage = RobotStorage(__user_agent__)
        self.pagestorage = PageStorage({'store_location': store_loc})
        self.urllist = [] # List of URLs crawled or in queue
        self.frontier = Queue() # Crawler's Request Queue
        self.watcher = Watcher() # Watch for Keyboard Interrupt
        self._pagesstored = 0 # Number of pages stored
        self._lock = threading.Lock()
        for n in range(num_threads): # Pool of Threads
            worker = threading.Thread(target=self.crawl, args=(n, ))
            worker.setDaemon(True)
            worker.start()

        for link in seeds:
            self.queue_url(link)
        self.frontier.join()

    def crawl(self, tid):
        """Crawl given URL"""
        while True:
            try:
                if self.threshold > 0 and self._pagesstored + 1 > self.threshold:
                    print "### Number of URLs crawled:", self._pagesstored
                    self.watcher.kill()
                    break

                url = self.frontier.get()
                if self.verbose:
                    print "  Crawler #%d: %s" % (tid, url)

                robot = self.robotstorage.get_robot(url)
                if robot.is_allowed(url):
                    # Delay processing
                    d_time = robot.delay_remaining(time.time())
                    if d_time > 0:
                        if self.verbose > 1:
                            print "\n###*** Delaying for %f seconds" % d_time
                        time.sleep(d_time)

                    # Update the last request time
                    robot.update_last_request(time.time())

                    # Download the Page
                    page = Fetcher(url, verbose=self.verbose)
                    doc = page.get_content()
                    if doc:
                        self.pagestorage.store(url, doc)
                        self._lock.acquire()
                        try:
                            self._pagesstored = self._pagesstored + 1
                        finally:
                            self._lock.release()

                        # Parse Page for Links
                        p = Parser(url, doc)
                        links = p.get_links()
                        if self.verbose > 1:
                            print "    # links on %s: %d" % (url, len(links))
                        for link in links:
                            self.queue_url(link)
                else:
                    if self.verbose > 1:
                        print "*** URL not allowed:", url
            finally:
                self.frontier.task_done()

    def queue_url(self, url):
        """Add url to the queue for crawling"""
        if url not in self.urllist and self.validate_url(url):
            self.urllist.append(url)
            self.frontier.put(url)

    def validate_url(self, url):
        """Validate given url - skip image/video/zip..."""
        u = urlparse.urlparse(url)
        if u.scheme in ['http', 'https'] and u.netloc and not u.fragment:
            return not re.search(r'(jpg|jpeg|gif|png|exe|msi|dmg|gz|zip|tar|mov|mpg|mp3|mp4)$', u.path, re.I)
        return False

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
