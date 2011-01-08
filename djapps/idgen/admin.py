
from models import IDGenerator, GeneratedID, IDGeneratorRandom, IDGeneratorLFSR
from django.contrib import admin as djangoadmin

try:
    djangoadmin.site.register(IDGenerator)
    djangoadmin.site.register(IDGeneratorRandom)
    djangoadmin.site.register(IDGeneratorLFSR)
    djangoadmin.site.register(GeneratedID)
except:
    import sys, traceback
    traceback.print_exc()
    print >> sys.stderr, "ID Gen Already Registered..."

