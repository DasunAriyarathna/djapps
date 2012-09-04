
import datetime

from django.db.models import Q
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context, loader
from djapps.utils import json_encode

# Get the output format from a given request.
#
# If none, then return none, but never an exception
#
def GetOutputFormat(request, fmt_spec = 'format'):
    try:
        return request.GET[fmt_spec]
    except:
        pass

    return None

#
# Checks if user is authenticated and that the request method matches
#
# Returns None if checks passed,
# otherwise an api_failure is returned.
#
def CheckAuthAndReqMethod(request, method = None):
    reqmethod   = request.method

    if not request.user.is_authenticated():
        return api_failure(-1, "User not authenticated")

    elif method is not None and (reqmethod is None or reqmethod != method):
        return api_failure(-1,
                           "Request MUST be a %s method.  %s provided instead." %
                           (method, reqmethod))

    return None

#
# Remove duplicates in a list
# Warning - list WILL be sorted
#
def remove_duplicates(list, compfunc = None):
    if len(list) == 0:
        return
    last = list[-1]
    if compfunc is None:
        list.sort()
        for i in range(len(list) - 2, -1, -1):
            if last == list[i]:
                del list[i]
            else:
                last = list[i]
    else:
        list.sort(compfunc)
        for i in range(len(list) - 2, -1, -1):
            if compfunc(last, list[i]) == 0:
                del list[i]
            else:
                last = list[i]

