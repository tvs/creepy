"""HTML Tag Stripper"""
import sys
import os
import re
from HTMLParser import HTMLParser

__version__ = "1.0"
__authors__ = "Bhadresh Patel <bhadresh@wsu.edu>"
__date__ = "Sep 23, 2010"

class Stripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

class TagStripper:
    """HTML Tag Stripper"""
    def __init__(self, indir=None, outdir=None, verbose=False):
        self.verbose = verbose
        self.startRM = re.compile(r'<(!\s*--|style\b|script\b)', re.I)
        self.endRM = {
            '!': re.compile(r'--\s*>'), # HTML Comment
            'script': re.compile(r'</script[^>]*>', re.I), # Script Tags
            'style': re.compile(r'</style[^>]*>', re.I) # Style Tags
        }
        
        if indir:
            for f in os.listdir(indir):
                if self.verbose:
                    print "Processing: %s" % (f)
                fp = open(os.path.join(indir, f), "r")
                content = fp.read()
                fp.close()                
                content  = self.strip_tags(content)
                if outdir and content:
                    fp = open(os.path.join(outdir, f), "w")
                    fp.write(content)
                    fp.close()
        
    def strip_tags(self, html):
        html = self.aggressively_strip(html)
        try:
            s = Stripper()
            s.feed(html)
            html = s.get_data()
            html = re.sub('\s+', ' ', re.sub('\n+|\t+', ' ', html))
            return html.strip()
        except:
            if self.verbose:
                print "  Skipped: Error parsing the page"
            return None

    def aggressively_strip(self, html):
        chunks, pos = [], 0
        while True:
            startmatch = self.startRM.search(html, pos)
            if not startmatch:
                break
            tagname = startmatch.group(1).rstrip('-').strip()
            tagname = tagname.lower().encode('utf-8')
            endmatch = self.endRM[tagname].search(html, startmatch.end())
            if not endmatch:
                break
            chunks.append(html[pos:startmatch.start()])
            pos = endmatch.end()
        chunks.append(html[pos:])
        html = ''.join(chunks)
        return html

if __name__ == "__main__":
    _storage = os.path.realpath(os.path.join(os.path.dirname(__file__), '../../storage'))
    import optparse
    parser = optparse.OptionParser(description="Tag Stripper",
                                   usage="usage: %prog [options] <htmlfile>",
                                   version=__version__)
    parser.add_option('-v', '--verbose', help="Verbose Output [default: %default]", action="count", default=False)
    parser.add_option('-i', '--input', help="Input stored files [default: %default]", default=os.path.join(_storage, 'crawled', ''))
    parser.add_option('-o', '--output', help="Output location to stored files [default: %default]", default=os.path.join(_storage, 'stripped', ''))

    (options, args) = parser.parse_args()
    if args:
        for arg in args:
            if os.path.isfile(arg):
                fp = open(args[0], "r")
                fcontent = fp.read()
                fp.close()
                
                t = TagStripper()
                print t.strip_tags(fcontent)
    else:
        TagStripper(
            indir=options.input,
            outdir=options.output,
            verbose=options.verbose
        )
