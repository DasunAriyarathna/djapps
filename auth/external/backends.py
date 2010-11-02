
try:
    set
except NameError:
    from sets import Set as set # Python 2.3 fallback

class ForeignSiteAuthBackend(ModelBackend):
    """
    Authenticates against a foreign site.
    This is a bit like the MultiSiteAuthentication but only one user can be
    logged in at a time instead of multiple.
    """
    def __init__(self):
        import utils
        self.authenticators = utils.load_site_authenticators()

    def authenticate(self, **credentials):
        """
        Authenticates against a set of credentials.
        """
        for authenticator in self.authenticators:
            if not authenticator.host_site:
                authenticator.host_site  = get_first_object(djmodels.HostSite, site_name = authenticator.host_site_name)
            
            site_user_id = authenticator.authenticate_credentials(**credentials)
            if site_user_id:
                try:
                    return ExternalUser.objects.get(username=site_user_id,
                                                    host_site = authenticator.host_site)
                except ExternalUser.DoesNotExist:
                    pass
        return None

    def get_user(self, user_id):
        try:
            return ExternalUser.objects.get(pk=user_id)
        except ExternalUser.DoesNotExist:
            return None
