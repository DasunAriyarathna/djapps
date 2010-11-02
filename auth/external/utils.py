
from djapps.dynamo.helpers import get_objects, get_first_object, get_or_create_object
import models as authextmodels

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

    authenticators = []

    for auth_params in settings.SITE_AUTHENTICATORS:
        params          = auth_params
        print "Auth Params: ", auth_params
        auth_class      = load_authenticator_class(auth_params['class'])
        auth_instance   = auth_class(**params)
        auth_instance.host_site  = get_first_object(authextmodels.HostSite, site_name = params['host_site'].lower())

        if auth_instance.host_site is None:
            assert "Authenticator Host Site is invalid!!!"

        authenticators.append(auth_instance)

    return authenticators
