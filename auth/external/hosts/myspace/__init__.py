
import sys, logging, md5, urllib2
from datetime import datetime
import djapps.utils.request     as djrequtils
from django.http import HttpResponseRedirect
from djapps.auth.external.authenticators import Authenticator

try:
    from threading import local
except ImportError:
    from django.utils._thread_local import local

_thread_locals = local()

def _hash_args(args, secret=None, prefix = "oauth_signature"):
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

    for param in args.keys():
        if param != "oauth_signature":
            if param not in params:
                params[param] = []
            params[param].append(urllib2.quote(args[param]))

    for key in params.keys():
        params[key].sort()

        newlist = []
        for val in params[key]:
            newlist.append(key + "=" + val)

        params[key] = "&".join(newlist)

    params = params.items()
    params.sort()

    params = "&".join( v for k, v in params)
        

    logging.debug(" =========   ")
    logging.debug(" =========   ")
    logging.debug(" =========   Params: " + str(params) + (", Size: %d" % len(params)))
    logging.debug(" =========   ")
    logging.debug(" =========   ")

    base_string = ''.join(['%s=%s' % (isinstance(x, unicode) and x.encode("utf-8") or x, isinstance(args[x], unicode) and args[x].encode("utf-8") or args[x]) for x in sorted(params.keys())])

    return base_string
    # hasher.update(secret)
    # return hasher.hexdigest()

# 
# Tries to authenticate a request by myspace and returns a user alias
#
class AuthMySpace(Authenticator):
    MYSPACE_AUTH_TOKEN       = "auth_token"
    MYSPACE_USER_ID          = "_myspace_user_id"
    MYSPACE_SESSION_KEY      = "_myspace_session_key"
    MYSPACE_SESSION_EXPIRES  = "_myspace_session_expires"

    def __init__(self, **kwargs):
        super(AuthMySpace, self).__init__(**kwargs)
        self.consumer_key       = kwargs['MYSPACE_CONSUMER_KEY']
        self.consumer_secret    = kwargs['MYSPACE_CONSUMER_SECRET']
        self.app_name           = kwargs['MYSPACE_APP_NAME']
        self.callback_path      = "" 
        self.internal           = ""
        self.proxy              = None

    def signature_is_valid(self, request):
        return True

    def authenticate(self, request):
        if False and request.GET and self.signature_is_valid(request):
            our_sig = _hash_args(request.GET, self.consumer_secret)
        return None

