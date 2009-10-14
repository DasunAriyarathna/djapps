
import sys, logging
from datetime import datetime
import djapps.utils.request     as djrequtils
from django.http import HttpResponse
from djapps.auth.external.authenticators import Authenticator
from djapps.dynamo import helpers as dynhelpers

from openid import fetchers
from openid.consumer.consumer import Consumer
from openid.consumer import discover
from openid.extensions import pape, sreg

try:
    from threading import local
except ImportError:
    from django.utils._thread_local import local
_thread_locals = local()

SESSION_USER_ALIAS_LIST = "_session_useralias_list"

# 
# Tries to authenticate a request by facebook and returns a user alias
#
class AuthOpenID(Authenticator):
    def __init__(self, **kwargs):
        super(AuthOpenID, self).__init__(**kwargs)
        self.openid_url             = kwargs['OPENID_SERVER_URL']
        self.consumer_instance      = None

    def get_consumer(self):
        if not self.consumer_instance:
            fetchers.setDefaultFetcher(fetcher.UrlfetchFetcher())
            self.consumer_instance = Consumer(request.session, store.DatastoreStore())
        return self.consumer_instance

    def authenticate(self, request):
        """
        Authenticates a request.  We have the following request types to
        handle.
            1. A redirection by the openid provider with a whole bunch
               openid parameters.
            2. A normal request with no openid parameters in the URL.  This
               could mean that one of the preceeding requests had the openid
               parameters in it in which case we lookup the openid user info
               from the session object.
            3. Neither.  In this case we are request NOT authenticated by
               the specific openid provider (could have others ofcourse).
        """

        goog_user = None
        #
        # we only see if calls to /openid/login/initiate and
        # /openid/login/complete (or other urls) have resulted in the
        # creation of respective session keys from the openid providers we
        # are interested in and save them in ms_session
        #
        return goog_user

    def logout(self, request):
        # mark the session cookies to be deleted
        # request.ms_session[self.FB_SESSION_DELETE] = True
        request.delete_fb_session = True
        request.ms_session.save()
