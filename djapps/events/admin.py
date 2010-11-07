
import logging
from models import DJSubscription, DJEvent, DJTask

try:
    from django.contrib import admin as djangoadmin
    from django.contrib.admin.sites import AlreadyRegistered
    djangoadmin.site.register(DJSubscription)
    djangoadmin.site.register(DJEvent)
    djangoadmin.site.register(DJTask)
except AlreadyRegistered, ar:
    logging.warning("Already registered...")

