
import sys, time, logging
from django.conf import settings
from django.utils.cache import patch_vary_headers

from djapps.utils.sessions import get_session
from djapps.auth.openid import OpenIDContext

# Name of the MS Session Cookie
OPENID_SESSION_COOKIE_NAME          = 'openid_sessionid'                                    
if hasattr(settings, "OPENID_SESSION_COOKIE_NAME"):
    OPENID_SESSION_COOKIE_NAME      = session.OPENID_SESSION_COOKIE_NAME

OPENID_SESSION_COOKIE_ACTIVE_ALIAS  = 'activeUserAlias'                                    
if hasattr(settings, "OPENID_SESSION_ACTIVE_ALIAS"):
    OPENID_SESSION_COOKIE_ACTIVE_ALIAS     = session.OPENID_SESSION_COOKIE_ACTIVE_ALIAS

# Age of cookie, in seconds (default: 2 weeks).
OPENID_SESSION_COOKIE_AGE           = settings.SESSION_COOKIE_AGE
if hasattr(settings, "OPENID_SESSION_COOKIE_AGE"):
    OPENID_SESSION_COOKIE_AGE       = settings.OPENID_SESSION_COOKIE_AGE

# A string like ".lawrence.com", or None for standard domain cookie.
OPENID_SESSION_COOKIE_DOMAIN        = settings.SESSION_COOKIE_DOMAIN
if hasattr(settings, "OPENID_SESSION_COOKIE_DOMAIN"):
    OPENID_SESSION_COOKIE_DOMAIN    = settings.OPENID_SESSION_COOKIE_DOMAIN

# Whether the ms session cookie should be secure (https:// only).
OPENID_SESSION_COOKIE_SECURE    = settings.SESSION_COOKIE_SECURE
if hasattr(settings, "OPENID_SESSION_COOKIE_SECURE"):
    OPENID_SESSION_COOKIE_SECURE    = settings.OPENID_SESSION_COOKIE_SECURE

# The path of the ms session cookie.
OPENID_SESSION_COOKIE_PATH          = "/"
if hasattr(settings, "OPENID_SESSION_COOKIE_PATH"):
    OPENID_SESSION_COOKIE_PATH      = settings.OPENID_SESSION_COOKIE_PATH

# Whether a user's ms session cookie expires when the Web browser is closed.
OPENID_SESSION_EXPIRE_AT_BROWSER_CLOSE = settings.SESSION_EXPIRE_AT_BROWSER_CLOSE
if hasattr(settings, "OPENID_SESSION_EXPIRE_AT_BROWSER_CLOSE"):
    OPENID_SESSION_EXPIRE_AT_BROWSER_CLOSE  = settings.OPENID_SESSION_EXPIRE_AT_BROWSER_CLOSE

if not settings.USING_APPENGINE:
    # The module to store session data
    OPENID_SESSION_ENGINE           = settings.SESSION_ENGINE
    if hasattr(settings, "OPENID_SESSION_ENGINE"):
        OPENID_SESSION_ENGINE       = settings.OPENID_SESSION_ENGINE

    # Directory to store session files if using the file session module. If
    # None, the backend will use a sensible default.
    OPENID_SESSION_FILE_PATH        = settings.SESSION_FILE_PATH
    if hasattr(settings, "OPENID_SESSION_FILE_PATH"):
        OPENID_SESSION_FILE_PATH        = settings.OPENID_SESSION_FILE_PATH

class LazyOpenIDContext(object):
    """ A lazy descriptor that will fetch the openid context tied into a
    particular request/session.
    """
    def __get__(self, request, obj_type = None):
        if not hasattr(request, '_cached_openid_context'):
            request._cached_openid_context = OpenIDContext(request)
        return request._cached_openid_context

# 
# This middleware object allows us to leverage authentication of a user
# from one of the several trusted sites, (including ourselves).
#
class OpenIDAuthMiddleware(object):
    def __init__(self):
        pass

    def process_request(self, request):
        # create a new session object ONLY for the openid stuff so we
        # dont have to use the session that is already created!

        request.openid_session              = get_session(OPENID_SESSION_COOKIE_NAME, request.COOKIES)
        request.__class__.openid_context    = LazyOpenIDContext()

        # use the old request (though possibly modified)
        return None

    def process_response(self, request, response):
        # now save the openid session
        # If request.openid_session was modified, or if response.session was set, save
        # those changes and set a session cookie.
        try:
            accessed = request.openid_session.accessed
            modified = request.openid_session.modified
        except AttributeError:
            pass
        else:
            if accessed:
                patch_vary_headers(response, ('Cookie',))
            if modified or settings.SESSION_SAVE_EVERY_REQUEST:
                if request.openid_session.get_expire_at_browser_close():
                    max_age = None
                    expires = None
                else:
                    max_age = request.openid_session.get_expiry_age()
                    expires_time = time.time() + max_age
                    # expires = cookie_date(expires_time)
                    expires = expires_time
                # Save the session data and refresh the client cookie.
                request.openid_session.save()
                response.set_cookie(OPENID_SESSION_COOKIE_NAME,
                        request.openid_session.session_key, max_age=max_age,
                        expires=expires, domain=OPENID_SESSION_COOKIE_DOMAIN,
                        path=OPENID_SESSION_COOKIE_PATH,
                        secure=OPENID_SESSION_COOKIE_SECURE or None)
        return response

