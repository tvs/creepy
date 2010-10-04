"""page Stopper"""
import sys
import os
import re
import string

__version__ = "1.0"
__authors__ = "Brittany Thompson <miller317@gmail.com>"
__date__ = "Sep 23, 2010"

class Stopper:
    def __init__(self, indir=None, outdir=None, verbose=False):
        self.verbose = verbose
        
        if indir:
            for f in os.listdir(indir):
                if self.verbose:
                    print "Processing: %s" % (f)
                fp = open(os.path.join(indir, f), "r")
                content = fp.read()
                fp.close()
                #content = self.stop_words(content)
                #print content

                if outdir:
                    fp = open(os.path.join(outdir, f), "w")
                    fp.write(self.stop_words(content))
                    fp.close()
        
    def stop_words(self, text):
        self.stoplist = []
        self.fixed = []
        text = text.lower()

        fp = open("stoplist.txt", "r")
        stopFile = fp.read()
        for word in stopFile.split('\n'):
            self.stoplist.append(word)
    
        try:
            for word in text.split(' '):
                if word not in self.stoplist:
                    self.fixed.append(word)
                print word
            print self.fixed
        except:
            if self.verbose:
                print " Error stopping file"
            pass
        return ' '.join(self.fixed)

if __name__ == "__main__":
    _storage = os.path.realpath(os.path.join(os.path.dirname(__file__), '../../storage'))
    import optparse
    parser = optparse.OptionParser(description="Stopper",
                                   usage="usage: %prog [options] <textfile>",
                                   version=__version__)
    parser.add_option('-v', '--verbose', help="Verbose Output [default: %default]", action="count", default=False)
    parser.add_option('-i', '--input', help="Input stored files [default: %default]", default=os.path.join(_storage, 'tokenized', ''))
    parser.add_option('-o', '--output', help="Output location to stored files [default: %default]", default=os.path.join(_storage, 'stopped', ''))

    (options, args) = parser.parse_args()
    if args:
        for arg in args:
            if os.path.isfile(arg):
                fp = open(args[0], "r")
                fcontent = fp.read()
                fp.close()
                
                t = Stopper()
                print t.stop_words(fcontent)
    else:
        Stopper(
            indir=options.input,
            outdir=options.output,
            verbose=options.verbose
        )
