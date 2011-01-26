# -*- coding: utf-8 -*-
import os

# Increase this when you update your media on the production site, so users
# don't have to refresh their cache. By setting this your MEDIA_URL
# automatically becomes /media/MEDIA_VERSION/
MEDIA_VERSION = 1

ADMINS              = ( ('Sri Panyam', 'sri.panyam@gmail.com'), )
LOGIN_REDIRECT_URL  = "/"
MANAGERS            = ADMINS
APPEND_SLASH        = True

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'UTC'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/static/"
# STATICFILES_ROOT = ''

# URL that handles the static files served from STATICFILES_ROOT.
# Example: "http://static.lawrence.com/", "http://example.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin media -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# A list of locations of additional static files
# STATICFILES_DIRS = ()

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

ROOT_URLCONF = 'urls'

AUTH_PROFILE_MODULE = "djapps.auth.external.models.localuserprofile"

LOGIN_URL = '/accounts/login/'
LOGOUT_URL = '/accounts/logout/'
LOGIN_REDIRECT_URL = '/'

# 
# These handle authenticators of requests by foreign sites.
#
SITE_AUTHENTICATORS = [
    {
        'auth_module':          'djapps.auth.external.hosts.fb',
        'auth_class':           'AuthFacebook',
        'host_site':            "Facebook",
        'FACEBOOK_API_KEY':     "",
        'FACEBOOK_SECRET_KEY':  "",     # not to be revealed
        'FACEBOOK_APP_NAME':    "",
    },
    {
        'auth_module':  'djapps.auth.external.authenticators',
        'auth_class':   'AuthLocalSite',
        'host_site':    "LocalSite",
    },
]

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request':{
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

# The root folder of THIS project
PROJ_ROOT           = os.path.abspath(os.path.split(__file__)[0])

