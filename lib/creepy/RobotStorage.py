import urlparse
from Robots import Robots

class RobotStorage:
    """Storage class for robots - emulates/encapsulates a dict"""
    def __init__(self, user_agent):
        self.user_agent = user_agent
        self.storage = {}
    
    def __getitem__(key):
        return self.storage[key]
    
    def __setitem__(key, value):
        self.storage[key] = value
    
    def __delitem__(key):
        del self.storage[key]
    
    def is_allowed(self, uri):
        domain = urlparse.urlparse(uri).netloc
        
        if domain in self.storage:
            return self.storage[domain].is_allowed(uri)
        else:
            robot = Robots(uri, self.user_agent)
            self.storage[domain] = robot
            return robot.is_allowed(uri)
        
    


if __name__ == '__main__':
    rs = RobotStorage('creepy')
    print rs.is_allowed('http://en.wikipedia.org/w/index.html') # False
    print rs.is_allowed('http://en.wikipedia.org/index.html') # True
    print rs.is_allowed('http://facebook.com/index.html') # False
    print rs.is_allowed('http://facebook.com/ac.php') # False
