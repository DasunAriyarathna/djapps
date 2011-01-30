
#################   Register Models with Admin ####################

from models import HostSite, UserLogin
from django.contrib import admin as djangoadmin
djangoadmin.site.register(HostSite)
djangoadmin.site.register(UserLogin)

