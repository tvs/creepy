#!/usr/bin/env python
import sys, os, shutil
sys.path.append('lib/crawler/')
sys.path.append('lib/cleanser/')

__version__ = "1.1"
__authors__ = "Travis Hall <trvs.hll@gmail.com>, Brittany Miller <miller317@gmail.com> and Bhadresh Patel <bhadresh@wsu.edu>"
__date__ = "Sep 5, 2010"

_verbose = False
_debug = False
_clean = False
_storage = sys.path[0] + "/storage/"
_storage_dirs = {
    'crawler': 'crawled',
    'stripper': 'stripped',
    'stopper': 'stopped',
    'stemmer': 'stemmed',
    'tokenizer': 'tokenized'
}

if __name__ == "__main__":
    import optparse
    parser = optparse.OptionParser(description="Creepy Search Engine",
                                usage="usage: %prog [options] <arguments>",
                                version=__version__)
    parser.add_option('-v', '--verbose', help="Verbose Output [default: %default]", action="count", default=_verbose)
    parser.add_option('-d', '--debug', help="Debug Mode [default: %default]", action="count", default=_debug)
    parser.add_option('-S', '--storage', action="store", type="string", dest="storage", help="Data Storage location [default: %default]", default=_storage)
    parser.add_option('-C', '--clean_start', help="Start clean by deleting existing storage location [default: %default]", action="store_true", default=_clean)

    # Project 1: Web Crawler
    ops = optparse.OptionGroup(parser, "Web Crawler", "Crawling the Web: Takes set of seed urls and start crawling the web and stores the pages in the storage location.")
    ops.add_option('-c', '--crawl', help="Crawl the web", action="store", metavar="<seeds | seedfile>")
    ops.add_option('-T', '--page_threshold', help="Max. number of pages to crawl [default: %default]", metavar="THRESHOLD", type='int', default=2500)
    ops.add_option('-N', '--num_threads', help="Number of threads to use [default: %default]", metavar="NUM_THREADS", type='int', default=1)
    parser.add_option_group(ops)

    # Project 2: Data Preparation
    ops = optparse.OptionGroup(parser, "Data Cleanser", "Data Preparation/Cleansing: Reads pages stored by the crawler and perform requested actions.")
    ops.add_option('-s', '--strip_tags', help="HTML Tag Stripping", action="store_true")
    ops.add_option('-t', '--tokenize', help="Tokenize the document", action="store_true")
    parser.add_option_group(ops)

    (options, args) = parser.parse_args()
    _verbose = options.verbose
    _debug = options.debug
    _clean = options.clean_start
    _storage = options.storage

    if _clean:
        shutil.rmtree(_storage)

    # Create Storage Dirs
    if not os.path.isdir(_storage):
        os.mkdir(_storage)
    for k,d in _storage_dirs.iteritems():
        _storage_dirs[k] = os.path.join(_storage, d, '')
        if not os.path.isdir(_storage_dirs[k]):
            os.mkdir(_storage_dirs[k])

    # Call Module
    if options.crawl: # Web Crawler
        args.insert(0, options.crawl)
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
            sys.exit(1)

        print "### Number of seeds:", len(seeds)
        from Crawler import Crawler
        Crawler(seeds, _storage_dirs['crawler'],
            threshold=options.page_threshold,
            num_threads=options.num_threads,
            verbose=_verbose)
    elif options.strip_tags: # Tag Stripper
        from TagStripper import TagStripper
        TagStripper(
            indir=_storage_dirs['crawler'],
            outdir=_storage_dirs['stripper'],
            verbose=options.verbose
        )        
    elif options.tokenize: # Tokenizer
        from Tokenizer import Tokenizer
        Tokenizer(
            indir=_storage_dirs['stripper'],
            outdir=_storage_dirs['tokenizer'],
            verbose=options.verbose
        )        
    else:
        print "Please select appropriate action"
        parser.print_help()
        sys.exit(1)

