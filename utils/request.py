
from djapps.utils import urls         as djurls

def get_var(request, variable, default_val = ""):
    if request.GET and variable in request.GET:
        return request.GET[variable]
    elif request.POST and variable in request.POST:
        return request.POST[variable]
    else:
        return default_val

def get_getvar(request, variable, default_val = ""):
    if request.GET and variable in request.GET:
        return request.GET[variable]
    return default_val


def get_postvar(request, variable, default_val = ""):
    if request.POST and variable in request.POST:
        return request.POST[variable]
    return default_val

