import datetime, sys
import gaemodels as models
from djapps.dynamo.gaehelpers import get_or_create_object
from djapps.dynamo.helpers import get_first_object

SESSION_KEY = '_auth_user_id'

def get_current_local_user(request):
    user = None
    if SESSION_KEY in request.session:
        userkey = request.session[SESSION_KEY]
        user = models.LocalUser.get(userkey)
    return user

def get_session_id(request):
    if hasattr(request, "session") and SESSION_KEY in request.session:
        return request.session[SESSION_KEY]
    return None

def login(request, local_user):
    local_user.last_login = datetime.datetime.now()
    local_user.put()

    if SESSION_KEY in request.session:
        if request.session[SESSION_KEY] != local_user.key():
            # To avoid reusing another user's session, create a new, empty
            # session if the existing session corresponds to a different
            # authenticated user.
            request.session.flush()
    else:
        request.session.cycle_key()
    request.session[SESSION_KEY] = local_user.key()
    if hasattr(request, 'local_user'):
        request.local_user = local_user

def verify_uname_password(username, password):
    user   = get_first_object(models.LocalUser, username = username)
    if user:
        algo, salt, hsh = user.algo, user.salt, user.hash
        if hsh == models.get_hexdigest(algo, salt, password):
            return user
            
    return None

def set_password(user, raw_password, save = True):
    import random
    user.algo           = 'sha1'
    user.salt           = models.get_hexdigest(user.algo, str(random.random()), str(random.random()))[:5]
    user.hash           = models.get_hexdigest(user.algo, user.salt, raw_password)
    if save: user.put()

#
# Authenticate a user
#
def authenticate(request, username, password):
    user = verify_uname_password(username, password)

    if user and user.is_active:
        login(request, user) 

    return user
