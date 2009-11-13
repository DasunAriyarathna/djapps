
from djapps.dynamo.helpers import get_objects, get_first_object, get_or_create_object

def load_site_authenticators():
    from django.conf import settings
    from django.core import exceptions

    authenticators = []

    for auth_params in settings.SITE_AUTHENTICATORS:
        params          = auth_params
        auth_class      = djapps.auth.external.load_authenticator_class(auth_params['class'])
        auth_instance   = auth_class(**params)
        auth_instance.host_site  = get_first_object(djmodels.HostSite, site_name = params['host_site'].lower())

        if auth_instance.host_site is None:
            assert "Authenticator Host Site is invalid!!!"

        authenticators.append(auth_instance)

    return authenticators
