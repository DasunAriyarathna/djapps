
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
# Another way of doing restful apis.  We create resources.  All things that
# go through a RESTful api, will subclass the Resource.
#
# Essentially our limitations on the apis are as follows:
#
# 1. /resource_name/action/<id> or
# 2. /resource_name/action or
# 3. /resource_name/<id> or
#
# In all of the above cases a few inbuilt methods are searched for.
# Following searches happen:
#
# <method>_handler_<action> method is called in case (1).  If such a method
# does not exist, then default_<method>_handler is looked for and the
# first parameter is passed as the object id instead of the action.
#
# And if neither of the above methods exist, default_handler is called
# which by default returns a Http404 error.
#
class ResourceHandler(object):
    # This class specific parameter says what method override param is
    method_param = "__method__";
    
    #
    # By default return a 404 on requests that cant be handled
    #
    @classmethod
    def default_handler(cls, request, format, action = None, objid = None):
        print "Action: ", action
        print "Object: ", objid, type(objid)
        from django.http import Http404
        return Http404()

    @classmethod
    def get_object_by_id(cls, id):
        """ All resources may have db objects.  So how they are fetched and
        constructed depends on the resource.  All That happens here.
        Override this to get a resource specific db object or item so that
        the handlers can be relieved of this extra burden.
        """
        return id

@djdecos.format_response
@djdecos.ensure_user_logged_in_for_methods("post", "put", "delete")
def auto_rest_resource_handler(request, resource, action = "", objid = "", handler_class = ResourceHandler, *args):
    format              = djrequest.get_getvar(request,
                                   settings.FORMAT_PARAM,
                                   djrequest.get_postvar(request, settings.FORMAT_PARAM, ""))
    method              = request.method.lower()
    if handler_class.method_param in request.GET:
        # Override/simulate methods not supported in the browser by
        # specifying as a get param
        method = request.GET[handler_class.method_param].lower()

    theresource = objid
    if objid:
        theresource = handler_class.get_object_by_id(objid)

    methodname = method + "_handler_" + action
    if hasattr(handler_class, methodname):
        themethod = getattr(handler_class, methodname)

        return themethod(request, format, theresource, *args)
    else:
        # otherwise there is the possibility that the action is
        # supposed to be "" and the first parameter refers to the
        # object id instead of the action - so try and find a default
        # method for taking just the object ID (with empty action).
        default_methodname = "default_" + method + "_handler"
        if hasattr(handler_class, default_methodname):
            themethod = getattr(handler_class, default_methodname)
            return themethod(request, format, theresource, *args)
        else:
            return handler_class.default_handler(request, format, action, theresource, *args)

# 
# Given a resource and a set of actions on the resource, returns the url
# patterns to cater for all those actions.
#
# TODO: Extract the available methods automatically by iterating through
# the <method>_handler_<action> functions and default_<method>_handler
# functions.
#
def get_resource_url_patterns(resource, handler_class):
    actions = {}
    for f in dir(handler_class):
        if f.find("_handler_") >= 0:
            actions[f[f.find("_handler_") + len("_handler_") : ]] = True

    pats    = []
    for action in actions:
        if action:
            params  = {'resource': resource, 'handler_class': handler_class}
            params['action'] = action
            pats += patterns("", (r'^%s/%s/(?P<objid>[^/]+)/$' % (resource, action), auto_rest_resource_handler, params))
            pats += patterns("", (r'^%s/%s/$' % (resource, action), auto_rest_resource_handler, params))

    params  = {'resource': resource, 'handler_class': handler_class}
    params['action'] = ""
    pats += patterns("", (r'^%s/(?P<objid>[^/]+)/$' % resource, auto_rest_resource_handler, params))
    pats += patterns("", (r'^%s/$' % resource, auto_rest_resource_handler, params))
    return pats

