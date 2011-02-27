
import sys, time
from django.conf import settings

if settings.USING_APPENGINE:
    from gaemodels import *
else:
    from djmodels import *

def make_useralias_id(username, gf_site):
    if gf_site:
        return "ua_" + username + "@" + gf_site.site_name.lower()
    else:
        return "ua_" + username + "@none"
