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
        self.surl = url # Source URL
        self.links = []
        if content:
            self.parse(content)

    def get_links(self):
        return self.links

    def parse(self, content):
        """Parse Web Page Source"""
        for match in _regex['href'].finditer(content):
            url = link = match.group(1)
            p = urlparse.urlparse(link)
            if p.scheme != 'http' and p.scheme != 'https': # scheme would be empty for partial URL
                if p.scheme: # Don't Allow any other protocols
                    continue
                elif p.path and not p.fragment:
                    # Relative URL from current page (will also take care of url starts with /)
                    url = urlparse.urljoin(self.surl, link)                    

            if url not in self.links:
                self.links.append(url)
