from django.conf import settings

if settings.USING_APPENGINE:
    from gaeapi import *
else:
    from djapi import *

