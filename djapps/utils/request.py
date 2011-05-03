
from djapps.utils import urls         as djurls

def get_getvar(request, variable, default = "", converter = None):
    if request.GET and variable in request.GET:
        if converter:
            return converter(request.GET[variable])
        else:
            return request.GET[variable]
    return default


def get_postvar(request, variable, default = "", converter = None):
    if request.POST and variable in request.POST:
        if converter:
            return converter(request.POST[variable])
        else:
            return request.POST[variable]
    return default


def get_var(request, variable, default = "", converter = None):
    if request.GET and variable in request.GET:
        if converter:
            return converter(request.GET[variable])
        else:
            return request.GET[variable]
    elif request.POST and variable in request.POST:
        if converter:
            return converter(request.POST[variable])
        else:
            return request.POST[variable]
    else:
        return default

