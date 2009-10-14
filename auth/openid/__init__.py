
PROVIDERS_KEY = "_openid_providers_key"

from django.conf import settings
from djapps.dynamo import helpers as dynhelpers
import base64

def user_from_key(user_id, server_url):
    if settings.USING_APPENGINE:
        from djapps.auth.local.gaemodels import LocalUser
    else:
        from django.contrib.auth.models import User as LocalUser

    user_class = LocalUser

    username    = user_id # base64.encodestring(user_id).replace("\n", "")
    user        = dynhelpers.get_first_object(user_class, username = username)
    if not user:
        user = dynhelpers.create_object(user_class, False, None, username = username)
        user.set_unusable_password()
        dynhelpers.save_objects(user)

    return user

def user_alias_from_key(user_id, server_url):
    pass

class OpenIDContext(object):
    def __init__(self, request):
        self.request = request

    def get_providers(self):
        if PROVIDERS_KEY in self.request.openid_session:
            return self.request.openid_session[PROVIDERS_KEY].keys()
        else:
            return []

    def get_users(self):
        if PROVIDERS_KEY in self.request.openid_session:
            providers = self.request.openid_session[PROVIDERS_KEY]
            return [{'op': providers[key], 'id': providers[key]} for key in providers]
        else:
            return []

    def is_logged_in(self):
        return PROVIDERS_KEY in self.request.openid_session and len(self.request.openid_session[PROVIDERS_KEY]) > 0

    def get_user(self, provider = None, user_finder = user_from_key):
        """
        Gets the user that is being authenticated by a particular provider.
        If no provider is specified then the user by the first provider
        (along with the provider) is returned.

        Another thing is we are forcing the type of user class here.  This
        may be a problem if a different user class is required - ie we need
        UserAliases instead of Plain users.  We could inherit this class
        and override this method, but then the problem would be that in
        middleware.py, the LazyOpenIDContext creates an instead of this
        class - changing the class it creates an instance of there is a
        problem.

        So to get around this, this method also takes a user_finder method
        which will be responsible for creating/fetching the user object
        given the user ID (and the provider/server url).
        """
        if PROVIDERS_KEY in self.request.openid_session:
            providers = self.request.openid_session[PROVIDERS_KEY]
            if provider:
                user_id = providers[provider]
            else:
                user_id = providers.itervalues().next()
            return user_finder(user_id, provider)
        return None
    
    def logout_from_provider(self, provider = None):
        """
        Logout from a specific provider or all providers
        """
        if PROVIDERS_KEY in self.request.openid_session:
            providers = self.request.openid_session[PROVIDERS_KEY]
            if provider:
                if provider in providers:
                    del providers[provider]
                    self.request.openid_session[PROVIDERS_KEY] = providers
            else:
                self.request.openid_session[PROVIDERS_KEY] = []
