
from models import DJCounter
import logging ; logger = logging.getLogger(__name__)

try:
    from django.contrib import admin as djangoadmin
    djangoadmin.site.register(DJCounter)
except:
    import sys, traceback
    traceback.print_exc()
    logger.error("Dynamo Models Already Registered.")

