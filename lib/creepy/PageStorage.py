
"""
PageStorage.py
Each retrieved document is renamed and saved as a unique ID based on the URL since URLs are by design unique
Once a certain number of files are obtained or the crawler is done, the dictionary is dumped into pid_map.dat
"""

import os
import re

class PageStorage:
    DEFAULT_OPTS = {
        # Maximum capacity for the hash - once over this point everything needs dumped
        'capacity': 1000,
        # Default storage location for all dumped files
        'store_location': 'storage/'
    }
  
    def __init__(self, opts = {}):
        self.storage = {}
        self.opts = dict(self.DEFAULT_OPTS.items() + opts.items())
        
        d = os.path.dirname(self.opts['store_location'])
        if not os.path.exists(d):
            os.makedirs(d)
    
    def store(self, url, doc):
        f = open(self.opts['store_location'] + PageStorage.slugify(url), 'w')
        f.write(doc)
        f.close()
    
    @staticmethod
    def slugify(value):
        """
        Normalizes string, converts to lowercase, removes non-alpha characters,
        and converts spaces to hyphens. From the Django library: (template/defaultfilters.py)
        """
        import unicodedata
        value = unicodedata.normalize('NFKD', unicode(value)).encode('ascii', 'ignore')
        value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
        return re.sub('[-\s]+', '-', value)
    
