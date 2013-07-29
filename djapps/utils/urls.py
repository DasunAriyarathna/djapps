from django.conf.urls import *
from django.conf import settings

########################  Standard URLS ############################

def get_site_url():
    """ Gets the name of the site. """
    return getattr(settings, "SITE_URL", "")
    """
    if settings and hasattr(settings, "SITE_URL"):
        re
        if settings.SITE_URL.startswith("http://") or settings.SITE_URL.startswith("https://"):
            return settings.SITE_URL
        else:
            return "http://" + settings.SITE_URL
    else:
        return ""
    """

#
# Returns a full url based on our site id and url path prefix
#
def make_url(path = ""):
    return "/" + settings.URL_PATH_PREFIX + path

#
# Gets the URL we use for our logging in.
#
def get_login_url(fwd_url = None):
    return make_account_url("login", fwd_url)

#
# Gets the URL we use for managing links.
#
def get_manage_logins_url(fwd_url = None):
    return make_account_url("manage", fwd_url)

#
# Gets the URL we use for our logging out
#
def get_logout_url(fwd_url = None):
    return make_account_url("logout", fwd_url)

#
# Gets the registration page.
#
def get_register_url(fwd_url = None):
    return make_account_url("register", fwd_url)

#
# Gets the registration confirmation URL.
#
def get_reg_confirm_url(fwd_url = None):
    return make_account_url("confirm", fwd_url)

#
# More helpers for making account based URLs
#
def make_account_url(action, fwd_url, prefix = "accounts/"):
    out_url = prefix + action

    if fwd_url:
        out_url += ("?next=" + fwd_url)

    return make_url(out_url)
