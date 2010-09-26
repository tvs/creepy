"""
PageStorage.py
Each retrieved document is renamed and saved as a unique ID based on the URL since URLs are by design unique
Once a certain number of files are obtained or the crawler is done, the dictionary is dumped into pid_map.dat
"""

import os
import hashlib

class PageStorage:
    DEFAULT_OPTS = {
        # Default storage location for all dumped files
        'store_location': 'storage/',
        # Default mapping file
        'map_file': 'pid_map.dat'
    }
  
    def __init__(self, opts = {}):
        self.opts = dict(self.DEFAULT_OPTS.items() + opts.items())
        
        d = os.path.dirname(self.opts['store_location'])
        if not os.path.exists(d):
            os.makedirs(d)
    
    def store(self, url, doc):
        locname = PageStorage.md5(url).hexdigest()
        
        f = open(os.path.join(self.opts['store_location'], locname), 'w')
        f.write(doc)
        f.close()
        
        f = open(os.path.join(self.opts['store_location'], '..', self.opts['map_file']), 'a')
        f.write(url + " => " + locname + "\n")
        f.close()    
    
    @staticmethod
    def md5(value):
        return hashlib.md5(value)    
