
#################   Register Models with Admin ####################

from models import HostSite, UserAlias, ExternalUser
from django.contrib import admin as djangoadmin
djangoadmin.site.register(HostSite)
djangoadmin.site.register(UserAlias)
djangoadmin.site.register(ExternalUser)

