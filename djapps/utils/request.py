
from djapps.utils import urls as djurls
import djapps.utils as djutils

def dict_from_request(request, get_has_priority = True):
    filters = {}
    if get_has_priority:
        if request.POST:
            filters = dict(request.POST.items())
        filters.update(dict(request.GET.items()))
    else:
        filters = dict(request.GET.items())
        if request.POST:
            filters.update(dict(request.POST.items()))
    return djutils.to_str_keys(filters)

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

