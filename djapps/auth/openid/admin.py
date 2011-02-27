
from models import Association, UsedNonce
from django.contrib import admin as djangoadmin

try:
    djangoadmin.site.register(Association)
    djangoadmin.site.register(UsedNonce)
except:
    import sys, traceback
    traceback.print_exc()
    print >> sys.stderr, "OpenID Models Already Registered..."

