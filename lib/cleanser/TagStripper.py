"""HTML Tag Stripper"""
import os
import re

__version__ = "1.0"
__authors__ = "Bhadresh Patel <bhadresh@wsu.edu>"
__date__ = "Sep 23, 2010"

class TagStripper:
    """HTML Tag Stripper"""
    def __init__(self, indir=None, outdir=None, verbose=False):
        self.verbose = verbose
        self.patterns = [
            re.compile(r'<(style|script|object|embed|applet|noframes|noscript)[^>]*?>.*?</\1>', re.I | re.S), # Aggressively strip tags
            re.compile(r'<![\s\S]*?--[ \t\n\r]*>'), # Strip HTML comments
            re.compile(r'<[\/\!]*?[^<>]*?>', re.S), # Strip HTML tags
        ]

        if indir:
            for f in os.listdir(indir):
                if self.verbose:
                    print "Processing: %s" % (f)
                fp = open(os.path.join(indir, f), "r")
                content = fp.read()
                fp.close()
                content = self.strip_tags(content)
                if outdir:
                    fp = open(os.path.join(outdir, f), "w")
                    fp.write(content)
                    fp.close()

    def strip_tags(self, html):
        """Strip Tags"""
        try:
            for p in self.patterns:
                html = p.sub(' ', html)
        except:
            if self.verbose:
                print "  Error stripping tags"
            pass
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
