from djapps.utils import urls         as djurls
import settings, sys

def site_urls(request):
    full_path   = request.get_full_path()
    return {'site_url': settings.SITE_URL,
            'static_host': settings.PROJ_STATIC_HOST,
            'format_param': settings.FORMAT_PARAM,
            'url_path_prefix': djurls.make_url(),
            'login_link': djurls.get_login_url(full_path),
            'logout_link': djurls.get_logout_url(full_path),
            'manage_logins_link': djurls.get_manage_logins_url(full_path),
            'register_link': djurls.get_register_url("/")}

def gae_local_auth(request):
    # drop in replacement for django auth context_processes 
    # for use with gae
    if hasattr(request, 'local_user'):
        print >> sys.stderr, "Here..........................................."
        print >> sys.stderr, "user: ", request.local_user
        user = request.local_user
    else:
        user = None

    # we do not worry about messages or permissions for now
    return  { 'user': user,
              'messages': "Messages not yet implemented",
              'perms': "Permissions not yet implemented" }

def msauth(request):
    return { 'useraliases': request.useraliases }
