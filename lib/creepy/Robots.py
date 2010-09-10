import re
import urlparse
import time

from Fetcher import Fetcher

class Robots:
    DEFAULT_OPTS = {
        'timeout': 3,
        'expires_in': 86400
    }
    
    def __init__(self, uri, user_agent, opts = {}):
        self.uri = uri
        self.user_agent = user_agent
        self.opts = dict(self.DEFAULT_OPTS.items() + opts.items())
        
        self.allowed = []
        self.disallowed = []
        self.delay = 0
        self.other = {}
        
        self._parse_from_uri(uri)
    
    def is_allowed(self, uri):
        if (time.time() - self.last_looked_at) > self.opts['expires_in']:
            self._parse_from_uri(uri)
        
        allow = True
        path = urlparse.urlparse(uri).path # Strip our URI down to the path for regex
        
        # Check if it's allowed (or in an allowed area)
        # re.match should be sufficient
        for rule in self.allowed:
            if rule.match(path):
                allow = True
                break # Exit the loop early if we have a match
        
        # Check to be sure it's not explicitly disallowed
        #   Disallows in the event of conflicting rules
        #   Might be worth checking the explicitness of the rule to resolve conflicts
        for rule in self.disallowed:
            if rule.match(path):
                allow = False
                break
        
        return allow
    
        
    # Protected space
    def _parse_from_uri(self, uri):
        self.last_looked_at = time.time()
        robots = Robots._get_robots(uri, self.user_agent, self.opts['timeout'])
        
        # If there's nothing in the string let's just load in a default that's
        # allowed for everything
        if not (len(robots) > 0):
            robots = "User-agent: *\nAllow: /\n"
        
        self._parse(robots)
    
    def _parse(self, string):
        found = False
        # Prune down our robots file to our specific user-agent (unless it doesn't exist)
        startloc = string.find("User-agent: " + self.user_agent)
        
        if startloc > -1:
            string = string[startloc:]
            string = string.split('\n', 1)[1]
            found = True
        
        if not found:
            startloc = string.find("User-agent: *")
            string = string[startloc:]
            string = string.split('\n', 1)[1]
            
        # Reset these values with every parse (only parse after expiration time)
        self.allowed = []
        self.disallowed = []
        self.delay = 0
        self.other = {}
        
        for line in string.splitlines():
            if re.match(r'^\s*(#.*|$)', line): # Delete blank or comment lines
                continue
            if re.match(r'^User-agent', line): # When we find a new user-agent, exit
                return
            
            d = re.match(r'^Disallow: (.*)', line) # Add disallowed
            if d:
                self.disallowed.append(Robots._to_regex(d.group(1)))
                continue
            
            d = re.match(r'^Allow: (.*)', line) # Add allowed
            if d:
                self.allowed.append(Robots._to_regex(d.group(1)))
                continue
            
            d = re.match(r'^Crawl-delay: (.*)', line) # Update crawl-delay
            if d:
                try:
                    self.delay = int(d.group(1))
                except ValueError:
                    self.delay = 0
                continue
            
            d = re.match(r'^(.*): (.*)', line)  # Any extra crap
            if d:
                if not self.other.has_key(d.group(1)):
                    self.other[d.group(1)] = []
                self.other[d.group(1)].append(d.group(2))
        
    
    
    @staticmethod
    def _to_regex(pattern):
        if len(pattern.strip()) == 0:
            return re.compile(r'a^') # Return a regex that will never match anything
        pattern = re.escape(pattern)
        pattern = pattern.replace(re.escape("*"), ".*") # Replace '*' in the regex with '.*'
        return re.compile(r'^' + pattern)
    
    
    @staticmethod
    def _get_robots(uri, user_agent, timeout):
        io = Fetcher(urlparse.urljoin(uri, '/robots.txt'))
        return io.get_content()
    


if __name__ == '__main__':
    d = Robots('http://en.wikipedia.org/', 'creepy')
    print d.is_allowed('http://en.wikipedia.org/w/index.html')
