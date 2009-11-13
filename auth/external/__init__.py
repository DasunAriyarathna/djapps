
from django.core import exceptions
from djapps.dynamo.helpers import get_object_id, get_object_by_id

import models, sys

SESSION_USER_ALIAS_LIST = "_session_useralias_list"
BACKEND_SESSION_KEY     = "_session_user_backend"

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

