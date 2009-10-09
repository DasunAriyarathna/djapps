
from django.core import exceptions
from djapps.dynamo.helpers import get_object_id, get_object_by_id

import models, sys

SESSION_USER_ALIAS_LIST = "_session_useralias_list"
BACKEND_SESSION_KEY     = "_session_user_backend"

def load_authenticator_class(full_auth_class):
    try:
        dot = full_auth_class.rindex('.')
    except ValueError:
        raise exceptions.ImproperlyConfigured, '%s isn\'t a authenticator module' % full_auth_class

    auth_module, auth_classname = full_auth_class[:dot], full_auth_class[dot+1:]

    try:
        auth_mod = __import__(auth_module, {}, {}, [''])
    except ImportError, e:
        raise exceptions.ImproperlyConfigured, 'Error importing site authenticator %s: "%s"' % (auth_module, e)

    try:
        auth_class = getattr(auth_mod, auth_classname)
    except AttributeError:
        raise exceptions.ImproperlyConfigured,                              \
                'Authenticator module "%s" does not define a "%s" class' %  \
                    (auth_module, auth_classname)

    return auth_class

# 
# Logout a user completely...
#
def logout(request):
    if SESSION_USER_ALIAS_LIST in request.ms_session:
        del request.ms_session[SESSION_USER_ALIAS_LIST]


############  methods to deal with multiple users 

def get_user_aliases(request):
    if  (not hasattr(request, "ms_session")) or \
        SESSION_USER_ALIAS_LIST not in request.ms_session: return []

    aliaslist = request.ms_session[SESSION_USER_ALIAS_LIST]
    return [ get_object_by_id(models.UserAlias, id) for id in aliaslist ]

def login_useralias(request, ualias):
    """ Logs in and adds a user alias to the list of logged in users 
    in the current request, if it does not already exist. """
 
    if not is_useralias_logged_in(request, ualias):
        # then add the user
        aliaslist = request.ms_session[SESSION_USER_ALIAS_LIST]
        aliaslist[get_object_id(ualias)] = True
        request.ms_session[SESSION_USER_ALIAS_LIST] = aliaslist

def is_useralias_logged_in(request, ualias):
    """ Checks if a user alias exists is logged in.
    in users in the current request. """

    if SESSION_USER_ALIAS_LIST not in request.ms_session:
        request.ms_session[SESSION_USER_ALIAS_LIST] = {}
        return False

    uid = get_object_id(ualias)

    return uid in request.ms_session[SESSION_USER_ALIAS_LIST]

def logout_useralias(request, ualias):
    """ Logs out and removes a user alias from the list of 
    logged in users in the current request, if it exists. """

    if is_useralias_logged_in(request, ualias):
        del request.ms_session[SESSION_USER_ALIAS_LIST][get_object_id(ualias)]

