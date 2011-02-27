
from models import IDGenerator, GeneratedID, IDGeneratorRandom, IDGeneratorLFSR
from django.contrib import admin as djangoadmin

class IDGeneratorAdmin(djangoadmin.ModelAdmin):
    list_display = ("name","gen_type","allowed_chars","key_length")

try:
    djangoadmin.site.register(IDGenerator, IDGeneratorAdmin)
    djangoadmin.site.register(IDGeneratorRandom)
    djangoadmin.site.register(IDGeneratorLFSR)
    djangoadmin.site.register(GeneratedID)
except:
    import sys, traceback
    traceback.print_exc()
    print >> sys.stderr, "ID Gen Already Registered..."

