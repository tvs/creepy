#!/usr/bin/env python
"""PageRank Calculation"""

import sys
from lxml import etree
import os

__version__ = "1.0"
__authors__ = "Bhadresh Patel <bhadresh@wsu.edu>"
__date__ = "Oct 24, 2010"

class PageRank:
    """PageRank"""
    def __init__(self, damping_factor=0.85, convergence=0.0000001, verbose=False):
        self.verbose = verbose
        self.damping_factor = damping_factor
        self.convergence = convergence

    def calculate(self, linkmap, output=None):
        """Calculate PageRank Sequentially"""
        ranks = {}
        newranks = {}
        pages = {}
        tree = etree.parse(linkmap)
        documents = tree.xpath("//doc/@id")
        for p in documents:
            ranks[p] = 1.0 # Initial PageRank
            pages[p] = {}
            pages[p]['in'] = tree.xpath("//doc[@id='%s']/from/page/@id" % p) # Inbound Links
            pages[p]['out'] = tree.xpath("//doc[@id='%s']/to/page/@id" % p) # Outbound Links

        ni = 0
        self.print_ranks(ni, ranks)
        rdiff = self.convergence * 2
        while rdiff > self.convergence:
            ni = ni + 1
            rdiff = self.convergence
            for p in pages:
                s = 0
                for q in pages[p]['in']:
                    try:
                        s = s + (ranks[q] / len(pages[q]['out']))
                    except:
                        pass

                nr = (1.0 - self.damping_factor) + (self.damping_factor * s)
                diff = abs(ranks[p] - nr)
                if (diff > rdiff):
                    rdiff = diff
                newranks[p] = nr

            ranks = newranks.copy()
            self.print_ranks(ni, ranks)

        if output:
            fp = open(output, "w")
            for docid, pagerank in ranks.iteritems():
                fp.write("%s:%s\n" % (docid, pagerank))
            fp.close()

        if self.verbose:
            print "\n# of iterations:", ni
            print "Top 10 pages:"
            toppages = sorted(ranks.iteritems(), key=lambda(docid, rank): (-rank, docid))[:10]
            print "-" * 60
            print "%4s\t%-32s\t%s" % ("#", "Page ID", "PageRank")
            print "-" * 60
            for n, (docid, rank) in enumerate(toppages):
                print "%4s\t%-32s\t%f" % (n + 1, docid, rank)
            print "-" * 60

    def print_ranks(self, i, ranks):
        if self.verbose > 1:
            keys = sorted(ranks.keys())
            if i == 0:
                print "-" * (11 + 16 * len(keys))
                print "%-10s" % "Iteration",
                for k in keys:
                    print "%15s" % ("Pr(%s)" % k),
                print
                print "-" * (11 + 16 * len(keys))

            print "%-10s" % i,
            for k in keys:
                print "%15.7f" % ranks[k],
            print

    def prepare_data(self, linkmap, output=None):
        """Prepare Data for MapReduce PageRank Calculation"""
        if output and os.path.isfile(output):
            print "Invalid output location, it is a existing file"
            return
        if not os.path.isfile(linkmap):
            print "linkmap file does not exits"
            return

        if os.path.isdir(output):
            import shutil
            shutil.rmtree(output)
        os.makedirs(output)
        tree = etree.parse(linkmap)
        documents = tree.xpath("//doc/@id")
        initial_rank = 1.0 # Initial Rank
        fp = None
        n = 0
        for docid in documents:
            if n % 50 == 0:
                if fp:
                    fp.close()
                fp = open(os.path.join(output, str((n / 50) + 1)), "w")
            outlinks = tree.xpath("//doc[@id='%s']/to/page/@id" % docid)
            if len(outlinks) > 0:
                n = n + 1
                fp.write("%s\t%s\t%s\n" % (docid, initial_rank, ",".join(outlinks)))

    def mapper(self):
        """Mapper code for MapReduce PageRank Calculation"""
        for line in sys.stdin:
            (docid, pr, outlinks) = line.strip().split('\t')
            outlinks = outlinks.split(',')
            npr = float(pr) * 1.0 / len(outlinks)
            print "%s\t[%s]" % (docid, ",".join(outlinks))
            for p in outlinks:
                print "%s\t%s" % (p, npr)

    def reducer(self):
        """Reducer code for MapReduce PageRank Calculation"""
        ranksum = {}
        outlinks = {}
        for line in sys.stdin:
            (docid, value) = line.strip().split('\t')
            if value.startswith('['):
                outlinks[docid] = value.strip('[]')
            else:
                ranksum[docid] = ranksum.get(docid, 0) + float(value)

        outlinks = sorted(outlinks.items())
        for docid, links in outlinks:
            pr = (1.0 - self.damping_factor) + (self.damping_factor * ranksum.get(docid, 0))
            print "%s\t%s\t%s" % (docid, pr, links)

    def final_mapper(self):
        """Final Mapper code"""
        for line in sys.stdin:
            (docid, pr, outlinks) = line.strip().split('\t')
            print "%s\t%s" % (docid, pr)

    def final_reducer(self):
        """Final Reducer code"""
        for line in sys.stdin:
            (docid, pr) = line.strip().split('\t')
            print "%s:%s" % (docid, pr)

if __name__ == "__main__":
    _storage = os.path.realpath(os.path.join(os.path.dirname(__file__), '../../storage'))
    import optparse
    parser = optparse.OptionParser(description="PageRank Calculation",
                                   usage="usage: %prog [options]",
                                   version=__version__)
    parser.add_option('-v', '--verbose', help="Verbose Output [default: %default]", action="count", default=False)
    parser.add_option('-o', '--output', help="Output location")
    parser.add_option('-d', '--damping', help="Damping factor [default: %default]", default=0.85, type='float')
    parser.add_option('-c', '--convergence', help="Convergence [default: %default]", default=0.0000001, type='float')
    parser.add_option('-l', '--linkmap', help="Calculate PageRank sequentially using given linkmap file", metavar="LINKMAP")
    parser.add_option('-p', '--prepare_data', help="Prepare Data for MapReduce PageRank Calculation", metavar="LINKMAP")
    parser.add_option('-m', '--mapper', help="Run Mapper code for MapReduce PageRank", action="store_true")
    parser.add_option('-r', '--reducer', help="Run Reducer code for MapReduce PageRank", action="store_true")
    parser.add_option('-f', '--final', help="Run final step code", action="store_true")

    (options, args) = parser.parse_args()
    p = PageRank(damping_factor=options.damping, convergence=options.convergence, verbose=options.verbose)

    if options.final:
        if options.mapper:
            p.final_mapper()
        elif options.reducer:
            p.final_reducer()
    elif options.mapper:
        p.mapper()
    elif options.reducer:
        p.reducer()
    elif options.prepare_data:
        p.prepare_data(options.prepare_data, options.output or os.path.join(_storage, 'pagerank', 'input'))
    elif options.linkmap:
        p.calculate(options.linkmap, options.output or os.path.join(_storage, 'pagerank.dat'))
    else:
        print "Please select appropriate option"
        parser.print_help()
        sys.exit(1)

