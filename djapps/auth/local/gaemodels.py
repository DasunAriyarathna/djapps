from google.appengine.ext import db
import utils

UNUSABLE_PASSWORD = '!' # This will never be a valid hash

def check_password(raw_password, enc_password):
    """
    Returns a boolean of whether the raw_password was correct. Handles
    encryption formats behind the scenes.
    """
    algo, salt, hsh = enc_password.split('$')
    return hsh == utils.get_hexdigest(algo, salt, raw_password)

# 
# A user in the model - not like Appengine'e User object.
# This is a copy of DJANGO's User model
#
class LocalUser(db.Model):
    """Users within the Django authentication system are represented by this model.
    Username and password are required. Other fields are optional.
    """
    username        = db.StringProperty()
    first_name      = db.StringProperty(default = "")
    last_name       = db.StringProperty(default = "")
    email           = db.EmailProperty(required = False)
    password        = db.StringProperty(default = "")
    is_staff        = db.BooleanProperty(default=False)
    is_active       = db.BooleanProperty(default=True)
    is_superuser    = db.BooleanProperty(default=False)
    last_login      = db.DateTimeProperty(auto_now_add = True)
    date_joined     = db.DateTimeProperty(auto_now_add = True)
    algo            = db.StringProperty(default = "")
    salt            = db.StringProperty(default = "")
    hash            = db.StringProperty(default = "")

    @classmethod
    def create(cls, **kwds):
        uname = ""
        if "username" in kwds:
            uname = kwds["username"]
        Unique.check("username", uname)
        user = LocalUser(username = name)
        user.put()
        return user

    def __unicode__(self):
        return self.username

    def is_anonymous(self):
        "Always returns False. This is a way of comparing User objects to anonymous users."
        return False

    def is_authenticated(self):
        """Always return True. This is a way to tell if the user has been authenticated in templates.
        """
        return True

    def get_full_name(self):
        "Returns the first_name plus the last_name, with a space in between."
        full_name = u'%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def set_password(self, raw_password):
        self.password = utils.salt_password(raw_password)

    def check_password(self, raw_password):
        """
        Returns a boolean of whether the raw_password was correct. Handles
        encryption formats behind the scenes.
        """
        # Backwards-compatibility check. Older passwords won't include the
        # algorithm or salt.
        if '$' not in self.password:
            is_correct = (self.password == utils.get_hexdigest('md5', '', raw_password))
            if is_correct:
                # Convert the password to the new, more secure format.
                self.set_password(raw_password)
                self.put()
            return is_correct
        return check_password(raw_password, self.password)

    def set_unusable_password(self):
        # Sets a value that will never be a valid hash
        self.password = UNUSABLE_PASSWORD

    def has_usable_password(self):
        return self.password != UNUSABLE_PASSWORD

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
                model = db.get_model(app_label, model_name)
                self._profile_cache = model._default_manager.get(user__id__exact=self.id)
            except (ImportError, ImproperlyConfigured):
                raise SiteProfileNotAvailable
        return self._profile_cache

# 
# A table for holding basic registration info about a user,
# the actual user profile will be in a different class
#
class LocalUserRegistration(db.Model):
    user            = db.ReferenceProperty(LocalUser)
    activation_key  = db.StringProperty()
    key_expires     = db.DateTimeProperty()

