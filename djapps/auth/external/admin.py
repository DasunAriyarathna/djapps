
#################   Register Models with Admin ####################

from django.contrib import admin as djangoadmin
djangoadmin.site.register(HostSite)
djangoadmin.site.register(UserAlias)
djangoadmin.site.register(ExternalUser)

