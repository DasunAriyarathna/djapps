
from django.db import models
from django.db import transaction
from django.contrib import admin as djangoadmin
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings
import datetime

def get_or_create_useralias(user_id, host_site):
    ualias, newcreated = UserAlias.objects.get_or_create(user_id = user_id, host_site = host_site)
    return ualias

# 
# The site which is authenticating the user.
#
# The idea is we want to use any social networking site or 
# container site as a distribution channel for our apps, why 
# create yet another social network???
#
class HostSite(models.Model):
    #
    # PK name for easier access - same as the site_name
    #
    key_name = models.CharField(max_length = 64, primary_key = True)

    # 
    # The external site name
    #
    site_name   = models.CharField(max_length = 64)

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

    class Meta:
        verbose_name_plural = "Foreign Sites"

    # 
    # Admin Interface
    #
    class Admin:
        save_on_top = True

# 
# The per-site login of a user.  For each request, this object provides
# authentication attributes for that site.  We can have authentication
# items for more than one site.  
#
# The idea is that we separate the authentication from the actual user
# management.  We will maintain a user profile object that is 
#
# Still to decide:
# 1. Who has controls over which sites are allowed and how are the site
# specific authentication mechanisms/data deciphered by the application?
#
# TODO:
# The primary key tuple is host_site/login_name
#
class UserAlias(models.Model):
    #
    # PK name for easier access - same as the site_name
    #
    key_name = models.CharField(max_length = 128, primary_key = True)

    # 
    # The host site/channel from which the user is logging in.
    #
    host_site    = models.ForeignKey(HostSite)

    # 
    # The unique id of the user within the host this can be an email or a
    # numeric id or anything really.
    #
    user_id         = models.CharField(max_length = 64)

    # 
    # Last login time from the foreign site.
    #
    last_login      = models.DateTimeField(_('last login'), default=datetime.datetime.now)

    # 
    # game/user are a unique primary key
    #
    unique_together = ("user_id", "host_site")

    def __str__(self):
        return self.user_id + "@" + self.host_site.site_name

    class Meta:
        verbose_name_plural = "User Aliases"

    # 
    # Admin Interface
    #
    class Admin:
        save_on_top = True

# 
# A class that maintains the status of similirities between two user
# profiles.
#
# This works as follows:
#
# User Afb logs in from FaceBook
# user Ams logs in from MySpace
#
#
# Ams "selects" Afb and clicks on "that is also me"
#
# Since Afb and Ams have logged in from two different networks, a message
# is sent to Afb requesting confirmation - so Afb can accept this
# "linkage" from FB or from the local site (ie via fb connect).
#
# Once Afb accepts the linkage, Ams's profile is deleted and will now point
# to Afb.
#
# What if:
#
# 1. Bfb also connects and says he is same as Afb - 
#   we can 
#   a: disallow this claiming that both are from the same network.
#   b: allow it and treat Afb and Bfb as the same user - since they point
#      to the same user anyway but not care how they are used - it does not
#      add any technical overhead anyway as only one user profile will be
#      read.
#
# 2. Bfb logs in and says he is same as Ams.  We could do a parent check
# and deduce that Afb is hence Bfb and follow the same strategy as in (1).
# For now we will allow these.
#
class AliasLinkage(models.Model):
    # 
    # The user initiating the similiarity linkage
    #
    alias1  =   models.ForeignKey(UserAlias, related_name = "initiator")

    # 
    # The user accepting the similiarity linkage
    #
    alias2  =   models.ForeignKey(UserAlias, related_name = "acceptor")

    # 
    # Yay or Nay
    #
    response    = models.BooleanField()

#################   Register Models with Admin ####################

djangoadmin.site.register(UserAlias)
djangoadmin.site.register(HostSite)
djangoadmin.site.register(AliasLinkage)

