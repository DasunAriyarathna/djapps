
import sys, time, logging
from django.conf import settings
from django.utils.cache import patch_vary_headers

# 
# This middleware allows facilitates the access module for fine grained yet
# simple authentication by sites and authorization to resources.
#
class AccessMiddleware(object):
    def __init__(self):
        pass

    def process_request(self, request):
        # use the old request (though possibly modified)
        return None

    def process_response(self, request, response):
        return response

