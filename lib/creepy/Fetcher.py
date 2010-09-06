"""
Fetcher.py

Connect to domain and request content
"""

import sys
import urllib2
_headers = {"User-Agent": "wsubot"}

class Fetcher:
    def __init__(self, url):
        self.url = url

    def add_headers(self, request):
        for key,value in _headers.iteritems():
            request.add_header(key, value)

    def get_content(self):
        content = None
        try:
            request = urllib2.Request(self.url)
            handle = urllib2.build_opener()
            self.add_headers(request)
            content = handle.open(request).read()
        except urllib2.HTTPError, e:
            print >> sys.stderr, "*** Error:", e
        except urllib2.URLError, e:
            print >> sys.stderr, "*** Error: Invalid URL:", e
        except:
            print >> sys.stderr, "*** Error: Could not open url:", self.url
        return content
