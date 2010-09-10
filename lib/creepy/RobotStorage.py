import urlparse
from Robot import Robot

class RobotStorage:
    """Storage class for robots - emulates/encapsulates a dict"""
    
    DEFAULT_OPTS = {
        # Default time-out for failed connections: 3 seconds
        'timeout': 3,   
        # Default expiration time: 24 hrs (86,400 seconds)
        'expires_in': 86400
    }
    
    def __init__(self, user_agent, opts = {}):
        self.user_agent = user_agent
        self.storage = {}
        self.opts = dict(self.DEFAULT_OPTS.items() + opts.items())
    
    def __getitem__(key):
        return self.storage[key]
    
    def __setitem__(key, value):
        self.storage[key] = value
    
    def __delitem__(key):
        del self.storage[key]
    
    def get_robot(self, uri):
        domain = urlparse.urlparse(uri).netloc
        
        if domain in self.storage:
            return self.storage[domain]
        else:
            robot = Robot(uri, self.user_agent, self.opts)
            self.storage[domain] = robot
            return robot
    

