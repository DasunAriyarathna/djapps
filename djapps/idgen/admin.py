
from django.contrib import admin as djangoadmin
import models
import logging
logger = logging.getLogger(__name__)

class IDGeneratorAdmin(djangoadmin.ModelAdmin):
    search_fields = ("name", )
    list_display = ("name","gen_type","allowed_chars","key_length")

class GeneratedIDAdmin(djangoadmin.ModelAdmin):
    list_display = ("id","generator","gen_id")

try:
    djangoadmin.site.register(models.GeneratedID, GeneratedIDAdmin)
    djangoadmin.site.register(models.IDGenerator, IDGeneratorAdmin)
    djangoadmin.site.register(models.IDGeneratorSerial)
    djangoadmin.site.register(models.IDGeneratorRandom)
    djangoadmin.site.register(models.IDGeneratorLFSR)
except:
    import sys, traceback
    traceback.print_exc()
    logger.error("ID Gen Already Registered...")

