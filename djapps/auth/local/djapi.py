from django.contrib.auth.models import User
import djmodels as models

def login(request, user):
    from django.contrib import auth
    auth.login(request, user)

def verify_uname_password(username, password):
    from django.contrib import auth
    return auth.authenticate(username = username, password = password)

def set_password(user, raw_password, save = True):
    user.set_password(raw_password)

#
# Authenticate a user
#
def authenticate(request, username, password):
    user = verify_uname_password(username, password)

    if user and user.is_active:
        login(request, user)
    return user

