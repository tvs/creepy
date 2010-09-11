"""
Fetcher.py

Connect to domain and request content
"""

import sys
import urllib2
_headers = {"User-Agent": "creepybot"}

class Fetcher:
    def __init__(self, url, verbose=False):
        self.url = url
        self.response = None
        try:
            request = urllib2.Request(self.url)
            handle = urllib2.build_opener()
            self.add_headers(request)
            self.response = handle.open(request)
        except urllib2.HTTPError, e:
            if verbose > 2:
                print >> sys.stderr, "*** Error:", e
        except urllib2.URLError, e:
            if verbose > 2:
                print >> sys.stderr, "*** Error: Invalid URL:", e
        except:
            if verbose > 2:
                print >> sys.stderr, "*** Error: Could not open url:", self.url

    def add_headers(self, request):
        for key, value in _headers.iteritems():
            request.add_header(key, value)

    def get_content(self):
        content = None
        try:
            if self.response:
                content = self.response.read()
        except:
            pass
        return content

    def get_response(self):
        return self.response


