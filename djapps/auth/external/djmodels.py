
from django.db import models
from django.db import transaction
from django.contrib.auth.models import Group, Permission
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings
import datetime
from djapps.dynamo.djhelpers import get_or_create_object, get_object_id

UNUSABLE_PASSWORD = '!' # This will never be a valid hash

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
    # Returns a json representation
    #
    def toJson(self):
        return {'id': get_object_id(self),
                'user_id': self.user_id,
                'host_site': get_object_id(self.host_site) if self.host_site else None,
                'last_login': self.last_login.strftime("%H:%M %d %h %y")}

class ExternalUserManager(models.Manager):
    def create_user(self, username, ext_site, password=None):
        "Creates and saves a User with the given username, e-mail and password."
        now = datetime.datetime.now()
        user = self.model(None, username = username, host_site = ext_site)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user

    def create_superuser(self, username, host_site, password):
        u = self.create_user(username, host_site, password)
        u.is_staff = True
        u.is_active = True
        u.is_superuser = True
        u.save()
        return u

    def make_random_password(self, length=10, allowed_chars='abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789'):
        "Generates a random password with the given length and given allowed_chars"
        # Note that default value of allowed_chars does not have "I" or letters
        # that look like it -- just to avoid confusion.
        from random import choice
        return ''.join([choice(allowed_chars) for i in range(length)])

# 
# An external user.  ie a user authenticated by an external site.
# This tries to mimic the Django's user but also adds the foreign site
# model and makes the 
#
class ExternalUser(models.Model):
    """
    Users coming in frome external sites (like facebook or myspace) are
    represented by this model.  This should hopefully replace the UserAlias
    model to be a pure extensions of the LocalUser model.  And even more
    eventually this will replace the LocalUser as well (by setting the
    host_site) to null.
    """
    username        = models.CharField(_('username'), max_length=90, unique=True, help_text=_("Required. 90 characters or fewer. "))
    host_site       = models.ForeignKey(HostSite, null = True)
    first_name      = models.CharField(_('first name'), max_length=64, blank=True)
    last_name       = models.CharField(_('last name'), max_length=64, blank=True)
    email           = models.EmailField(_('e-mail address'), blank=True)
    password        = models.CharField(_('password'), default = UNUSABLE_PASSWORD,
                                       max_length=128, help_text=_("Use '[algo]$[salt]$[hexdigest]' or use the <a href=\"password/\">change password form</a>."))
    is_staff        = models.BooleanField(_('staff status'), default=False, help_text=_("Designates whether the user can log into this admin site."))
    is_active       = models.BooleanField(_('active'), default=True, help_text=_("Designates whether this user should be treated as active. Unselect this instead of deleting accounts."))
    is_superuser    = models.BooleanField(_('superuser status'), default=False, help_text=_("Designates that this user has all permissions without explicitly assigning them."))
    last_login      = models.DateTimeField(_('last login'), default=datetime.datetime.now)
    date_joined     = models.DateTimeField(_('date joined'), default=datetime.datetime.now)
    groups          = models.ManyToManyField(Group, verbose_name=_('groups'), blank=True,
                                             help_text=_("In addition to the permissions manually assigned, this user will also get all permissions granted to each group he/she is in."))
    user_permissions = models.ManyToManyField(Permission, verbose_name=_('user permissions'), blank=True)

    objects         = ExternalUserManager()

    class Meta:
        verbose_name = _('external user')
        verbose_name_plural = _('external users')

    def __unicode__(self):
        if self.host_site:
            return self.username + "#" + self.host_site.site_name
        else:
            return self.username + "#"

    def get_absolute_url(self):
        return "/extusers/%d/" % id

    def is_anonymous(self):
        "Always returns False. This is a way of comparing User objects to anonymous users."
        return False

    def is_authenticated(self):
        """
        Always return True. This is a way to tell if the user has been authenticated in templates.
        """
        return True

    def get_full_name(self):
        "Returns the first_name plus the last_name, with a space in between."
        full_name = u'%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def set_password(self, raw_password):
        import random
        algo = 'sha1'
        salt = get_hexdigest(algo, str(random.random()), str(random.random()))[:5]
        hsh = get_hexdigest(algo, salt, raw_password)
        self.password = '%s$%s$%s' % (algo, salt, hsh)

    def check_password(self, raw_password):
        """
        Returns a boolean of whether the raw_password was correct. Handles
        encryption formats behind the scenes.
        """
        # Backwards-compatibility check. Older passwords won't include the
        # algorithm or salt.
        if '$' not in self.password:
            is_correct = (self.password == get_hexdigest('md5', '', raw_password))
            if is_correct:
                # Convert the password to the new, more secure format.
                self.set_password(raw_password)
                self.save()
            return is_correct
        return check_password(raw_password, self.password)

    def set_unusable_password(self):
        # Sets a value that will never be a valid hash
        self.password = UNUSABLE_PASSWORD

    def has_usable_password(self):
        return self.password != UNUSABLE_PASSWORD

    def get_group_permissions(self):
        """
        Returns a list of permission strings that this user has through
        his/her groups. This method queries all available auth backends.
        """
        permissions = set()
        for backend in auth.get_backends():
            if hasattr(backend, "get_group_permissions"):
                permissions.update(backend.get_group_permissions(self))
        return permissions

    def get_all_permissions(self):
        permissions = set()
        for backend in auth.get_backends():
            if hasattr(backend, "get_all_permissions"):
                permissions.update(backend.get_all_permissions(self))
        return permissions

    def has_perm(self, perm):
        """
        Returns True if the user has the specified permission. This method
        queries all available auth backends, but returns immediately if any
        backend returns True. Thus, a user who has permission from a single
        auth backend is assumed to have permission in general.
        """
        # Inactive users have no permissions.
        if not self.is_active:
            return False

        # Superusers have all permissions.
        if self.is_superuser:
            return True

        # Otherwise we need to check the backends.
        for backend in auth.get_backends():
            if hasattr(backend, "has_perm"):
                if backend.has_perm(self, perm):
                    return True
        return False

    def has_perms(self, perm_list):
        """Returns True if the user has each of the specified permissions."""
        for perm in perm_list:
            if not self.has_perm(perm):
                return False
        return True

    def has_module_perms(self, app_label):
        """
        Returns True if the user has any permissions in the given app
        label. Uses pretty much the same logic as has_perm, above.
        """
        if not self.is_active:
            return False

        if self.is_superuser:
            return True

        for backend in auth.get_backends():
            if hasattr(backend, "has_module_perms"):
                if backend.has_module_perms(self, app_label):
                    return True
        return False

    def get_and_delete_messages(self):
        messages = []
        for m in self.message_set.all():
            messages.append(m.message)
            m.delete()
        return messages

    def email_user(self, subject, message, from_email=None):
        "Sends an e-mail to this User."
        from django.core.mail import send_mail
        send_mail(subject, message, from_email, [self.email])

    def get_profile(self):
        """
        Returns site-specific profile for this user. Raises
        SiteProfileNotAvailable if this site does not allow profiles.
        """
        if not hasattr(self, '_profile_cache'):
            from django.conf import settings
            if not getattr(settings, 'AUTH_PROFILE_MODULE', False):
                raise SiteProfileNotAvailable
            try:
                app_label, model_name = settings.AUTH_PROFILE_MODULE.split('.')
                model = models.get_model(app_label, model_name)
                self._profile_cache = model._default_manager.get(user__id__exact=self.id)
                self._profile_cache.user = self
            except (ImportError, ImproperlyConfigured):
                raise SiteProfileNotAvailable
        return self._profile_cache

