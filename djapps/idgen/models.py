from django.conf import settings

if settings.USING_APPENGINE:
    from gaemodels import *
else:
    from djmodels import *

