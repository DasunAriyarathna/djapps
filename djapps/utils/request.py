
import urlparse
from djapps.utils import urls as djurls
import djapps.utils as djutils

def dict_from_request(request, get_has_priority = True):
    """
    Returns a dict with merged GET and POST parameters.
    If get_has_priority is True GET overrides POST else the other way round.
    """
    def get_post_data_as_dict(request):
        if request.POST:
            return query_dict_items(request.POST)
        elif request.body:
            return dict(urlparse.parse_qsl(request.body))
        return {}

    if get_has_priority:
        params = get_post_data_as_dict(request)
        params.update(query_dict_items(request.GET))
        return params
    
    params = query_dict_items(request.GET)
    params.update(get_post_data_as_dict(request))
    return params

def query_dict_items(qdict):
    items = qdict.lists()
    out = {}
    for k,l in qdict.lists():
        out[k] = len(l) > 1 and l or l[0]
    return out

def get_getvar(request, variable, default = "", converter = None, **converter_args):
    if request.GET and variable in request.GET:
        if converter:
            return converter(request.GET[variable], **converter_args)
        else:
            return request.GET[variable]
    return default


def get_postvar(request, variable, default = "", converter = None, **converter_args):
    if request.POST and variable in request.POST:
        if converter:
            return converter(request.POST[variable], **converter_args)
        else:
            return request.POST[variable]
    return default


def get_var(request, variable, default = "", converter = None, **converter_args):
    if request.GET and variable in request.GET:
        if converter:
            return converter(request.GET[variable], **converter_args)
        else:
            return request.GET[variable]
    elif request.POST and variable in request.POST:
        if converter:
            return converter(request.POST[variable], **converter_args)
        else:
            return request.POST[variable]
    else:
        return default

