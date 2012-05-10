
from models import DJCounter

try:
    from django.contrib import admin as djangoadmin
    djangoadmin.site.register(DJCounter)
except:
    import sys, traceback
    traceback.print_exc()
    print >> sys.stderr, "Dynamo Models Already Registered..."

