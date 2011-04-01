
import logging
import gaeapi
import gaemodels

#####################   Local Authentication middleware   ####################

class LazyLocalUser(object):
    def __get__(self, request, obj_type=None):
        if not hasattr(request, '_cached_local_user'):
            request._cached_local_user = gaeapi.get_current_local_user(request)
        return request._cached_local_user

class LocalAuthMiddleware(object):
    def process_request(self, request):
        assert hasattr(request, 'session'), "The local authentication middleware requires session middleware to be installed. Edit your MIDDLEWARE_CLASSES setting to insert 'gaeutils.middle.middleware.SessionMiddleware'."
        request.__class__.local_user = LazyLocalUser()
        return None

