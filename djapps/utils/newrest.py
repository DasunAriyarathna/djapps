

import sys
from django.conf import settings
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.conf.urls.defaults import *

import  decorators      as  djdecos
import  request         as  djrequest
from    .       import      api_result

#
# This is an experimental new way to have handlers to requests
# The problem so far is that in the ResourceHandler method, we auto create
# url patterns based on the the class methods beginning with handler_.
# While this is good to auto-detect actions based on method names, there
# are cases where we want to use "class" of actions by grouping them to
# specifically handcrafted urls - which may be more descriptive and
# expressive. Especially in urls with multiple ids eg:
# /a/<id>/b/<id>/create cant be created with ResourceHandler classes.
#
# The advantage of RH classes however is that it allows clean inheritance.
# The same can be acheived here by passing extra functions but this could
# become unweildy.
#
# Alternatively, we could use ResourceHandler or similiar classes but
# generate the urls manually.  This would allow inheritances as well as
# allow handler methods whose signatures are completely customized to each
# handler type with a direct correspondence with parameters in the url
# pattern!
#
@djdecos.format_response
def manual_resource_handler(request, handler_class, handler_suffix,
                            method_param = "__method__", *args, **kwargs):
    format = djrequest.get_var(request, settings.FORMAT_PARAM)
    method = request.method
    if method_param in request.GET:
        # Override/simulate methods not supported in the browser by
        # specifying as a get param
        method = request.GET[method_param]

    themethod = handler_class.handler_for_method(method, handler_suffix)
    return themethod(request, format, *args, **kwargs)

def resturl(regex, handler_class, suffix,
            kwargs = None, name = None, prefix='',
            handler_function = manual_resource_handler):
    if not kwargs: kwargs = {}
    kwargs['handler_class']     = handler_class
    kwargs['handler_suffix']    = suffix
    return url(regex, handler_function, kwargs, name, prefix)

class DefaultRestHandler(object):
    """
    An OO style accessor for the resturl
    """
    @classmethod
    def handler_for_method(handler_class, method, handler_suffix, use_default = True, raise_on_no_method = True):
        method = method.strip().lower()
        methodname = method + "_handler_" + handler_suffix
        themethod = getattr(handler_class, methodname, None)
        if use_default and not themethod:
            # fall back to default_handler_....
            methodname  = "default_handler_" + handler_suffix
            themethod   = getattr(handler_class, methodname, None)
        if raise_on_no_method and not themethod:
            from django.http import Http404
            raise Http404
        return themethod

    @classmethod
    def RestUrl(cls, regex, suffix, kwargs = None, name = None, prefix=''):
        get_method = cls.handler_for_method("get", suffix, False, False)
        post_method = cls.handler_for_method("post", suffix, False, False)
        default_method = cls.handler_for_method("default", suffix, False, False)
        def real_handler(request, handler_class, handler_suffix,
                         method_param = "__method__", *args, **kwargs):
            return manual_resource_handler(request, handler_class, handler_suffix,
                                           method_param, *args, **kwargs)
        real_handler.__getdoc__ = get_method and get_method.__doc__ or ""
        real_handler.__postdoc__ = post_method and post_method.__doc__ or ""
        real_handler.__doc__ = default_method and default_method.__doc__ or ""
        return resturl(regex, cls, suffix, kwargs, name, prefix, handler_function = real_handler)

