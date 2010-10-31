"""Indexer"""
import sys
import os
import re
import string

__version__ = "1.0"
__authors__ = "Brittany Thompson <miller317@gmail.com>"
__date__ = "Oct 28, 2010"

class Indexer:
    def __init__(self, indir=None, outdir=None, verbose=False):
        self.verbose = verbose
        self.terms = {}        
        if indir:
            for f in os.listdir(indir):
                if self.verbose:
                    print "Processing: %s" % (f)
                fp = open(os.path.join(indir, f), "r")
                self.page = f
                content = fp.read()
                fp.close()

                if outdir:
                    fp = open(os.path.join(outdir, f), "w")
                    fp.write(self.index_words(content))
                    fp.close()
        
    def index_words(self, text):
        try:
            for word in text.split(' '):
                print word
                if self.terms.has_key(word): #if word is in index
                    if self.terms[word].has_key(self.page): #if not first occurance for this page
                        self.terms[word][self.page] = self.terms[word][self.page] + 1
                    else:
                        self.terms[word][self.page] = 1
                else: #if word is not in the index, then add it
                    self.terms[word] = {self.page: 1}
            print self.terms
        except:
            if self.verbose:
                print " Error indexing file"
            pass
        return ' '.join(self.terms)

if __name__ == "__main__":
    _storage = os.path.realpath(os.path.join(os.path.dirname(__file__), '../../storage'))
    import optparse
    parser = optparse.OptionParser(description="Indexer",
                                   usage="usage: %prog [options] <textfile>",
                                   version=__version__)
    parser.add_option('-v', '--verbose', help="Verbose Output [default: %default]", action="count", default=False)
    parser.add_option('-i', '--input', help="Input stored files [default: %default]", default=os.path.join(_storage, 'stemmed', ''))
    parser.add_option('-o', '--output', help="Output location to stored files [default: %default]", default=os.path.join(_storage, 'indexed', ''))

    (options, args) = parser.parse_args()
    if args:
        for arg in args:
            if os.path.isfile(arg):
                fp = open(args[0], "r")
                fcontent = fp.read()
                fp.close()
                
                t = Indexer()
                print t.index_words(fcontent)
    else:
        Indexer(
            indir=options.input,
            outdir=options.output,
            verbose=options.verbose
        )
