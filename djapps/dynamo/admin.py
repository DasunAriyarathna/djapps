
from models import DJCounter, DJBOBFragment

try:
    from django.contrib import admin as djangoadmin
    djangoadmin.site.register(DJCounter)
    djangoadmin.site.register(DJBOBFragment)
except:
    import sys, traceback
    traceback.print_exc()
    print >> sys.stderr, "Dynamo Models Already Registered..."

