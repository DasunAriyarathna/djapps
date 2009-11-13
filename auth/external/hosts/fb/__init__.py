
import sys, logging, md5
from datetime import datetime
import djapps.utils.request     as djrequtils
from django.http import HttpResponse
from djapps.auth.external.authenticators import Authenticator
from djapps.dynamo.helpers import get_or_create_object, get_first_object

try:
    from threading import local
except ImportError:
    from django.utils._thread_local import local

_thread_locals = local()

SESSION_USER_ALIAS_LIST = "_session_useralias_list"

# 
# Tries to authenticate a request by facebook and returns a user alias
#
class AuthFacebook(Authenticator):
    FB_AUTH_TOKEN       = "auth_token"
    FB_SIGNATURE        = "_fb_sig"
    FB_USER_ID          = "_fb_user"
    FB_SESSION_KEY      = "_fb_session_key"
    FB_SESSION_SECRET   = "_fb_session_secret"
    FB_SESSION_EXPIRES  = "_fb_session_expires"
    FB_SESSION_DELETE   = "_fb_session_delete"

    def __init__(self, **kwargs):
        super(AuthFacebook, self).__init__(**kwargs)
        self.api_key            = kwargs['FACEBOOK_API_KEY']
        self.secret_key         = kwargs['FACEBOOK_SECRET_KEY']
        self.app_name           = kwargs['FACEBOOK_APP_NAME']
        self.callback_path      = "" # kwargs['FACEBOOK_CALLBACK_PATH']
        self.internal           = ""
        self.proxy              = None

    def _hash_args(self, args, secret=None, prefix = "fb_sig"):
        """
        Hashes arguments by joining key=value pairs, appending a secret,
        and then taking the MD5 hex digest.  Taken shamelessly from
        pyfacebook!  Has the advantage of passing a prefix which is to be
        ignored - since signatures from FB canvases have a prefix of
        'fb_sig' whereas signatures set by cookies via FB Connect have the
        api_key as the prefix.
        """
        # get the parameters for the sig calculation 
        # to see if the signature is correct
        params = {}
        SIG_LEN = len(prefix + "_")
        for param in args.keys():
            if param.startswith(prefix + "_"):
                params[param[SIG_LEN:]] = args[param]

        args = params

        hasher = md5.new(''.join(['%s=%s' % (isinstance(x, unicode) and x.encode("utf-8") or x, isinstance(args[x], unicode) and args[x].encode("utf-8") or args[x]) for x in sorted(args.keys())]))

        if secret:
            hasher.update(secret)
        elif self.secret_key:
            hasher.update(self.secret_key)
        return hasher.hexdigest()

    def authenticate(self, request):
        request.set_fb_cookies      = None
        request.delete_fb_session   = False

        fb_user = None
        fb_sig = djrequtils.get_getvar(request, "fb_sig", "")
        fb_logged_out = djrequtils.get_getvar(request, "fb_sig_logged_out_facebook", "")

        if fb_logged_out:
            request.delete_fb_session   = True
            return None

        if not fb_sig:
            # this request is not by FB, however do not logout an already
            # logged in user so just return existing user
            # But can this be faked? no since it is stored in the server
            # and cannot get here easily

            # try fb connect
            fb_user = self.authenticate_fb_connect(request)

            if not fb_user:
                if self.FB_USER_ID in request.ms_session:
                    fb_user = request.ms_session[self.FB_USER_ID]
                else:
                    request.delete_fb_session   = True
        else:
            fb_user = self.authenticate_new_profile(request)
            if not fb_user:
                # try the old profile
                fb_user = self.authenticate_old_profile(request)

            if fb_user:   
                request.set_fb_cookies = {}

                # set the cookies on the client so it can 
                # be validated the next time as a fbconnect 
                # request
                request.set_fb_cookies[self.api_key + "_user"]          = request.ms_session[self.FB_USER_ID]
                request.set_fb_cookies[self.api_key + "_expires"]       = request.ms_session[self.FB_SESSION_EXPIRES]
                request.set_fb_cookies[self.api_key + "_ss"]            = request.ms_session[self.FB_SESSION_SECRET]
                request.set_fb_cookies[self.api_key + "_session_key"]   = ""
                if self.FB_SESSION_KEY in request.ms_session:
                    request.set_fb_cookies[self.api_key + "_session_key"]   = request.ms_session[self.FB_SESSION_KEY]

                request.set_fb_cookies[self.api_key]                    = self._hash_args(request.set_fb_cookies, self.secret_key, self.api_key)
            
        return fb_user

    def authenticate_old_profile(self, request):
        """ Authenticates a FB app from the old design. """
        auth_token      = djrequtils.get_getvar(request, "auth_token", None)

        if auth_token:
            if self.FB_AUTH_TOKEN not in request.ms_session or request.ms_session[self.FB_AUTH_TOKEN] != auth_token:
                # we have different auth token this time, so this is a new 
                # session
                import facebook
                request.facebook                            = facebook.Facebook(self.api_key, self.secret_key)
                check_session                               = request.facebook.check_session(request)
                request.ms_session[self.FB_AUTH_TOKEN]         = auth_token
                request.ms_session[self.FB_USER_ID]            = request.facebook.uid
                request.ms_session[self.FB_SESSION_KEY]        = request.facebook.session_key
                request.ms_session[self.FB_SESSION_EXPIRES]    = request.facebook.session_key_expires

                return request.facebook.uid

        return None

    def authenticate_fb_connect(self, request):
        """ Authenticates using FB Connect. """

        # is there a FB cookie in here?
        if self.api_key in request.COOKIES:
            signature_hash = self._hash_args(request.COOKIES, self.secret_key, self.api_key)

            fb_expires  = request.COOKIES[self.api_key + '_expires']

            if  signature_hash == request.COOKIES[self.api_key] and     \
                (datetime.fromtimestamp(float(fb_expires)) > datetime.now()):
                # hashes match and time stamp hasnt expired 
                # so return the user

                fb_user         = request.COOKIES[self.api_key + "_user"]
                fb_session_key  = request.COOKIES[self.api_key + "_session_key"]

                request.ms_session[self.FB_USER_ID]        = fb_user
                request.ms_session[self.FB_SESSION_KEY]    = fb_session_key
                request.ms_session[self.FB_SESSION_SECRET] = request.COOKIES[self.api_key + "_ss"]
                request.ms_session[self.FB_SIGNATURE]      = signature_hash

                if fb_expires:
                    request.ms_session[self.FB_SESSION_EXPIRES]    = fb_expires

                return fb_user

        return None

    def authenticate_new_profile(self, request):
        """ Authenticates a FB app from the new design. """

        fb_sig = djrequtils.get_getvar(request, "fb_sig", "")
        our_sig = self._hash_args(request.GET, self.secret_key, "fb_sig")

        if  fb_sig == our_sig:
            # Signatures dont match so fail authentication

            fb_user     = djrequtils.get_getvar(request, "fb_sig_user", None) or    \
                          djrequtils.get_getvar(request, "fb_sig_canvas_user", None)

            # what if fb_user is invalid here?
            # so we are really from facebook.  where to go from here?
            # if the userid does not exist it means the user has not added
            # the page - need to show something generic but facebook
            # specific.

            if fb_user:
                fb_session_key  = djrequtils.get_getvar(request, "fb_sig_session_key", None)
                fb_expires      = djrequtils.get_getvar(request, "fb_sig_expires", "")
                fb_ss           = djrequtils.get_getvar(request, "fb_sig_ss", "")

                request.ms_session[self.FB_USER_ID]            = fb_user
                request.ms_session[self.FB_SESSION_SECRET]     = fb_ss
                request.ms_session[self.FB_SIGNATURE]          = fb_sig
                request.ms_session[self.FB_SESSION_EXPIRES]    = fb_expires

                if fb_session_key:
                    request.ms_session[self.FB_SESSION_KEY]        = fb_session_key

                return fb_user

        return None

    def processResponse(self, request, response):
        """ Deletes FB cookies if marked for deletion. """
        if (hasattr(request, 'ms_session') and SESSION_USER_ALIAS_LIST not in request.ms_session) or \
           (hasattr(request, 'delete_fb_session') and request.delete_fb_session):
            response.delete_cookie(self.api_key + '_user')
            response.delete_cookie(self.api_key + '_session_key')
            response.delete_cookie(self.api_key + '_expires')
            response.delete_cookie(self.api_key + '_ss')
            response.delete_cookie(self.api_key)
            response.delete_cookie('fbsetting_' + self.api_key)
        elif hasattr(request, "set_fb_cookies") and request.set_fb_cookies:
            for key in request.set_fb_cookies.keys():
                cookie_key = str(key)
                cookie_val = str(request.set_fb_cookies[key])
                print >> sys.stderr, "============Setting FB Cookies: ", cookie_key, cookie_val
                response.set_cookie(cookie_key, cookie_val)

        # request.ms_session[self.FB_SESSION_DELETE] = False
        request.delete_fb_session   = False
        request.set_fb_cookies      = None

    def logout(self, request):
        """ Called to cleanup any cookies/session variables we may have created. """
        for key in (self.FB_AUTH_TOKEN,
                    self.FB_SIGNATURE,
                    self.FB_USER_ID,
                    self.FB_SESSION_KEY,
                    self.FB_SESSION_SECRET,
                    self.FB_SESSION_EXPIRES):
            if key in request.ms_session:
                del request.ms_session[key]


        # mark the session cookies to be deleted
        # request.ms_session[self.FB_SESSION_DELETE] = True
        request.delete_fb_session = True
        request.ms_session.save()
