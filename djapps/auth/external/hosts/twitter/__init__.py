
import sys, logging, md5
from datetime import datetime
import djapps.utils.request     as djrequtils
from djapps.auth.external.authenticators import Authenticator
from djapps.dynamo.helpers import get_or_create_object, get_first_object

try:
    from threading import local
except ImportError:
    from django.utils._thread_local import local

_thread_locals = local()

SESSION_USER_ALIAS_LIST = "_session_useralias_list"

# 
# Tries to authenticate a request by twitter and returns a user id
#
class AuthTwitter(Authenticator):

    def __init__(self, **kwargs):
        super(AuthTwitter, self).__init__(**kwargs)
        self.oauth_server               = kwargs['TWITTER_OAUTH_SERVER']
        self.consumer_key               = kwargs['TWITTER_CONSUMER_KEY']
        self.consumer_secret            = kwargs['TWITTER_CONSUMER_SECRET']
        self.app_name                   = kwargs['TWITTER_APP_NAME']
        self.request_token_url          = kwargs['TWITTER_REQUEST_TOKEN_URL']
        self.access_token_url           = kwargs['TWITTER_ACCESS_TOKEN_URL']
        self.authorize_url              = kwargs['TWITTER_AUTHORIZE_URL']

        import httplib
        from djapps.utils import oauth
        self.connection         = httplib.HTTPSConnection(self.oauth_server)
        self.consumer           = oauth.OAuthConsumer(self.consumer_key, self.consumer_secret)
        self.signature_method   = oauth.OAuthSignatureMethod_HMAC_SHA1()

    def authenticate(self, request):
        return None

    def processResponse(self, request, response):
        pass

    def logout(self, request):
        pass
