
from django.db import models
from django.db import transaction
from django.contrib.auth.models import User, Group, Permission
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings
import datetime

# 
# The site which is authenticating the user.  This can also be local sites.
#
class HostSite(models.Model):
    #
    # PK name for easier access - same as the site_name
    #
    key_name = models.CharField(max_length = 64, primary_key = True)

    # 
    # The external site name
    #
    site_name   = models.CharField(max_length = 64, unique = True)

    # 
    # URL for the site
    #
    site_url    = models.URLField(max_length = 256)

    # 
    # Login url of the site
    #
    site_login_url  = models.URLField(max_length = 512)

    def __str__(self):
        return self.site_name + "/" + str(self.site_url)

    # Admin Interface
    class Admin: save_on_top = True

    # 
    # Returns a json representation
    #
    def toJson(self):
        return {'id': get_object_id(self),
                'site_name': self.site_name,
                'site_url': self.site_url}

# 
# The per-site login of a user.  For each request, this object provides
# authentication attributes for that site.  We can have authentication
# items for more than one site.  
#
# The idea is that we separate the authentication from the actual user
# management.  We will maintain a user profile object that is 
#
class UserLogin(models.Model):
    #
    # PK name for easier access - same as the site_name
    #
    key_name    = models.CharField(max_length = 128, primary_key = True)

    # 
    # The host site/channel from which the user is logging in.
    #
    host_site   = models.ForeignKey(HostSite)

    # 
    # The unique id of the user within the host site.
    # This can be an email or a numeric id or anything really.
    #
    user_id     = models.CharField(max_length = 64)

    #
    # The djano User object that this login actually refers to.
    #
    user_model  = models.ForeignKey(User, null = True, blank = True)

    # 
    # Last login time from the foreign site.
    #
    last_login  = models.DateTimeField(_('last login'), default=datetime.datetime.now)

    def __str__(self):
        return self.user_id + "@" + self.host_site.site_name

    # 
    # Returns a json representation
    #
    def toJson(self):
        return {'id': get_object_id(self),
                'user_id': self.user_id,
                'host_site': get_object_id(self.host_site) if self.host_site else None,
                'last_login': self.last_login.strftime("%H:%M %d %h %y")}

    # Admin Interface
    class Admin: save_on_top = True
    class Meta:
        # game/user are a unique primary key
        unique_together = ("user_id", "host_site")
        verbose_name = "User Login"

