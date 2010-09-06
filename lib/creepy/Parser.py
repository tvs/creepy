"""
Parser.py

Parse HTML Source
"""

import re
import urlparse

_regex = {
    'href': re.compile(r'<a\s.*?href="(.*?)".*?>', re.I)
}
class Parser:
    def __init__(self, url, content):
        self.surl = urlparse.urlparse(url)
        self.links = []
        try:
            self.parse(content)
        except:
            pass

    def get_links(self):
        return self.links

    def parse(self, content):
        # Find Links
        for match in _regex['href'].finditer(content):
            url = link = match.group(1)
            p = urlparse.urlparse(link)
            if p.scheme != 'http' and p.scheme != 'https':
                if p.scheme: # Don't Allow any other protocols
                    continue
                else:
                    if p.path.startswith('/'):
                        url = self.surl.scheme + '://' + self.surl.netloc + p.path
                    else:
                        # @TODO: Deal with relative URLs
                        continue

            if url not in self.links:
                self.links.append(url)
