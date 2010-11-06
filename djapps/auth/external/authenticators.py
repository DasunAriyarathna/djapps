
import sys, logging, md5
from datetime import datetime
import djapps.utils.request     as djrequtils
from django.http import HttpResponseRedirect
from djapps.dynamo.helpers import get_or_create_object, get_first_object
import models as djacmodels
import settings

try:
    from threading import local
except ImportError:
    from django.utils._thread_local import local

_thread_locals = local()

class Authenticator(object):
    def __init__(self, **kwargs):
        self.host_site_name = kwargs['host_site']
        self.host_site      = None

    def authenticate(self, request):
        """ Authenticates a request and if successful, returns a descriptor
        object that lazily loads the UserAlias object when actually used and
        also a object for the host site!!!"""
        return None

    def authenticate_credentials(self, **credentials):
        """ Authenticates a request and if successful, returns a descriptor
        object that lazily loads the UserAlias object when actually used and
        also a object for the host site!!!"""
        return None

    def processResponse(self, request, response):
        pass

    def logout(self, request):
        """ Called to cleanup any cookies we may have created. """
        pass

# 
# Tries to authenticate a request by local site and returns a user alias
#
class AuthLocalSite(Authenticator):
    def authenticate(self, request):
        if settings.USING_APPENGINE:
            local_user = request.local_user
        else:
            local_user = request.user

        username = None
        if local_user:
            if (not hasattr(local_user, "is_authenticated")) or local_user.is_authenticated():
                username = local_user.username
        return username

    def logout(self, request):
        """ Called to cleanup any cookies we may have created. """
        if settings.USING_APPENGINE:
            logging.debug("============================================================")
            logging.debug("TODO - Loggin Out - TBD for GAE")
            logging.debug("============================================================")
        else:
            from django.contrib.auth import logout
            logout(request)
        
