
import sys

from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect, Http404

from . import api_result
import json as djjson

JSON_CONTENT_TYPE = "application/json"
# JSON_CONTENT_TYPE = "text/html"

def format_response(func):
    """ Takes a result and converts to an appropriate response object.
        A function that uses this as a decorator, must return one of the
        following:

        1. HttpResonse or Http404 object - this will be
        returned by the decorator as is.

        2. A json object - will be stringified and returned.

        3. A json object and a path to a template, the json object will be
        rendered on the template.  

        If no object is returned by the wrapee, then this decorator does
        nothing (possibly resulting in a django exception.
    """
    def format_response_method(request, *args, **kwargs):
        result  = func(request, *args, **kwargs)

        if result is not None:
            if isinstance(result, HttpResponse):
                return result
            elif isinstance(result, Http404):
                raise result
            elif type(result) is tuple:
                import request as djrequest
                from django.conf import settings
                content_type = djrequest.get_getvar(request, "content_type", JSON_CONTENT_TYPE)
                format = djrequest.get_getvar(request,
                                              settings.FORMAT_PARAM,
                                              djrequest.get_postvar(request, settings.FORMAT_PARAM, ""))
                if format == "json" or len(result) < 2:
                    return HttpResponse(djjson.json_encode(result[0]), content_type = content_type)
                else:
                    from django.template import RequestContext
                    context = RequestContext(request)
                    return render_to_response(result[1], result[0], context)
            import request as djrequest
            content_type = djrequest.get_getvar(request, "content_type", JSON_CONTENT_TYPE)
            return HttpResponse(djjson.json_encode(result), content_type = content_type)
    return format_response_method

# 
# A decorator for ensuring that a method in the request confirms to what is
# in a given list.
#
def ensure_request_type(*methods):
    def ensure_request_type_decorator(func):
        def ensure_request_type_method(request, *args, **kws):
            if methods and request.method not in methods:

                return api_result(-1, "Invalid method type: '%s'" % method)

            return func(request, *args, **kws)

        return ensure_request_type_method
    return ensure_request_type_decorator

# 
# Sends a "unauthenticated" response for a given request.
# Usually this will be called from a decorator or a request handler if
# authentication is required but was not valid or successful.
# This automatically takes care of the format - ie if we are in API mode,
# then a json object is sent, otherwise a redirection to the login_url is
# made.
#
def send_unauthenticated_response(request, *args, **kwds):
    from django.conf import settings
    import request as djrequest
    import urls as djurls
    format = djrequest.get_getvar(request,
                                  settings.FORMAT_PARAM,
                                  djrequest.get_postvar(request, settings.FORMAT_PARAM, ""))
    if format == "json":
        return api_result(-1, "Unable to authenticate user.")
    else:
        return HttpResponseRedirect(djurls.get_login_url(request.path))
    
# 
# Apply an authentication function instead of simply 
# checking for method types
#
def ensure_user_authenticated(auth_function):
    def ensure_user_authenticated_decorator(func):
        def ensure_user_authenticated_method(request, *args, **kwds):
            if auth_function and not auth_function(request, *args, **kwds):
                return send_unauthenticated_response(request, *args, **kwds)
            else:
                return func(request, *args, **kws)
        return ensure_user_authenticated_method
    return ensure_user_authenticated_decorator
                
# 
# Same as the ensure_user_authenticated but applies to a class or
# instance method instead of a global method.
#
def ensure_user_authenticated_im(auth_function):
    def ensure_user_authenticated_decorator(func):
        def ensure_user_authenticated_method(scope, request, *args, **kwds):
            if auth_function and not auth_function(scope, request, *args, **kwds):
                return send_unauthenticated_response(scope, request, *args, **kwds)
            else:
                return func(scope, request, *args, **kws)
        return ensure_user_authenticated_method
    return ensure_user_authenticated_decorator

# 
# A decorator for ensuring the user is logged in for given methods.  Eg we
# may require that POST and PUT methods require user login however GET may
# not.  
#
# This is simply a wrapper for the generic authentication decorator that
# to simply see if the request's method type confirms to the ones we allow
# to be unauthenticated.
#
def ensure_user_logged_in_for_methods(*methods):
    def auth_function(request, *args, **kwds):
        return not methods or request.method.lower() in methods
    return ensure_user_authenticated(auth_function)

