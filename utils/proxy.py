
import urllib2

class SkippableProxyHandler(urllib2.ProxyHandler):
    """
    A proxy handler that disables the proxy for hosts in a given list,
    but goes through the proxy for all other hosts.
    """
    def __init__(self, proxies = None, *skiplist):
        super(SkippableProxyHandler, self).__init__(proxies)
        self.skiplist = skiplist
