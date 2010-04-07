
PROVIDERS_KEY = "_openid_providers_key"

from django.conf import settings
from djapps.dynamo import helpers as dynhelpers
import base64

def default_user_finder(user_id, server_url):
    if settings.USING_APPENGINE:
        from djapps.auth.local.gaemodels import LocalUser
    else:
        from django.contrib.auth.models import User as LocalUser

    username    = user_id # base64.encodestring(user_id).replace("\n", "")
    user        = dynhelpers.get_first_object(LocalUser, username = username)
    return user

def default_user_maker(user_id, server_url):
    if settings.USING_APPENGINE:
        from djapps.auth.local.gaemodels import LocalUser
    else:
        assert False, "Do we need to resize the username field in django User model"
        from django.contrib.auth.models import User as LocalUser

    username    = user_id
    user        = dynhelpers.get_first_object(LocalUser, username = username)
    new_created = False
    if not user:
        new_created = True
        user = dynhelpers.create_object(LocalUser, False, None, username = username)
        user.set_unusable_password()
        dynhelpers.save_objects(user)
    return user, new_created

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

    def get_user(self, provider = None, user_finder = default_user_finder):
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
        user = None
        if PROVIDERS_KEY in self.request.openid_session:
            providers = self.request.openid_session[PROVIDERS_KEY]
            if provider:
                user_id = providers[provider]
            else:
                user_id = providers.itervalues().next()
            user = user_finder(user_id, provider)
            if not user:
                # remove the provider then
                if provider:
                    del providers[provider]
                self.request.openid_session[PROVIDERS_KEY] = providers

        return user
    
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
