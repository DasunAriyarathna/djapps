
import  djapps.utils.decorators     as djdecos
import  djapps.utils.request        as djrequest
from django.http import HttpResponseRedirect, HttpResponse

@djdecos.format_response
def complete_logout(request):
    from django.contrib.auth import logout
    logout(request)

    # now multisite logout
    if hasattr(request, "ms_session"):
        request.ms_session.flush()

    next_page = djrequest.get_getvar(request, "next", "/")
    return HttpResponseRedirect(next_page or request.path)
