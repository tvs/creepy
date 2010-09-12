import sys, os, shutil
sys.path.append('lib/creepy/')

__version__ = "0.1"
__authors__ = "Travis Hall <trvs.hll@gmail.com>, Brittany Miller <miller317@gmail.com> and Bhadresh Patel <bhadresh@wsu.edu>"
__date__ = "Sep 5, 2010"
__user_agent__ = "creepybot"

_verbose = False
_debug = False
_clean = False
_storage = sys.path[0] + "/storage/"

from Crawler import Watcher
from Crawler import Crawler

if __name__ == "__main__":
    import optparse
    parser = optparse.OptionParser(description="Web Crawler",
                                   usage="usage: %prog [options] <seedfile | seeds>",
                                   version=__version__)
    parser.add_option('-v', '--verbose', help="Verbose Output [default: %default]", action="count", default=_verbose)
    parser.add_option('-d', '--debug', help="Debug Mode [default: %default]", action="count", default=_debug)
    parser.add_option('-O', '--output', action="store", type="string", dest="storage", help="Output location for stored files [default: %default]", default=_storage)
    parser.add_option('-T', '--page_threshold', help="Max. number of pages to crawl [default: %default]", metavar="THRESHOLD", default=10)
    parser.add_option('-N', '--num_threads', help="Number of threads to use [default: %default]", metavar="NUM_THREADS", default=1)
    parser.add_option('-C', '--clean_start', help="Start clean by deleting old storage location [default: %default]", action="count", metavar="CLEAN_START", default=_clean)

    (options, args) = parser.parse_args()
    if not args:
        parser.print_help()
        sys.exit(1)

    _verbose = options.verbose
    _debug = options.debug
    _clean = options.clean_start
    _storage = options.storage
    
    if _clean:
        shutil.rmtree(_storage)
    
    Watcher() # Watch for Keyboard Interrupt

    seeds = []
    for arg in args:
        if os.path.isfile(arg):
            fp = open(args[0], "r")
            fcontent = fp.read()
            fp.close()
            seeds.extend(fcontent.splitlines())
        else:
            seeds.append(arg)

    if len(seeds) == 0:
        print "Please provide Seed URL or File that contains seed urls"
        parser.print_help()
        sys.exit(1)

    print "### Number of seeds:", len(seeds)
    c = Crawler(seeds, _storage, 
        threshold=int(options.page_threshold), 
        num_threads=int(options.num_threads), 
        verbose=_verbose)
    print "### Number of URLs crawled:", len(c.urllist)
