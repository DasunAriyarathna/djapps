
import sys, time, logging
from django.conf import settings
from django.utils.cache import patch_vary_headers

from djapps.auth.sessions import get_session
import djapps.auth.external
import models as djmodels
from djapps.dynamo.helpers import get_objects, get_first_object, get_or_create_object

# Name of the MS Session Cookie
MS_SESSION_COOKIE_NAME          = 'ms_sessionid'                                    
if hasattr(settings, "MS_SESSION_COOKIE_NAME"):
    MS_SESSION_COOKIE_NAME      = session.MS_SESSION_COOKIE_NAME

MS_SESSION_COOKIE_ACTIVE_ALIAS  = 'activeUserAlias'                                    
if hasattr(settings, "MS_SESSION_ACTIVE_ALIAS"):
    MS_SESSION_COOKIE_ACTIVE_ALIAS     = session.MS_SESSION_COOKIE_ACTIVE_ALIAS

# Age of cookie, in seconds (default: 2 weeks).
MS_SESSION_COOKIE_AGE           = settings.SESSION_COOKIE_AGE
if hasattr(settings, "MS_SESSION_COOKIE_AGE"):
    MS_SESSION_COOKIE_AGE       = settings.MS_SESSION_COOKIE_AGE

# A string like ".lawrence.com", or None for standard domain cookie.
MS_SESSION_COOKIE_DOMAIN        = settings.SESSION_COOKIE_DOMAIN
if hasattr(settings, "MS_SESSION_COOKIE_DOMAIN"):
    MS_SESSION_COOKIE_DOMAIN    = settings.MS_SESSION_COOKIE_DOMAIN

# Whether the ms session cookie should be secure (https:// only).
MS_SESSION_COOKIE_SECURE    = settings.SESSION_COOKIE_SECURE
if hasattr(settings, "MS_SESSION_COOKIE_SECURE"):
    MS_SESSION_COOKIE_SECURE    = settings.MS_SESSION_COOKIE_SECURE

# The path of the ms session cookie.
MS_SESSION_COOKIE_PATH          = "/"
if hasattr(settings, "MS_SESSION_COOKIE_PATH"):
    MS_SESSION_COOKIE_PATH      = settings.MS_SESSION_COOKIE_PATH

# Whether a user's ms session cookie expires when the Web browser is closed.
MS_SESSION_EXPIRE_AT_BROWSER_CLOSE = settings.SESSION_EXPIRE_AT_BROWSER_CLOSE
if hasattr(settings, "MS_SESSION_EXPIRE_AT_BROWSER_CLOSE"):
    MS_SESSION_EXPIRE_AT_BROWSER_CLOSE  = settings.MS_SESSION_EXPIRE_AT_BROWSER_CLOSE

if not settings.USING_APPENGINE:
    # The module to store session data
    MS_SESSION_ENGINE           = settings.SESSION_ENGINE
    if hasattr(settings, "MS_SESSION_ENGINE"):
        MS_SESSION_ENGINE       = settings.MS_SESSION_ENGINE

    # Directory to store session files if using the file session module. If
    # None, the backend will use a sensible default.
    MS_SESSION_FILE_PATH        = settings.SESSION_FILE_PATH
    if hasattr(settings, "MS_SESSION_FILE_PATH"):
        MS_SESSION_FILE_PATH        = settings.MS_SESSION_FILE_PATH

class LazyUserAliases(object):
    """ A lazy descriptor that will fetch all the users aliases currently logged in in
    this session. """

    def __get__(self, request, obj_type = None):
        if not hasattr(request, '_cached_useraliases'):
            request._cached_useraliases = djapps.auth.external.get_user_aliases(request)
        return request._cached_useraliases

# 
# This middleware object allows us to leverage authentication of a user
# from one of the several trusted sites, (including ourselves).
#
class MultiSiteAuthMiddleware(object):
    def __init__(self):
        import utils
        self.authenticators = utils.load_site_authenticators()

    def process_request(self, request):
        # create a new session object ONLY for the multi site stuff so we
        # dont have to use the session that is already created!

        # dont apply multisite authentication to admin sites or logout sites
        # TODO: use an "ignorelist" for MS
        if request.path.startswith("/admin/"):
            return None

        request.ms_session      = get_session(MS_SESSION_COOKIE_NAME, request.COOKIES)

        for authenticator in self.authenticators:
            if not authenticator.host_site:
                authenticator.host_site  = get_first_object(djmodels.HostSite, site_name = authenticator.host_site_name)
            
            site_user_id = authenticator.authenticate(request)
            if site_user_id:
                # fetch the associated useralias for the fb user if any
                useralias_id = djmodels.make_useralias_id(site_user_id, authenticator.host_site),
                useralias, newcreated = get_or_create_object(djmodels.UserAlias, True, None,
                                                             useralias_id,
                                                             host_site = authenticator.host_site,
                                                             user_id = site_user_id)
                djapps.auth.external.login_useralias(request, useralias)

        request.__class__.useraliases   = LazyUserAliases()

        # use the old request (though possibly modified)
        return None

    def process_response(self, request, response):
        for authenticator in self.authenticators:
            authenticator.processResponse(request, response)

        # now save the multi site session
        # If request.ms_session was modified, or if response.session was set, save
        # those changes and set a session cookie.
        try:
            accessed = request.ms_session.accessed
            modified = request.ms_session.modified
        except AttributeError:
            pass
        else:
            if accessed:
                patch_vary_headers(response, ('Cookie',))
            if modified or settings.SESSION_SAVE_EVERY_REQUEST:
                if request.ms_session.get_expire_at_browser_close():
                    max_age = None
                    expires = None
                else:
                    max_age = request.ms_session.get_expiry_age()
                    expires_time = time.time() + max_age
                    # expires = cookie_date(expires_time)
                    expires = expires_time
                # Save the session data and refresh the client cookie.
                request.ms_session.save()
                response.set_cookie(MS_SESSION_COOKIE_NAME,
                        request.ms_session.session_key, max_age=max_age,
                        expires=expires, domain=MS_SESSION_COOKIE_DOMAIN,
                        path=MS_SESSION_COOKIE_PATH,
                        secure=MS_SESSION_COOKIE_SECURE or None)
        return response

