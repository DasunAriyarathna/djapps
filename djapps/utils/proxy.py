
import urllib2

class SkippableProxyHandler(urllib2.BaseHandler):
    """
    A proxy handler that disables the proxy for hosts in a given list,
    but goes through the proxy for all other hosts.
    """
    def __init__(self, skiplist = [], proxy_handler = None, noproxy_handler = None):
        # damn it ProxyHandler is an old-style class!!!
        self.skiplist = skiplist

        self.proxy_handler = proxy_handler
        if self.proxy_handler is None:
            self.proxy_handler = urllib2.ProxyHandler()

        self.noproxy_handler = noproxy_handler
        if self.noproxy_handler is None:
            self.noproxy_handler = urllib2.HTTPHandler()

    def http_open(self, req, proxy, type):
        if True:
            self.proxy_handler.proxy_open(req, proxy, type)
        else:
            self.noproxy_handler.http_open(req)
