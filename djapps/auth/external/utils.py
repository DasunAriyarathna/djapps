
import models as authextmodels
from django.utils.importlib import import_module
import logging ; logger = logging.getLogger(__name__)

def load_authenticator_class(full_auth_class):
    try:
        dot = full_auth_class.rindex('.')
    except ValueError:
        raise exceptions.ImproperlyConfigured, '%s isn\'t a authenticator module' % full_auth_class

    auth_module, auth_classname = full_auth_class[:dot], full_auth_class[dot+1:]

    try:
        auth_mod = __import__(auth_module, {}, {}, [''])
    except ImportError, e:
        raise exceptions.ImproperlyConfigured, 'Error importing site authenticator %s: "%s"' % (auth_module, e)

    try:
        auth_class = getattr(auth_mod, auth_classname)
    except AttributeError:
        raise exceptions.ImproperlyConfigured,                              \
                'Authenticator module "%s" does not define a "%s" class' %  \
                    (auth_module, auth_classname)

    return auth_class

def load_site_authenticators():
    from django.conf import settings
    from django.core import exceptions
    from djapps.dynamo.helpers import get_first_object

    authenticators = []

    for host_site in settings.SITE_AUTHENTICATORS:
        auth_obj        = settings.SITE_AUTHENTICATORS[host_site]
        if 'host_site' not in auth_obj:
            auth_obj['host_site'] = host_site
        auth_module     = import_module(auth_obj['auth_module'])
        auth_class      = getattr(auth_module, auth_obj['auth_class'])

        logger.debug("Auth Class: %s" % str(auth_class))
        logger.debug("Auth Class Params: " % str(auth_obj))

        auth_instance   = auth_class(**auth_obj)
        auth_instance.host_site  = get_first_object(authextmodels.HostSite,
                                                    site_name = host_site.lower())

        if auth_instance.host_site is None:
            assert "Authenticator Host Site is invalid!!!"

        authenticators.append(auth_instance)

    return authenticators
