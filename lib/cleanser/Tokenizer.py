"""Tokenizer"""
import os
import string

__version__ = "1.0"
__authors__ = "Bhadresh Patel <bhadresh@wsu.edu>"
__date__ = "Sep 25, 2010"

class Tokenizer:
    """Tokenizer"""
    def __init__(self, indir=None, outdir=None, verbose=False):
        self.verbose = verbose
        if indir:
            for f in os.listdir(indir):
                if self.verbose:
                    print "Processing: %s" % (f)
                fp = open(os.path.join(indir, f), "r")
                content = fp.read()
                fp.close()
                content  = self.tokenize(content)
                if outdir:
                    fp = open(os.path.join(outdir, f), "w")
                    fp.write(content)
                    fp.close()

    def tokenize(self, content):
        """Tokenize the given string"""
        # 1. Convert to lowercase
        out = content.lower()
        # 2. Remove all punctuations !"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~
        out = out.translate(None, string.punctuation)
        # 3. Make tokens - remove multiple spaces and lines
        out = string.join(string.split(out))
        return out

if __name__ == "__main__":
    _storage = os.path.realpath(os.path.join(os.path.dirname(__file__), '../../storage'))
    import optparse
    parser = optparse.OptionParser(description="Tokenizer",
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
                content = fp.read()
                fp.close()

                t = Tokenizer()
                print t.tokenize(content)
    else:
        Tokenizer(
            indir=options.input,
            outdir=options.output,
            verbose=options.verbose
        )
