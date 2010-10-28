"""PageRank Calculation"""
import sys
from lxml import etree
import os

__version__ = "1.0"
__authors__ = "Bhadresh Patel <bhadresh@wsu.edu>"
__date__ = "Oct 24, 2010"

class PageRank:
    """PageRank"""
    def __init__(self, linkmap=None, output=None, Lambda=0.15, convergence=0.0001, verbose=False):
        self.verbose = verbose
        self.linkmap = linkmap

        ranks = {}
        pages = {}
        tree = etree.parse(self.linkmap)
        documents = tree.xpath("//doc/@id")
        D = len(documents) # Size of document collection
        initial_rank = 1.0 / D
        for p in documents:
            ranks[p] = initial_rank
            pages[p] = {}
            pages[p]['from'] = tree.xpath("//doc[@id='%s']/from/page/@id" % p)
            pages[p]['to'] = tree.xpath("//doc[@id='%s']/to/page/@id" % p)

        ni = 0
        rdiff = convergence * 2
        while rdiff > convergence:
            ni = ni + 1
            if self.verbose:
                print "Iteration: %d" % ni
            rdiff = convergence
            for p in pages:
                s = 0
                for q in pages[p]['from']:
                    try:
                        s = s + (ranks[q] / len(pages[q]['to']))
                    except:
                        pass

                nr = (Lambda * initial_rank) + (1 - Lambda) * s
                diff = abs(ranks[p] - nr)
                if (diff > rdiff):
                    rdiff = diff
                ranks[p] = nr

        if output:
            fp = open(output, "w")
            for docid, pagerank in ranks.iteritems():
                fp.write("%s:%s\n" % (docid, pagerank))
            fp.close()

        if self.verbose:
            print "# of iterations: %d" % ni
            print "Top 10 pages:"
            toppages = sorted(ranks.iteritems(), key=lambda(docid, rank): (-rank, docid))[:10]
            print "-" * 60
            print "%4s\t%-32s\t%s" % ("#", "Page ID", "PageRank")
            print "-" * 60
            for n, (docid, rank) in enumerate(toppages):
                print "%4s\t%-32s\t%f" % (n + 1, docid, rank)
            print "-" * 60

if __name__ == "__main__":
    _storage = os.path.realpath(os.path.join(os.path.dirname(__file__), '../../storage'))
    import optparse
    parser = optparse.OptionParser(description="PageRank",
                                   usage="usage: %prog [options] <mapfile>",
                                   version=__version__)
    parser.add_option('-v', '--verbose', help="Verbose Output [default: %default]", action="count", default=False)
    parser.add_option('-o', '--output', help="Output file to save PageRanks [default: %default]", default=os.path.join(_storage, 'pagerank.dat'))

    (options, args) = parser.parse_args()
    if not args:
        print "Please select provide map file"
        parser.print_help()
        sys.exit(1)

    p = PageRank(args[0], output=options.output, verbose=options.verbose)
