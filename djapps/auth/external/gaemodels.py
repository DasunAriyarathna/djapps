
import datetime, sys
import google
from google import appengine
from google.appengine.ext import db
from djapps.dynamo.gaehelpers import get_or_create_object, get_object_id

def get_or_create_useralias(user_id, host_site):
    aliases = UserAlias.all();
    aliases.filter("user_id = ", user_id)
    aliases.filter("host_site = ", host_site)
    if aliases.count() > 0:
        return aliases.fetch(1)[0]
    else:
        alias = UserAlias(user_id = user_id, host_site = host_site)
        alias.put()
        return alias

#
# The site which is authenticating the user.
#
# The idea is we want to use any social networking site or
# container site as a distribution channel for our apps, why
# create yet another social network???
#
class HostSite(db.Model):
    #
    # The external site name
    #
    site_name   = db.StringProperty()   # unique = True

    #
    # URL for the site
    #
    site_url    = db.LinkProperty()

    #
    # Login url of the site
    #
    site_login_url  = db.LinkProperty()

    def __str__(self):
        return self.site_name + "/" + str(self.site_url)

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
# Still to decide:
# 1. Who has controls over which sites are allowed and how are the site
# specific authentication mechanisms/data deciphered by the application?
#
# TODO:
# The primary key tuple is host_site/login_name
#
class UserAlias(db.Model):
    #
    # The host site/channel from which the user is logging in.
    #
    host_site    = db.ReferenceProperty(HostSite)

    #
    # The unique id of the user within the host this can be an email or a
    # numeric id or anything really.
    #
    user_id         = db.StringProperty()

    #
    # Last login time from the foreign site.
    #
    last_login      = db.DateTimeProperty(verbose_name = "last login", auto_now_add = True)

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


